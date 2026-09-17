from pydantic import BaseModel


class ChallengeStats(BaseModel):
    total: int
    submitted: int
    under_review: int
    routed: int
    in_progress: int
    resolved: int
    rejected: int
    closed: int
    innovation_required: int
    high_priority: int


class ProjectStats(BaseModel):
    total: int
    planning: int
    active: int
    on_hold: int
    completed: int
    cancelled: int


class ProjectHealthStats(BaseModel):
    on_track: int
    at_risk: int
    delayed: int
    critical: int


class EcosystemStats(BaseModel):
    universities: int
    industries: int


class FundingStats(BaseModel):
    allocated: float
    disbursed: float
    utilized: float
    refunded: float
    remaining: float


class ImpactStats(BaseModel):
    verified_outcomes: int
    total_beneficiaries: int
    average_project_progress: float


class DistrictChallengeStats(BaseModel):
    district: str
    challenge_count: int


class DistributionStats(BaseModel):
    challenge_categories: dict[str, int]
    challenge_districts: list[DistrictChallengeStats]


class GovernmentDashboardResponse(BaseModel):
    challenge_stats: ChallengeStats
    project_stats: ProjectStats
    project_health: ProjectHealthStats
    ecosystem: EcosystemStats
    funding: FundingStats
    impact: ImpactStats
    distribution: DistributionStats