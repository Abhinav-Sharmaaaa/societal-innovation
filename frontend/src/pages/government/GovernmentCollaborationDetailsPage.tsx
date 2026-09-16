import {
  ArrowLeft,
  CheckCircle2,
  Clock3,
  Coins,
  FileText,
  Loader2,
  Rocket,
  Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getAcceptedGovernmentCollaborations,
  type IndustryCollaboration,
} from "../../services/industryCollaborationService";

import "./GovernmentCollaborationPages.css";

export default function GovernmentCollaborationDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [collaboration, setCollaboration] =
    useState<IndustryCollaboration | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
          await getAcceptedGovernmentCollaborations();

        const found = collaborations.find(
          (item) => item.id === Number(id)
        );

        if (!found) {
          setError(
            "Accepted collaboration was not found."
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

  if (loading) {
    return (
      <main className="government-collaborations-page">
        <div className="government-collaborations-state">
          <Loader2
            size={28}
            className="government-collaboration-spin"
          />
          Loading collaboration...
        </div>
      </main>
    );
  }

  if (error || !collaboration) {
    return (
      <main className="government-collaborations-page">
        <div className="government-collaborations-state">

          <h2>
            Collaboration unavailable
          </h2>

          <p>
            {error ||
              "The accepted collaboration could not be found."}
          </p>

          <button
            type="button"
            className="government-project-button"
            onClick={() =>
              navigate(
                "/government/collaborations"
              )
            }
          >
            <ArrowLeft size={17} />
            Back
          </button>

        </div>
      </main>
    );
  }

  return (
    <main className="government-collaborations-page">

      <header className="government-collaborations-header">

        <button
          type="button"
          className="government-collaborations-back"
          onClick={() =>
            navigate(
              "/government/collaborations"
            )
          }
        >
          <ArrowLeft size={18} />
          Accepted Collaborations
        </button>

        <span>
          ACCEPTED PARTNERSHIP
        </span>

        <h1>
          {collaboration.title}
        </h1>

        <p>
          Collaboration #{collaboration.id}
          {" · "}
          University Proposal #
          {collaboration.university_proposal_id}
        </p>

      </header>

      <div className="government-collaboration-details">

        <section className="government-collaboration-detail-card">

          <div className="government-detail-heading">

            <div className="government-detail-icon">
              <Rocket size={20} />
            </div>

            <div>
              <span>
                COLLABORATION STATUS
              </span>

              <h2>
                ACCEPTED
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

        </section>


        <aside className="government-collaboration-side">

          <div className="government-collaboration-detail-card">

            <div className="government-detail-heading">
              <CheckCircle2 size={20} />

              <div>
                <h2>
                  Project Readiness
                </h2>

                <span>
                  Approved for execution
                </span>
              </div>
            </div>


            <SummaryItem
              icon={<Coins size={17} />}
              label="Industry Funding"
              value={
                collaboration.funding_amount !== null
                  ? `₹${collaboration.funding_amount.toLocaleString()}`
                  : "Not specified"
              }
            />

            <SummaryItem
              icon={<Clock3 size={17} />}
              label="Proposed Duration"
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

            <SummaryItem
              icon={<FileText size={17} />}
              label="University Proposal"
              value={`#${collaboration.university_proposal_id}`}
            />


            <div className="government-ready-message">
              <CheckCircle2 size={18} />

              <span>
                The collaboration has been accepted by
                the university and can now be converted
                into a project.
              </span>
            </div>


            <button
              type="button"
              className="government-create-project-button"
              onClick={() =>
                navigate(
                  `/government/projects/new?collaboration_id=${collaboration.id}`
                )
              }
            >
              <Rocket size={18} />
              Create Project
            </button>

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
    <section className="government-detail-section">
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
    <div className="government-summary-item">
      <div>{icon}</div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}