from pydantic import BaseModel


class AnalyticsOverviewResponse(BaseModel):
    challenges: dict
    projects: dict
    ecosystem: dict
    impact: dict


class DistrictAnalyticsResponse(BaseModel):
    district: str
    challenge_count: int
    resolved_count: int
    innovation_count: int


class UniversityLeaderboardItem(BaseModel):
    organization_id: int
    organization_name: str
    reputation_points: int
    projects: int
    completed_projects: int
    verified_outcomes: int


class IndustryLeaderboardItem(BaseModel):
    organization_id: int
    organization_name: str
    reputation_points: int
    projects: int
    completed_projects: int
    funding_contribution: float


class ReputationLeaderboardItem(BaseModel):
    entity_type: str
    organization_id: int | None
    organization_name: str | None
    total_points: int
    contribution_count: int