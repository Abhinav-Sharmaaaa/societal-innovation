import {
  ArrowLeft,
  CheckCircle2,
  ChevronRight,
  Clock3,
  FileText,
  Loader2,
  Sparkles,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  declineInvitation,
  expressInterest,
  getMyRFPInvitations,
  type RFPInvitation,
} from "../../services/rfpInvitationService";

import "./UniversityInvitationsPage.css";

export default function UniversityInvitationsPage() {
  const navigate = useNavigate();

  const [invitations, setInvitations] = useState<
    RFPInvitation[]
  >([]);

  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const loadInvitations = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getMyRFPInvitations();

      setInvitations(data);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Failed to load RFP invitations."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadInvitations();
  }, []);

  const handleInterest = async (
    invitation: RFPInvitation
  ) => {
    try {
      setActionId(invitation.id);
      setError("");

      const updated = await expressInterest(
        invitation.id
      );

      setInvitations((current) =>
        current.map((item) =>
          item.id === updated.id ? updated : item
        )
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Failed to express interest."
      );
    } finally {
      setActionId(null);
    }
  };

  const handleDecline = async (
    invitation: RFPInvitation
  ) => {
    const reason = window.prompt(
      "Why are you declining this invitation? (Optional)"
    );

    if (reason === null) {
      return;
    }

    try {
      setActionId(invitation.id);
      setError("");

      const updated = await declineInvitation(
        invitation.id,
        reason.trim() || undefined
      );

      setInvitations((current) =>
        current.map((item) =>
          item.id === updated.id ? updated : item
        )
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Failed to decline invitation."
      );
    } finally {
      setActionId(null);
    }
  };

  const getStatusClass = (
    status: RFPInvitation["status"]
  ) => {
    switch (status) {
      case "INTERESTED":
        return "invitation-status interested";

      case "PROPOSAL_SUBMITTED":
        return "invitation-status proposal";

      case "DECLINED":
        return "invitation-status declined";

      case "EXPIRED":
        return "invitation-status expired";

      default:
        return "invitation-status invited";
    }
  };

  const getStatusLabel = (
    status: RFPInvitation["status"]
  ) => {
    return status.replaceAll("_", " ");
  };

  return (
    <div className="university-invitations-page">
      <div className="invitations-header">
        <button
          type="button"
          className="invitations-back"
          onClick={() => navigate("/university/dashboard")}
        >
          <ArrowLeft size={18} />
          Dashboard
        </button>

        <div>
          <p className="invitations-eyebrow">
            UNIVERSITY INNOVATION PORTAL
          </p>

          <h1>RFP Invitations</h1>

          <p>
            Review government innovation challenges matched to
            your university.
          </p>
        </div>
      </div>

      {error && (
        <div className="invitations-alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="invitations-state">
          <Loader2
            size={28}
            className="invitations-spinner"
          />
          <p>Loading invitations...</p>
        </div>
      ) : invitations.length === 0 ? (
        <div className="invitations-state">
          <FileText size={42} />

          <h2>No RFP invitations yet</h2>

          <p>
            Your university has not received any RFP
            invitations.
          </p>
        </div>
      ) : (
        <div className="invitations-list">
          {invitations.map((invitation) => (
            <article
              key={invitation.id}
              className="invitation-card"
            >
              <div className="invitation-card-header">
                <div className="invitation-title-area">
                  <div className="invitation-icon">
                    <FileText size={21} />
                  </div>

                  <div>
                    <span className="invitation-label">
                      RFP INVITATION
                    </span>

                    <h2>
                      Government Innovation Opportunity
                    </h2>

                    <p>
                      RFP #{invitation.rfp_id}
                    </p>
                  </div>
                </div>

                <span
                  className={getStatusClass(
                    invitation.status
                  )}
                >
                  {getStatusLabel(invitation.status)}
                </span>
              </div>

              <div className="invitation-metrics">
                <div>
                  <span>Match Score</span>

                  <strong>
                    {invitation.match_score !== null
                      ? `${invitation.match_score.toFixed(1)}%`
                      : "N/A"}
                  </strong>
                </div>

                <div>
                  <span>Recommendation Rank</span>

                  <strong>
                    {invitation.recommendation_rank !== null
                      ? `#${invitation.recommendation_rank}`
                      : "N/A"}
                  </strong>
                </div>

                <div>
                  <span>Received</span>

                  <strong>
                    {new Date(
                      invitation.invited_at
                    ).toLocaleDateString()}
                  </strong>
                </div>
              </div>

              {invitation.status === "INTERESTED" && (
                <div className="invitation-action-message">
                  <CheckCircle2 size={18} />

                  <span>
                    Your university has expressed interest.
                    You can now submit a proposal.
                  </span>
                </div>
              )}

              {invitation.status === "PROPOSAL_SUBMITTED" && (
                <div className="invitation-action-message">
                  <CheckCircle2 size={18} />

                  <span>
                    Proposal submitted successfully.
                  </span>
                </div>
              )}

              {invitation.status === "INVITED" && (
                <div className="invitation-action-message neutral">
                  <Clock3 size={18} />

                  <span>
                    Review the invitation and respond.
                  </span>
                </div>
              )}

              <div className="invitation-actions">
                {invitation.status === "INVITED" && (
                  <>
                    <button
                      type="button"
                      className="invitation-decline-button"
                      disabled={
                        actionId === invitation.id
                      }
                      onClick={() =>
                        void handleDecline(invitation)
                      }
                    >
                      <XCircle size={17} />
                      Decline
                    </button>

                    <button
                      type="button"
                      className="invitation-interest-button"
                      disabled={
                        actionId === invitation.id
                      }
                      onClick={() =>
                        void handleInterest(invitation)
                      }
                    >
                      {actionId === invitation.id ? (
                        <Loader2
                          size={17}
                          className="invitations-spinner"
                        />
                      ) : (
                        <Sparkles size={17} />
                      )}

                      Express Interest
                    </button>
                  </>
                )}

                {invitation.status === "INTERESTED" && (
                  <button
                    type="button"
                    className="invitation-primary-button"
                    onClick={() =>
                      navigate(
                        `/university/proposals/new?invitation_id=${invitation.id}&rfp_id=${invitation.rfp_id}`
                      )
                    }
                  >
                    Create Proposal
                    <ChevronRight size={17} />
                  </button>
                )}

                {invitation.status ===
                  "PROPOSAL_SUBMITTED" && (
                  <button
                    type="button"
                    className="invitation-secondary-button"
                    disabled
                  >
                    Proposal Already Submitted
                  </button>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}