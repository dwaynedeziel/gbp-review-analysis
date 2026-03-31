from dataclasses import dataclass, field


@dataclass
class ReviewDistribution:
    five_star: int = 0
    four_star: int = 0
    three_star: int = 0
    two_star: int = 0
    one_star: int = 0

    @property
    def total(self) -> int:
        return self.five_star + self.four_star + self.three_star + self.two_star + self.one_star

    @property
    def average_rating(self) -> float:
        if self.total == 0:
            return 0.0
        weighted = (
            5 * self.five_star
            + 4 * self.four_star
            + 3 * self.three_star
            + 2 * self.two_star
            + 1 * self.one_star
        )
        return round(weighted / self.total, 2)

    def as_dict(self) -> dict:
        return {
            "5": self.five_star,
            "4": self.four_star,
            "3": self.three_star,
            "2": self.two_star,
            "1": self.one_star,
        }

    def percentages(self) -> dict:
        if self.total == 0:
            return {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        return {k: round(v / self.total * 100, 1) for k, v in self.as_dict().items()}


@dataclass
class GBPProfile:
    name: str
    url: str = ""
    total_reviews: int = 0
    average_rating: float = 0.0
    distribution: ReviewDistribution = field(default_factory=ReviewDistribution)


@dataclass
class Business:
    name: str
    business_type: str = "default"
    profiles: list = field(default_factory=list)
