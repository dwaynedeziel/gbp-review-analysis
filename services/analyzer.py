import math
from models.business import ReviewDistribution, GBPProfile, Business
from models.analysis import WhatIfResult, ProfileAnalysis, PricingInfo, AnalysisResult
from services.business_type import get_terminology


def estimate_distribution(total: int, average: float) -> ReviewDistribution:
    """Estimate star distribution from total count and average rating.

    Uses a model where reviews cluster at 5-star and 1-star with fewer in
    the middle, calibrated to match the given average.
    """
    if total == 0:
        return ReviewDistribution()

    avg = max(1.0, min(5.0, average))

    # Weight toward 5-star proportional to how high the average is
    # A 4.5 average means ~80% are 5-star, a 2.0 average means ~10%
    five_pct = max(0, min(1, (avg - 1) / 4)) ** 1.3
    one_pct = max(0, min(1, (5 - avg) / 4)) ** 2.0

    # Distribute remaining across 2, 3, 4 stars
    remaining = 1 - five_pct - one_pct
    if remaining < 0:
        # Normalize
        s = five_pct + one_pct
        five_pct /= s
        one_pct /= s
        remaining = 0

    four_pct = remaining * 0.5
    three_pct = remaining * 0.25
    two_pct = remaining * 0.25

    # Convert to counts
    five = round(total * five_pct)
    one = round(total * one_pct)
    four = round(total * four_pct)
    three = round(total * three_pct)
    two = total - five - four - three - one
    if two < 0:
        two = 0
        # Adjust five to maintain total
        five = total - four - three - two - one

    dist = ReviewDistribution(
        five_star=max(0, five),
        four_star=max(0, four),
        three_star=max(0, three),
        two_star=max(0, two),
        one_star=max(0, one),
    )

    # Fix total if rounding errors occurred
    diff = total - dist.total
    if diff > 0:
        dist.five_star += diff
    elif diff < 0:
        dist.five_star = max(0, dist.five_star + diff)

    return dist


def compute_what_if(distribution: ReviewDistribution) -> WhatIfResult:
    """Calculate projected rating if all 1-star and 2-star reviews are removed."""
    removed_1 = distribution.one_star
    removed_2 = distribution.two_star
    removed_count = removed_1 + removed_2

    if removed_count == 0:
        return WhatIfResult(
            removed_count=0,
            remove_breakdown="No reviews to remove",
            new_total=distribution.total,
            new_average=distribution.average_rating,
            rating_lift=0.0,
        )

    new_total = distribution.total - removed_count
    if new_total == 0:
        return WhatIfResult(
            removed_count=removed_count,
            remove_breakdown=_breakdown_text(removed_1, removed_2),
            new_total=0,
            new_average=0.0,
            rating_lift=0.0,
        )

    new_weighted = (
        5 * distribution.five_star
        + 4 * distribution.four_star
        + 3 * distribution.three_star
    )
    new_average = round(new_weighted / new_total, 2)
    rating_lift = round(new_average - distribution.average_rating, 2)

    return WhatIfResult(
        removed_count=removed_count,
        remove_breakdown=_breakdown_text(removed_1, removed_2),
        new_total=new_total,
        new_average=new_average,
        rating_lift=rating_lift,
    )


def _breakdown_text(one_star: int, two_star: int) -> str:
    parts = []
    if one_star > 0:
        parts.append(f"{one_star} one-star")
    if two_star > 0:
        parts.append(f"{two_star} two-star")
    return " + ".join(parts) + " reviews"


def analyze_profile(profile: GBPProfile) -> ProfileAnalysis:
    """Analyze a single GBP profile."""
    what_if = compute_what_if(profile.distribution)

    if what_if.removed_count == 0:
        recommendation = "none"
        recommendation_detail = "No action needed \u2014 Excellent performance"
    else:
        recommendation = "remove"
        recommendation_detail = f"Remove all 1-star & 2-star reviews"

    return ProfileAnalysis(
        profile=profile,
        what_if=what_if,
        recommendation=recommendation,
        recommendation_detail=recommendation_detail,
    )


def analyze_business(business: Business) -> AnalysisResult:
    """Run full analysis on a business with all its profiles."""
    terminology = get_terminology(business.business_type)
    profile_analyses = [analyze_profile(p) for p in business.profiles]

    total_reviews = sum(p.distribution.total for p in business.profiles)
    total_to_remove = sum(pa.what_if.removed_count for pa in profile_analyses)
    profiles_needing_action = sum(1 for pa in profile_analyses if pa.recommendation == "remove")
    max_lift = max((pa.what_if.rating_lift for pa in profile_analyses), default=0.0)

    totals = {
        "total_reviews": total_reviews,
        "total_to_remove": total_to_remove,
        "profiles_needing_action": profiles_needing_action,
        "total_profiles": len(business.profiles),
        "max_lift": max_lift,
    }

    pricing = PricingInfo(total_reviews=total_to_remove)

    # Generate executive summary
    customers = terminology["customers"]
    exec_summary = _generate_executive_summary(
        business, totals, profile_analyses, terminology
    )
    exec_summary_2 = _generate_executive_summary_2(totals, terminology)

    # Next steps
    next_steps_subtitle = (
        f"You've already done the hard work \u2014 earning {total_reviews} reviews. "
        f"This is about removing the {total_to_remove} that are holding you back."
    )
    if total_to_remove == 0:
        next_steps_subtitle = (
            f"You've already done the hard work \u2014 earning {total_reviews} reviews. "
            f"Your profiles are performing excellently. Here's how to maintain your edge."
        )

    next_steps = [
        {
            "title": "Choose your reviews.",
            "description": (
                "Review your Google profile and decide which reviews you want removed. "
                "Focus on the 1-star and 2-star reviews identified in this report."
            ),
        },
        {
            "title": "Email your list to WISE.",
            "description": (
                "Send us the reviews you've selected \u2014 include the reviewer name "
                "and star rating for each. We'll take it from there."
            ),
        },
        {
            "title": "Pay only for results.",
            "description": (
                "You are invoiced only when a review is successfully removed. "
                "No upfront costs, no risk \u2014 you pay as each one comes down."
            ),
        },
        {
            "title": "Keep the momentum going.",
            "description": (
                f"Ask your {terminology['review_ask_audience']} to leave a review. "
                f"Fresh positive reviews accelerate your rating climb and keep your "
                f"profile active in Google's algorithm."
            ),
        },
    ]

    # Check for estimated data
    data_is_estimated = any(
        getattr(p, '_estimated', False) for p in business.profiles
    )

    return AnalysisResult(
        business=business,
        profile_analyses=profile_analyses,
        totals=totals,
        terminology=terminology,
        pricing=pricing,
        executive_summary=exec_summary,
        executive_summary_2=exec_summary_2,
        next_steps_subtitle=next_steps_subtitle,
        next_steps=next_steps,
        data_is_estimated=data_is_estimated,
    )


def _generate_executive_summary(
    business: Business, totals: dict, analyses: list, terminology: dict
) -> str:
    n_profiles = totals["total_profiles"]
    total_reviews = totals["total_reviews"]
    total_to_remove = totals["total_to_remove"]
    customers = terminology["customers"]

    profile_word = "profile" if n_profiles == 1 else "profiles"

    if total_to_remove == 0:
        return (
            f"{business.name} maintains {n_profiles} active Google Business "
            f"{profile_word} with a combined {total_reviews} reviews. "
            f"All profiles are performing excellently with no low-star reviews "
            f"requiring attention. The focus should be on maintaining this strong "
            f"position and continuing to generate fresh reviews from {customers}."
        )

    needing = totals["profiles_needing_action"]
    scope = "the profile" if n_profiles == 1 else f"{needing} of {n_profiles} profiles"
    return (
        f"{business.name} maintains {n_profiles} active Google Business "
        f"{profile_word} with a combined {total_reviews} reviews. "
        f"While the overall reputation is strong, a small number of low-star "
        f"reviews are suppressing ratings across {scope}."
    )


def _generate_executive_summary_2(totals: dict, terminology: dict) -> str:
    total_to_remove = totals["total_to_remove"]
    max_lift = totals["max_lift"]
    prospect = terminology["prospect"]

    if total_to_remove == 0:
        return ""

    return (
        f"By removing just {total_to_remove} low-star reviews, the projected "
        f"rating lift is up to +{max_lift:.2f} stars \u2014 a meaningful improvement "
        f"that directly impacts click-through rates, inbound calls, and how "
        f"every {prospect} perceives the business in search results."
    )
