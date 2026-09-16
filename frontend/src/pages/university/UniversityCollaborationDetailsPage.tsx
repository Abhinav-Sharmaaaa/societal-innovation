import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  Coins,
  Clock3,
  Loader2,
  MessageSquare,
  Rocket,
  ShieldCheck,
  Users,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  decideIndustryCollaboration,
  getUniversityCollaborations,
  type IndustryCollaboration,
} from "../../services/industryCollaborationService";

import "./UniversityCollaborationPages.css";

export default function UniversityCollaborationDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [collaboration, setCollaboration] =
    useState<IndustryCollaboration | null>(null);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] =
    useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [remarks, setRemarks] = useState("");

  useEffect(() => {
    const loadCollaboration = async () => {
      if (!id) {
        setError("Invalid collaboration ID.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const collaborations =
          await getUniversityCollaborations();

        const found = collaborations.find(
          (item) => item.id === Number(id)
        );

        if (!found) {
          setError(
            "Industry collaboration not found."
          );
          return;
        }

        setCollaboration(found);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load collaboration."
        );
      } finally {
        setLoading(false);
      }
    };

    void loadCollaboration();
  }, [id]);

  const handleDecision = async (
    decision:
      | "ACCEPTED"
      | "REJECTED"
      | "MODIFICATION_REQUESTED"
  ) => {
    if (!collaboration) {
      return;
    }

    try {
      setActionLoading(true);
      setError("");
      setMessage("");

      const updated =
        await decideIndustryCollaboration(
          collaboration.id,
          {
            decision,
            remarks:
              remarks.trim() || undefined,
          }
        );

      setCollaboration(updated);

      if (decision === "ACCEPTED") {
        setMessage(
          "Industry collaboration accepted successfully."
        );
      } else if (
        decision === "REJECTED"
      ) {
        setMessage(
          "Industry collaboration rejected."
        );
      } else {
        setMessage(
          "Modification request sent to the industry partner."
        );
      }
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Unable to update collaboration decision."
      );
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <main className="university-collaborations-page">
        <div className="university-collaborations-state">
          <Loader2
            size={28}
            className="university-collaboration-spin"
          />
          Loading collaboration...
        </div>
      </main>
    );
  }

  if (error && !collaboration) {
    return (
      <main className="university-collaborations-page">
        <div className="university-collaborations-state">
          <h2>Collaboration unavailable</h2>

          <p>{error}</p>

          <button
            type="button"
            className="university-collaboration-primary"
            onClick={() =>
              navigate("/university/collaborations")
            }
          >
            <ArrowLeft size={17} />
            Back to Collaborations
          </button>
        </div>
      </main>
    );
  }

  if (!collaboration) {
    return null;
  }

  const canReview =
    collaboration.status === "SUBMITTED" ||
    collaboration.status === "UNDER_REVIEW" ||
    collaboration.status ===
      "MODIFICATION_REQUESTED";

  return (
    <main className="university-collaborations-page">

      <header className="university-collaborations-header">

        <button
          type="button"
          className="university-collaborations-back"
          onClick={() =>
            navigate("/university/collaborations")
          }
        >
          <ArrowLeft size={18} />
          Industry Collaborations
        </button>

        <span>
          INDUSTRY COLLABORATION REVIEW
        </span>

        <h1>{collaboration.title}</h1>

        <p>
          Collaboration #{collaboration.id} ·
          University Proposal #
          {collaboration.university_proposal_id}
        </p>

      </header>

      {error && (
        <div className="university-collaboration-error">
          <AlertCircle size={17} />
          {error}
        </div>
      )}

      {message && (
        <div className="university-collaboration-success">
          <CheckCircle2 size={17} />
          {message}
        </div>
      )}

      <div className="university-collaboration-details-layout">

        {/* ====================================================
            MAIN DETAILS
        ==================================================== */}

        <section className="university-collaboration-details-main">

          <div className="university-collaboration-detail-card">

            <div className="university-detail-heading">
              <div className="university-detail-icon">
                <Rocket size={20} />
              </div>

              <div>
                <span>COLLABORATION STATUS</span>

                <h2>
                  {collaboration.status.replaceAll(
                    "_",
                    " "
                  )}
                </h2>
              </div>
            </div>


            <DetailSection
              title="Collaboration Description"
              value={
                collaboration.collaboration_description
              }
            />

            <DetailSection
              title="Technical Mentorship"
              value={
                collaboration.technical_mentorship
              }
            />

            <DetailSection
              title="Industry Experts"
              value={
                collaboration.industry_experts
              }
            />

            <DetailSection
              title="Infrastructure Resources"
              value={
                collaboration.infrastructure_resources
              }
            />

            <DetailSection
              title="Technology Support"
              value={
                collaboration.technology_support
              }
            />

            <DetailSection
              title="Internship Support"
              value={
                collaboration.internship_support
              }
            />

            <DetailSection
              title="Pilot Deployment Support"
              value={
                collaboration.pilot_deployment_support
              }
            />

            <DetailSection
              title="Commercialization Support"
              value={
                collaboration.commercialization_support
              }
            />

            <DetailSection
              title="Additional Terms"
              value={
                collaboration.additional_terms
              }
            />

          </div>

        </section>


        {/* ====================================================
            SUMMARY / DECISION
        ==================================================== */}

        <aside className="university-collaboration-details-side">

          <div className="university-collaboration-detail-card">

            <div className="university-detail-heading">
              <ShieldCheck size={20} />

              <div>
                <h2>Collaboration Offer</h2>

                <span>
                  Industry contribution
                </span>
              </div>
            </div>


            <SummaryItem
              icon={<Coins size={17} />}
              label="Funding"
              value={
                collaboration.funding_amount !==
                null
                  ? `₹${collaboration.funding_amount.toLocaleString()}`
                  : "Not specified"
              }
            />

            <SummaryItem
              icon={<Clock3 size={17} />}
              label="Duration"
              value={
                collaboration.proposed_duration_days
                  ? `${collaboration.proposed_duration_days} days`
                  : "Not specified"
              }
            />

            <SummaryItem
              icon={<Users size={17} />}
              label="Industry"
              value={`Organization #${collaboration.industry_id}`}
            />


            {collaboration.response_deadline && (
              <SummaryItem
                icon={<Clock3 size={17} />}
                label="Response Deadline"
                value={new Date(
                  collaboration.response_deadline
                ).toLocaleString("en-IN", {
                  dateStyle: "medium",
                  timeStyle: "short",
                })}
              />
            )}


            {canReview && (
              <div className="university-review-box">

                <div className="university-review-heading">
                  <MessageSquare size={18} />

                  <strong>
                    University Decision
                  </strong>
                </div>

                <textarea
                  rows={5}
                  value={remarks}
                  onChange={(event) =>
                    setRemarks(
                      event.target.value
                    )
                  }
                  placeholder="Add review remarks or requested changes..."
                />

                <div className="university-review-actions">

                  <button
                    type="button"
                    className="university-review-accept"
                    disabled={actionLoading}
                    onClick={() =>
                      void handleDecision(
                        "ACCEPTED"
                      )
                    }
                  >
                    {actionLoading ? (
                      <Loader2
                        size={16}
                        className="university-collaboration-spin"
                      />
                    ) : (
                      <CheckCircle2 size={16} />
                    )}

                    Accept
                  </button>

                  <button
                    type="button"
                    className="university-review-modify"
                    disabled={actionLoading}
                    onClick={() =>
                      void handleDecision(
                        "MODIFICATION_REQUESTED"
                      )
                    }
                  >
                    <MessageSquare size={16} />
                    Request Changes
                  </button>

                  <button
                    type="button"
                    className="university-review-reject"
                    disabled={actionLoading}
                    onClick={() =>
                      void handleDecision(
                        "REJECTED"
                      )
                    }
                  >
                    <XCircle size={16} />
                    Reject
                  </button>

                </div>

              </div>
            )}


            {!canReview &&
              collaboration.status ===
                "ACCEPTED" && (
                <div className="university-collaboration-status-message accepted">
                  <CheckCircle2 size={18} />

                  <span>
                    Collaboration accepted.
                    Government can now create the
                    project.
                  </span>
                </div>
              )}

            {!canReview &&
              collaboration.status ===
                "REJECTED" && (
                <div className="university-collaboration-status-message rejected">
                  <XCircle size={18} />

                  <span>
                    This collaboration has been
                    rejected.
                  </span>
                </div>
              )}

          </div>

        </aside>

      </div>

    </main>
  );
}


function DetailSection({
  title,
  value,
}: {
  title: string;
  value: string | null;
}) {
  if (!value) {
    return null;
  }

  return (
    <section className="university-collaboration-detail-section">

      <h3>{title}</h3>

      <p>{value}</p>

    </section>
  );
}


function SummaryItem({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="university-collaboration-summary-item">

      <div>
        {icon}
      </div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>

    </div>
  );
}