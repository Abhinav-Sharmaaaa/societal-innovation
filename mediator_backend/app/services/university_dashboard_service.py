from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.industry_collaboration import (
    IndustryCollaborationProposal,
    IndustryCollaborationStatus,
)
from app.models.project import (
    Project,
    ProjectStatus,
)
from app.models.project_milestone import (
    ProjectMilestone,
    ProjectMilestoneStatus,
)
from app.models.project_deliverable import (
    ProjectDeliverable,
    ProjectDeliverableStatus,
)
from app.models.project_outcome import (
    ProjectOutcome,
    ProjectOutcomeStatus,
)
from app.models.reputation_score import ReputationScore
from app.models.rfp_invitation import (
    RFPInvitation,
    RFPInvitationStatus,
)
from app.models.university_proposal import (
    UniversityProposal,
    UniversityProposalStatus,
)
from app.models.user import User


def get_university_dashboard(
    db: Session,
    current_user: User,
) -> dict:

    organization_id = current_user.organization_id

    if organization_id is None:
        raise ValueError(
            "University user is not associated with an organization."
        )

    # =========================================================
    # INVITATIONS
    # =========================================================

    invitation_total = (
        db.query(func.count(RFPInvitation.id))
        .filter(
            RFPInvitation.university_id
            == organization_id
        )
        .scalar()
        or 0
    )

    invitation_interested = (
        db.query(func.count(RFPInvitation.id))
        .filter(
            RFPInvitation.university_id
            == organization_id,
            RFPInvitation.status
            == RFPInvitationStatus.INTERESTED,
        )
        .scalar()
        or 0
    )

    invitation_declined = (
        db.query(func.count(RFPInvitation.id))
        .filter(
            RFPInvitation.university_id
            == organization_id,
            RFPInvitation.status
            == RFPInvitationStatus.DECLINED,
        )
        .scalar()
        or 0
    )

    invitation_proposals = (
        db.query(func.count(RFPInvitation.id))
        .filter(
            RFPInvitation.university_id
            == organization_id,
            RFPInvitation.status
            == RFPInvitationStatus.PROPOSAL_SUBMITTED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # UNIVERSITY PROPOSALS
    # =========================================================

    proposal_total = (
        db.query(func.count(UniversityProposal.id))
        .filter(
            UniversityProposal.university_id
            == organization_id
        )
        .scalar()
        or 0
    )

    proposal_submitted = (
        db.query(func.count(UniversityProposal.id))
        .filter(
            UniversityProposal.university_id
            == organization_id,
            UniversityProposal.status
            == UniversityProposalStatus.SUBMITTED,
        )
        .scalar()
        or 0
    )

    proposal_under_evaluation = (
        db.query(func.count(UniversityProposal.id))
        .filter(
            UniversityProposal.university_id
            == organization_id,
            UniversityProposal.status
            == UniversityProposalStatus.UNDER_EVALUATION,
        )
        .scalar()
        or 0
    )

    proposal_shortlisted = (
        db.query(func.count(UniversityProposal.id))
        .filter(
            UniversityProposal.university_id
            == organization_id,
            UniversityProposal.status
            == UniversityProposalStatus.SHORTLISTED,
        )
        .scalar()
        or 0
    )

    proposal_rejected = (
        db.query(func.count(UniversityProposal.id))
        .filter(
            UniversityProposal.university_id
            == organization_id,
            UniversityProposal.status
            == UniversityProposalStatus.REJECTED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # INDUSTRY COLLABORATION
    # =========================================================

    collaboration_total = (
        db.query(func.count(IndustryCollaborationProposal.id))
        .join(
            UniversityProposal,
            IndustryCollaborationProposal.university_proposal_id
            == UniversityProposal.id,
        )
        .filter(
            UniversityProposal.university_id
            == organization_id
        )
        .scalar()
        or 0
    )

    collaboration_submitted = (
        db.query(func.count(IndustryCollaborationProposal.id))
        .join(
            UniversityProposal,
            IndustryCollaborationProposal.university_proposal_id
            == UniversityProposal.id,
        )
        .filter(
            UniversityProposal.university_id
            == organization_id,
            IndustryCollaborationProposal.status
            == IndustryCollaborationStatus.SUBMITTED,
        )
        .scalar()
        or 0
    )

    collaboration_accepted = (
        db.query(func.count(IndustryCollaborationProposal.id))
        .join(
            UniversityProposal,
            IndustryCollaborationProposal.university_proposal_id
            == UniversityProposal.id,
        )
        .filter(
            UniversityProposal.university_id
            == organization_id,
            IndustryCollaborationProposal.status
            == IndustryCollaborationStatus.ACCEPTED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # PROJECTS
    # =========================================================

    project_total = (
        db.query(func.count(Project.id))
        .filter(
            Project.university_id
            == organization_id
        )
        .scalar()
        or 0
    )

    project_planning = (
        db.query(func.count(Project.id))
        .filter(
            Project.university_id
            == organization_id,
            Project.status
            == ProjectStatus.PLANNING,
        )
        .scalar()
        or 0
    )

    project_active = (
        db.query(func.count(Project.id))
        .filter(
            Project.university_id
            == organization_id,
            Project.status
            == ProjectStatus.ACTIVE,
        )
        .scalar()
        or 0
    )

    project_completed = (
        db.query(func.count(Project.id))
        .filter(
            Project.university_id
            == organization_id,
            Project.status
            == ProjectStatus.COMPLETED,
        )
        .scalar()
        or 0
    )

    project_on_hold = (
        db.query(func.count(Project.id))
        .filter(
            Project.university_id
            == organization_id,
            Project.status
            == ProjectStatus.ON_HOLD,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # MILESTONES
    # =========================================================

    milestone_total = (
        db.query(func.count(ProjectMilestone.id))
        .join(
            Project,
            ProjectMilestone.project_id
            == Project.id,
        )
        .filter(
            Project.university_id
            == organization_id
        )
        .scalar()
        or 0
    )

    milestone_completed = (
        db.query(func.count(ProjectMilestone.id))
        .join(
            Project,
            ProjectMilestone.project_id
            == Project.id,
        )
        .filter(
            Project.university_id
            == organization_id,
            ProjectMilestone.status
            == ProjectMilestoneStatus.COMPLETED,
        )
        .scalar()
        or 0
    )

    milestone_delayed = (
        db.query(func.count(ProjectMilestone.id))
        .join(
            Project,
            ProjectMilestone.project_id
            == Project.id,
        )
        .filter(
            Project.university_id
            == organization_id,
            ProjectMilestone.status
            == ProjectMilestoneStatus.DELAYED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # DELIVERABLES
    # =========================================================

    deliverable_total = (
        db.query(func.count(ProjectDeliverable.id))
        .join(
            Project,
            ProjectDeliverable.project_id
            == Project.id,
        )
        .filter(
            Project.university_id
            == organization_id
        )
        .scalar()
        or 0
    )

    deliverable_approved = (
        db.query(func.count(ProjectDeliverable.id))
        .join(
            Project,
            ProjectDeliverable.project_id
            == Project.id,
        )
        .filter(
            Project.university_id
            == organization_id,
            ProjectDeliverable.status
            == ProjectDeliverableStatus.APPROVED,
        )
        .scalar()
        or 0
    )

    deliverable_rejected = (
        db.query(func.count(ProjectDeliverable.id))
        .join(
            Project,
            ProjectDeliverable.project_id
            == Project.id,
        )
        .filter(
            Project.university_id
            == organization_id,
            ProjectDeliverable.status
            == ProjectDeliverableStatus.REJECTED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # PROJECT PROGRESS
    # =========================================================

    average_project_progress = (
        db.query(
            func.coalesce(
                func.avg(
                    Project.progress_percentage
                ),
                0,
            )
        )
        .filter(
            Project.university_id
            == organization_id
        )
        .scalar()
        or 0
    )

    # =========================================================
    # VERIFIED IMPACT
    # =========================================================

    verified_outcomes = (
        db.query(func.count(ProjectOutcome.id))
        .join(
            Project,
            ProjectOutcome.project_id
            == Project.id,
        )
        .filter(
            Project.university_id
            == organization_id,
            ProjectOutcome.status
            == ProjectOutcomeStatus.VERIFIED,
        )
        .scalar()
        or 0
    )

    beneficiaries = (
        db.query(
            func.coalesce(
                func.sum(
                    ProjectOutcome.beneficiary_count
                ),
                0,
            )
        )
        .join(
            Project,
            ProjectOutcome.project_id
            == Project.id,
        )
        .filter(
            Project.university_id
            == organization_id,
            ProjectOutcome.status
            == ProjectOutcomeStatus.VERIFIED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # REPUTATION
    # =========================================================

    reputation = (
        db.query(ReputationScore)
        .filter(
            ReputationScore.organization_id
            == organization_id,
        )
        .first()
    )

    reputation_points = (
        reputation.total_points
        if reputation
        else 0
    )

    reputation_contributions = (
        reputation.contribution_count
        if reputation
        else 0
    )

    # =========================================================
    # RESPONSE
    # =========================================================

    return {
        "organization_id": organization_id,

        "invitations": {
            "total": invitation_total,
            "interested": invitation_interested,
            "declined": invitation_declined,
            "proposal_submitted": invitation_proposals,
        },

        "proposals": {
            "total": proposal_total,
            "submitted": proposal_submitted,
            "under_evaluation": proposal_under_evaluation,
            "shortlisted": proposal_shortlisted,
            "rejected": proposal_rejected,
        },

        "industry_collaboration": {
            "total": collaboration_total,
            "submitted": collaboration_submitted,
            "accepted": collaboration_accepted,
        },

        "projects": {
            "total": project_total,
            "planning": project_planning,
            "active": project_active,
            "on_hold": project_on_hold,
            "completed": project_completed,
        },

        "milestones": {
            "total": milestone_total,
            "completed": milestone_completed,
            "delayed": milestone_delayed,
        },

        "deliverables": {
            "total": deliverable_total,
            "approved": deliverable_approved,
            "rejected": deliverable_rejected,
        },

        "impact": {
            "verified_outcomes": verified_outcomes,
            "beneficiaries": int(beneficiaries),
            "average_project_progress": round(
                float(average_project_progress),
                2,
            ),
        },

        "reputation": {
            "total_points": reputation_points,
            "contribution_count": reputation_contributions,
        },
    }