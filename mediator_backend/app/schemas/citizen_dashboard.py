from datetime import datetime

from pydantic import BaseModel


class CitizenChallengeStats(BaseModel):
    total: int
    submitted: int
    under_review: int
    routed: int
    in_progress: int
    resolved: int
    rejected: int
    closed: int
    innovation_required: int


class CitizenReputationStats(BaseModel):
    total_points: int
    contribution_count: int


class RecentChallenge(BaseModel):
    id: int
    title: str
    status: str
    category: str
    urgency: str
    innovation_required: bool
    district: str | None = None
    state: str | None = None
    current_authority_id: int | None = None
    created_at: datetime
    updated_at: datetime


class CitizenDashboardResponse(BaseModel):
    user_id: int
    challenge_stats: CitizenChallengeStats
    reputation: CitizenReputationStats
    recent_challenges: list[RecentChallenge]