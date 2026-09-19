import {
  ArrowLeft,
  Calendar,
  CheckCircle2,
  Clock3,
  Coins,
  FileText,
  Handshake,
  Loader2,
  Users,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getIndustryCollaborationById,
  type IndustryCollaboration,
  type IndustryCollaborationStatus,
} from "../../services/industryCollaborationService";

import "./IndustryCollaborationDetailsPage.css";


const STATUS_CONFIG: Record<
  IndustryCollaborationStatus,
  { label: string; color: string }
> = {
  DRAFT: { label: "Draft", color: "grey" },
  SUBMITTED: { label: "Submitted", color: "blue" },
  UNDER_REVIEW: { label: "Under Review", color: "blue" },
  MODIFICATION_REQUESTED: {
    label: "Modification Requested",
    color: "amber",
  },
  ACCEPTED: { label: "Accepted", color: "green" },
  REJECTED: { label: "Rejected", color: "red" },
  WITHDRAWN: { label: "Withdrawn", color: "red" },
};


export default function IndustryCollaborationDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [collab, setCollab] =
    useState<IndustryCollaboration | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    const load = async () => {
      if (!id) {
        setError("Invalid collaboration ID.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const data = await getIndustryCollaborationById(
          Number(id)
        );

        setCollab(data);
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            "Unable to load this collaboration proposal."
        );
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [id]);


  if (loading) {
    return (
      <main className="collab-details-page">
        <div className="collab-details-state">
          <Loader2
            size={28}
            className="collab-details-spin"
          />
          Loading collaboration...
        </div>
      </main>
    );
  }


  if (error || !collab) {
    return (
      <main className="collab-details-page">
        <div className="collab-details-state collab-details-state-error">
          <XCircle size={38} />
          <h2>Collaboration not found</h2>
          <p>
            {error ||
              "This collaboration proposal could not be loaded."}
          </p>
          <button
            type="button"
            className="collab-details-primary"
            onClick={() =>
              navigate("/industry/collaborations")
            }
          >
            <ArrowLeft size={17} />
            My Collaborations
          </button>
        </div>
      </main>
    );
  }


  const statusCfg =
    STATUS_CONFIG[collab.status] ?? {
      label: collab.status,
      color: "grey",
    };


  return (
    <main className="collab-details-page">

      <header className="collab-details-header">

        <button
          type="button"
          className="collab-details-back"
          onClick={() =>
            navigate("/industry/collaborations")
          }
        >
          <ArrowLeft size={18} />
          My Collaborations
        </button>

        <span>INDUSTRY COLLABORATION PROPOSAL</span>

        <div className="collab-details-title-row">
          <h1>{collab.title}</h1>

          <span
            className={`collab-details-status collab-details-status-${statusCfg.color}`}
          >
            {statusCfg.label}
          </span>
        </div>

        <p>
          Collaboration #{collab.id} · University Proposal
          #{collab.university_proposal_id}
        </p>

      </header>


      <div className="collab-details-layout">

        {/* === MAIN CONTENT === */}
        <section className="collab-details-main">

          {/* Description */}
          <div className="collab-details-card">

            <div className="collab-details-card-title">
              <div className="collab-details-card-icon">
                <Handshake size={20} />
              </div>

              <div>
                <h2>Collaboration Description</h2>
                <span>
                  How your organization will support the university
                </span>
              </div>
            </div>

            <p className="collab-details-body-text">
              {collab.collaboration_description}
            </p>

          </div>


          {/* Industry Support */}
          {(collab.technical_mentorship ||
            collab.industry_experts ||
            collab.infrastructure_resources ||
            collab.technology_support ||
            collab.internship_support ||
            collab.pilot_deployment_support ||
            collab.commercialization_support) && (
            <div className="collab-details-card">

              <div className="collab-details-card-title">
                <div className="collab-details-card-icon">
                  <Users size={20} />
                </div>

                <div>
                  <h2>Industry Support Offered</h2>
                  <span>
                    Resources and assistance your organization
                    will provide
                  </span>
                </div>
              </div>

              {collab.technical_mentorship && (
                <SupportBlock
                  label="Technical Mentorship"
                  value={collab.technical_mentorship}
                />
              )}

              {collab.industry_experts && (
                <SupportBlock
                  label="Industry Experts"
                  value={collab.industry_experts}
                />
              )}

              {collab.infrastructure_resources && (
                <SupportBlock
                  label="Infrastructure Resources"
                  value={collab.infrastructure_resources}
                />
              )}

              {collab.technology_support && (
                <SupportBlock
                  label="Technology Support"
                  value={collab.technology_support}
                />
              )}

              {collab.internship_support && (
                <SupportBlock
                  label="Internship Support"
                  value={collab.internship_support}
                />
              )}

              {collab.pilot_deployment_support && (
                <SupportBlock
                  label="Pilot Deployment Support"
                  value={collab.pilot_deployment_support}
                />
              )}

              {collab.commercialization_support && (
                <SupportBlock
                  label="Commercialization Support"
                  value={collab.commercialization_support}
                />
              )}

            </div>
          )}


          {/* Additional Terms */}
          {collab.additional_terms && (
            <div className="collab-details-card">

              <div className="collab-details-card-title">
                <div className="collab-details-card-icon">
                  <FileText size={20} />
                </div>

                <div>
                  <h2>Additional Terms</h2>
                </div>
              </div>

              <p className="collab-details-body-text">
                {collab.additional_terms}
              </p>

            </div>
          )}

        </section>


        {/* === SIDEBAR === */}
        <aside className="collab-details-side">

          <div className="collab-details-card">

            <div className="collab-details-card-title">
              <div className="collab-details-card-icon">
                <CheckCircle2 size={20} />
              </div>

              <div>
                <h2>Proposal Summary</h2>
              </div>
            </div>


            <StatRow
              icon={<Coins size={16} />}
              label="Funding Offered"
              value={
                collab.funding_amount !== null
                  ? `₹${collab.funding_amount.toLocaleString()}`
                  : "Not specified"
              }
            />

            <StatRow
              icon={<Clock3 size={16} />}
              label="Proposed Duration"
              value={
                collab.proposed_duration_days
                  ? `${collab.proposed_duration_days} days`
                  : "Not specified"
              }
            />

            <StatRow
              icon={<Calendar size={16} />}
              label="Response Deadline"
              value={
                collab.response_deadline
                  ? new Date(
                      collab.response_deadline
                    ).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    })
                  : "Not specified"
              }
            />

            <StatRow
              icon={<Calendar size={16} />}
              label="Submitted At"
              value={
                collab.submitted_at
                  ? new Date(
                      collab.submitted_at
                    ).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    })
                  : "Not yet submitted"
              }
            />

            <StatRow
              icon={<Calendar size={16} />}
              label="Last Reviewed"
              value={
                collab.reviewed_at
                  ? new Date(
                      collab.reviewed_at
                    ).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    })
                  : "Pending review"
              }
            />


            <div className="collab-details-view-proposal-btn-wrapper">
              <button
                type="button"
                className="collab-details-primary"
                onClick={() =>
                  navigate(
                    `/industry/opportunities/${collab.university_proposal_id}`
                  )
                }
              >
                <FileText size={17} />
                View University Proposal
              </button>
            </div>

          </div>

        </aside>

      </div>

    </main>
  );
}


/* ============================================================
   SUB COMPONENTS
============================================================ */

function SupportBlock({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="collab-details-support-block">
      <strong>{label}</strong>
      <p>{value}</p>
    </div>
  );
}


function StatRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="collab-details-stat">
      <div className="collab-details-stat-icon">
        {icon}
      </div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}
