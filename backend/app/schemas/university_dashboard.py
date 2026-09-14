from pydantic import BaseModel


class UniversityInvitationStats(BaseModel):
    total: int
    interested: int
    declined: int
    proposal_submitted: int


class UniversityProposalStats(BaseModel):
    total: int
    submitted: int
    under_evaluation: int
    shortlisted: int
    rejected: int


class UniversityCollaborationStats(BaseModel):
    total: int
    submitted: int
    accepted: int


class UniversityProjectStats(BaseModel):
    total: int
    planning: int
    active: int
    on_hold: int
    completed: int


class UniversityMilestoneStats(BaseModel):
    total: int
    completed: int
    delayed: int


class UniversityDeliverableStats(BaseModel):
    total: int
    approved: int
    rejected: int


class UniversityImpactStats(BaseModel):
    verified_outcomes: int
    beneficiaries: int
    average_project_progress: float


class UniversityReputationStats(BaseModel):
    total_points: int
    contribution_count: int


class UniversityDashboardResponse(BaseModel):
    organization_id: int
    invitations: UniversityInvitationStats
    proposals: UniversityProposalStats
    industry_collaboration: UniversityCollaborationStats
    projects: UniversityProjectStats
    milestones: UniversityMilestoneStats
    deliverables: UniversityDeliverableStats
    impact: UniversityImpactStats
    reputation: UniversityReputationStats