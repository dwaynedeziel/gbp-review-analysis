from models.business import ReviewDistribution, GBPProfile, Business
from models.analysis import AnalysisResult, ProfileAnalysis, WhatIfResult, PricingInfo
from services.pdf_generator import generate_pdf
from services.business_type import get_terminology


def _make_test_result():
    """Create a minimal AnalysisResult for PDF generation testing."""
    dist1 = ReviewDistribution(five_star=400, four_star=19, three_star=5, two_star=4, one_star=21)
    dist2 = ReviewDistribution(five_star=34, four_star=3, three_star=0, two_star=0, one_star=0)

    p1 = GBPProfile(name="Downtown Location", url="https://maps.app.goo.gl/example",
                     total_reviews=449, average_rating=4.7, distribution=dist1)
    p2 = GBPProfile(name="Westside Location", url="",
                     total_reviews=37, average_rating=4.92, distribution=dist2)

    pa1 = ProfileAnalysis(
        profile=p1,
        what_if=WhatIfResult(removed_count=25, remove_breakdown="21 one-star + 4 two-star reviews",
                             new_total=424, new_average=4.93, rating_lift=0.23),
        recommendation="remove",
        recommendation_detail="Remove all 1-star & 2-star reviews",
    )
    pa2 = ProfileAnalysis(
        profile=p2,
        what_if=WhatIfResult(removed_count=0, remove_breakdown="No reviews to remove",
                             new_total=37, new_average=4.92, rating_lift=0.0),
        recommendation="none",
        recommendation_detail="No action needed \u2014 Excellent performance",
    )

    business = Business(name="Smith Plumbing & HVAC", business_type="home_services",
                        profiles=[p1, p2])

    terminology = get_terminology("home_services")

    return AnalysisResult(
        business=business,
        profile_analyses=[pa1, pa2],
        totals={
            "total_reviews": 486,
            "total_to_remove": 25,
            "profiles_needing_action": 1,
            "total_profiles": 2,
            "max_lift": 0.23,
        },
        terminology=terminology,
        pricing=PricingInfo(per_review=795, original_per_review=895,
                            total_reviews=25, discount_pct=10),
        executive_summary=(
            "Smith Plumbing & HVAC maintains 2 active Google Business Profiles "
            "with a combined 486 reviews."
        ),
        executive_summary_2=(
            "By removing just 25 low-star reviews, the projected rating lift "
            "is up to +0.23 stars."
        ),
        next_steps_subtitle=(
            "You've already done the hard work \u2014 earning 486 reviews. "
            "This is about removing the 25 that are holding you back."
        ),
        next_steps=[
            {"title": "Choose your reviews.", "description": "Review your Google profile."},
            {"title": "Email your list to WISE.", "description": "Send us the reviews."},
            {"title": "Pay only for results.", "description": "You are invoiced only when removed."},
            {"title": "Keep the momentum going.", "description": "Ask your happiest customers to leave a review."},
        ],
    )


def test_generate_pdf_returns_bytes():
    result = _make_test_result()
    pdf_bytes = generate_pdf(result)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    # PDF files start with %PDF
    assert pdf_bytes[:5] == b"%PDF-"


def test_generate_pdf_single_profile():
    result = _make_test_result()
    # Reduce to single profile
    result.profile_analyses = result.profile_analyses[:1]
    result.business.profiles = result.business.profiles[:1]
    result.totals["total_profiles"] = 1

    pdf_bytes = generate_pdf(result)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:5] == b"%PDF-"


def test_generate_pdf_no_removals():
    result = _make_test_result()
    # Set all profiles to no action
    for pa in result.profile_analyses:
        pa.what_if = WhatIfResult(removed_count=0, remove_breakdown="No reviews to remove",
                                   new_total=pa.profile.total_reviews,
                                   new_average=pa.profile.average_rating, rating_lift=0.0)
        pa.recommendation = "none"
        pa.recommendation_detail = "No action needed"
    result.totals["total_to_remove"] = 0
    result.totals["max_lift"] = 0.0
    result.pricing.total_reviews = 0

    pdf_bytes = generate_pdf(result)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes[:5] == b"%PDF-"
