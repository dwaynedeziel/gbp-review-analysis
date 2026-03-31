from dataclasses import dataclass, field


@dataclass
class WhatIfResult:
    removed_count: int = 0
    remove_breakdown: str = ""
    new_total: int = 0
    new_average: float = 0.0
    rating_lift: float = 0.0


@dataclass
class ProfileAnalysis:
    profile: object = None
    what_if: WhatIfResult = field(default_factory=WhatIfResult)
    recommendation: str = "none"  # "remove" or "none"
    recommendation_detail: str = ""


@dataclass
class PricingInfo:
    per_review: int = 795
    original_per_review: int = 895
    total_reviews: int = 0
    discount_pct: int = 10

    @property
    def standard_total(self) -> int:
        return self.per_review * self.total_reviews

    @property
    def discounted_total(self) -> int:
        return round(self.standard_total * (1 - self.discount_pct / 100))

    @property
    def savings(self) -> int:
        return self.standard_total - self.discounted_total


@dataclass
class AnalysisResult:
    business: object = None
    profile_analyses: list = field(default_factory=list)
    totals: dict = field(default_factory=dict)
    terminology: dict = field(default_factory=dict)
    pricing: PricingInfo = field(default_factory=PricingInfo)
    executive_summary: str = ""
    executive_summary_2: str = ""
    next_steps_subtitle: str = ""
    next_steps: list = field(default_factory=list)
    data_is_estimated: bool = False
