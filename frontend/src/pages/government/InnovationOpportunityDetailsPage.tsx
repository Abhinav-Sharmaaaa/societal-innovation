import {
  ArrowLeft,
  CheckCircle2,
  FileText,
  Lightbulb,
  Loader2,
  ShieldCheck,
} from "lucide-react";
import {
  useEffect,
  useState,
} from "react";
import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  innovationService,
  type InnovationOpportunity,
} from "../../services/innovationService";

import "./InnovationPages.css";


export default function InnovationOpportunityDetailsPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  const opportunityId =
    Number(id);

  const [opportunity, setOpportunity] =
    useState<InnovationOpportunity | null>(
      null,
    );

  const [loading, setLoading] =
    useState(true);

  const [actionLoading, setActionLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");


  async function loadOpportunity() {
    try {
      setLoading(true);
      setError("");

      const data =
        await innovationService.getOpportunity(
          opportunityId,
        );

      setOpportunity(data);

    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to load innovation opportunity.",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadOpportunity();
  }, [opportunityId]);


  async function handleApprove() {
    try {
      setActionLoading(true);
      setError("");
      setMessage("");

      const data =
        await innovationService.approveOpportunity(
          opportunityId,
        );

      setOpportunity(data);

      setMessage(
        "Innovation opportunity approved successfully.",
      );

    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to approve opportunity.",
      );
    } finally {
      setActionLoading(false);
    }
  }


  if (loading) {
    return (
      <main className="innovation-page">

        <div className="innovation-loading">
          <Loader2
            size={20}
            className="button-spin"
          />
          Loading opportunity...
        </div>

      </main>
    );
  }


  if (!opportunity) {
    return (
      <main className="innovation-page">

        <div className="innovation-error-page">

          <strong>
            Opportunity unavailable
          </strong>

          <p>
            {error ||
              "Innovation opportunity not found."}
          </p>

          <button
            onClick={() =>
              navigate(
                "/government/dashboard",
              )
            }
          >
            Dashboard
          </button>

        </div>

      </main>
    );
  }


  const canApprove =
    opportunity.status === "DRAFT";


  const canCreateRFP =
    opportunity.status === "APPROVED";


  return (
    <main className="innovation-page">

      <header className="innovation-header">

        <button
          className="innovation-back"
          onClick={() =>
            navigate(
              `/government/challenges/${opportunity.challenge_id}`,
            )
          }
        >
          <ArrowLeft size={16} />
          Challenge
        </button>

        <span className="innovation-eyebrow">
          INNOVATION OPPORTUNITY
        </span>

        <h1>
          {opportunity.title}
        </h1>

        <p>
          Opportunity #{opportunity.id}
          {" • "}
          Challenge #{opportunity.challenge_id}
        </p>

      </header>


      <div className="innovation-container">

        {error && (
          <div className="innovation-error">
            {error}
          </div>
        )}

        {message && (
          <div className="innovation-success">
            <CheckCircle2 size={17} />
            {message}
          </div>
        )}


        <section className="opportunity-status-card">

          <div className="opportunity-status-main">

            <div className="opportunity-icon">
              <Lightbulb size={22} />
            </div>

            <div>

              <span>
                Status
              </span>

              <strong>
                {formatValue(
                  opportunity.status,
                )}
              </strong>

            </div>

          </div>


          <div className="opportunity-actions">

            {canApprove && (
              <button
                className="innovation-primary-button"
                onClick={handleApprove}
                disabled={actionLoading}
              >
                {actionLoading ? (
                  <Loader2
                    size={16}
                    className="button-spin"
                  />
                ) : (
                  <ShieldCheck size={16} />
                )}

                Approve Opportunity
              </button>
            )}


            {canCreateRFP && (
              <button
                className="innovation-primary-button"
                onClick={() =>
                  navigate(
                    `/government/rfps/new?opportunity_id=${opportunity.id}`,
                  )
                }
              >
                <FileText size={16} />
                Create RFP
              </button>
            )}

          </div>

        </section>


        <section className="opportunity-grid">

          <ContentCard
            title="Problem Statement"
            value={
              opportunity.problem_statement
            }
          />

          <ContentCard
            title="Objectives"
            value={
              opportunity.objectives ||
              "Not specified."
            }
          />

          <ContentCard
            title="Technical Requirements"
            value={
              opportunity.technical_requirements ||
              "Not specified."
            }
          />

          <ContentCard
            title="Expected Outcomes"
            value={
              opportunity.expected_outcomes ||
              "Not specified."
            }
          />

        </section>


        <section className="opportunity-metadata">

          <MetadataItem
            label="Estimated Budget"
            value={
              opportunity.estimated_budget !=
              null
                ? `₹${opportunity.estimated_budget.toLocaleString()}`
                : "Not specified"
            }
          />

          <MetadataItem
            label="Duration"
            value={
              opportunity.expected_duration_days !=
              null
                ? `${opportunity.expected_duration_days} days`
                : "Not specified"
            }
          />

          <MetadataItem
            label="Proposal Deadline"
            value={
              opportunity.proposal_deadline
                ? formatDate(
                    opportunity.proposal_deadline,
                  )
                : "Not specified"
            }
          />

          <MetadataItem
            label="Created"
            value={formatDate(
              opportunity.created_at,
            )}
          />

          <MetadataItem
            label="Approved"
            value={
              opportunity.approved_at
                ? formatDate(
                    opportunity.approved_at,
                  )
                : "Not approved"
            }
          />

        </section>

      </div>

    </main>
  );
}


function ContentCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <section className="content-card">

      <h2>
        {title}
      </h2>

      <p>
        {value}
      </p>

    </section>
  );
}


function MetadataItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="metadata-item">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


function formatValue(
  value: string,
) {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    );
}


function formatDate(
  value: string,
) {
  return new Date(value).toLocaleString(
    "en-IN",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  );
}