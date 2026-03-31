from models.business import ReviewDistribution, GBPProfile, Business
from models.analysis import PricingInfo
from services.analyzer import (
    compute_what_if,
    analyze_profile,
    analyze_business,
    estimate_distribution,
)


def test_compute_what_if_basic():
    dist = ReviewDistribution(five_star=400, four_star=19, three_star=5, two_star=4, one_star=21)
    result = compute_what_if(dist)
    assert result.removed_count == 25
    assert result.new_total == 424
    assert result.new_average > dist.average_rating
    assert result.rating_lift > 0


def test_compute_what_if_no_negatives():
    dist = ReviewDistribution(five_star=50, four_star=5, three_star=0, two_star=0, one_star=0)
    result = compute_what_if(dist)
    assert result.removed_count == 0
    assert result.rating_lift == 0.0
    assert result.new_total == 55


def test_compute_what_if_all_one_star():
    dist = ReviewDistribution(five_star=0, four_star=0, three_star=0, two_star=0, one_star=10)
    result = compute_what_if(dist)
    assert result.removed_count == 10
    assert result.new_total == 0


def test_analyze_profile_remove():
    dist = ReviewDistribution(five_star=100, four_star=10, three_star=3, two_star=2, one_star=5)
    profile = GBPProfile(name="Test", distribution=dist, total_reviews=120, average_rating=dist.average_rating)
    pa = analyze_profile(profile)
    assert pa.recommendation == "remove"
    assert pa.what_if.removed_count == 7


def test_analyze_profile_excellent():
    dist = ReviewDistribution(five_star=50, four_star=3, three_star=0, two_star=0, one_star=0)
    profile = GBPProfile(name="Test", distribution=dist, total_reviews=53, average_rating=dist.average_rating)
    pa = analyze_profile(profile)
    assert pa.recommendation == "none"


def test_estimate_distribution():
    dist = estimate_distribution(100, 4.5)
    assert dist.total == 100
    assert dist.five_star > dist.one_star
    # Average should be roughly close to 4.5
    assert abs(dist.average_rating - 4.5) < 0.5


def test_estimate_distribution_zero():
    dist = estimate_distribution(0, 0.0)
    assert dist.total == 0


def test_analyze_business():
    profiles = [
        GBPProfile(
            name="Location 1",
            distribution=ReviewDistribution(five_star=400, four_star=19, three_star=5, two_star=4, one_star=21),
            total_reviews=449,
            average_rating=4.7,
        ),
        GBPProfile(
            name="Location 2",
            distribution=ReviewDistribution(five_star=34, four_star=3, three_star=0, two_star=0, one_star=0),
            total_reviews=37,
            average_rating=4.92,
        ),
    ]
    business = Business(name="Test Biz", business_type="home_services", profiles=profiles)
    result = analyze_business(business)

    assert result.totals["total_reviews"] == 486
    assert result.totals["total_to_remove"] == 25
    assert result.totals["profiles_needing_action"] == 1
    assert result.terminology["customers"] == "customers"
    assert result.terminology["prospect"] == "homeowner"
    assert "Test Biz" in result.executive_summary


def test_pricing_info():
    p = PricingInfo(per_review=795, original_per_review=895, total_reviews=25, discount_pct=10)
    assert p.standard_total == 19875
    assert p.discounted_total == 17888  # 19875 * 0.9 = 17887.5, rounded
    assert p.savings == 19875 - 17888
