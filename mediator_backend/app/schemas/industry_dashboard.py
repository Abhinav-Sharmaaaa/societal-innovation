from pydantic import BaseModel


class IndustryCollaborationStats(BaseModel):
    total: int
    draft: int
    submitted: int
    under_review: int
    accepted: int
    rejected: int


class IndustryProjectStats(BaseModel):
    total: int
    planning: int
    active: int
    on_hold: int
    completed: int


class IndustryMilestoneStats(BaseModel):
    total: int
    completed: int
    delayed: int
    blocked: int


class IndustryDeliverableStats(BaseModel):
    total: int
    approved: int
    rejected: int


class IndustryFundingStats(BaseModel):
    allocated: float
    disbursed: float
    utilized: float
    refunded: float


class IndustryImpactStats(BaseModel):
    verified_outcomes: int
    beneficiaries: int
    average_project_progress: float


class IndustryReputationStats(BaseModel):
    total_points: int
    contribution_count: int


class IndustryDashboardResponse(BaseModel):
    organization_id: int
    collaborations: IndustryCollaborationStats
    projects: IndustryProjectStats
    milestones: IndustryMilestoneStats
    deliverables: IndustryDeliverableStats
    funding: IndustryFundingStats
    impact: IndustryImpactStats
    reputation: IndustryReputationStats