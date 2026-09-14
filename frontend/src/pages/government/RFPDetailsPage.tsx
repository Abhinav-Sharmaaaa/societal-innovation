import {
  ArrowLeft,
  CheckCircle2,
  FileText,
  Lock,
  Loader2,
  Send,
  Users,
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
  type RFP,
} from "../../services/innovationService";

import "./InnovationPages.css";


export default function RFPDetailsPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  const rfpId = Number(id);

  const [rfp, setRfp] =
    useState<RFP | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [actionLoading, setActionLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");


  async function loadRFP() {
    try {
      setLoading(true);
      setError("");

      const data =
        await innovationService.getRFP(
          rfpId,
        );

      setRfp(data);

    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Unable to load RFP.",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadRFP();
  }, [rfpId]);


  async function handlePublish() {
    try {
      setActionLoading(true);
      setError("");
      setMessage("");

      const data =
        await innovationService.publishRFP(
          rfpId,
        );

      setRfp(data);

      setMessage(
        "RFP published successfully.",
      );

    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Unable to publish RFP.",
      );
    } finally {
      setActionLoading(false);
    }
  }


  async function handleClose() {
    try {
      setActionLoading(true);
      setError("");
      setMessage("");

      const data =
        await innovationService.closeRFP(
          rfpId,
        );

      setRfp(data);

      setMessage(
        "RFP closed successfully.",
      );

    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
        "Unable to close RFP.",
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

          Loading RFP...
        </div>

      </main>
    );
  }


  if (!rfp) {
    return (
      <main className="innovation-page">

        <div className="innovation-error-page">

          <strong>
            RFP unavailable
          </strong>

          <p>
            {error ||
              "The requested RFP was not found."}
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


  const canPublish =
    rfp.status === "DRAFT";

  const canClose =
    rfp.status === "PUBLISHED";


  return (
    <main className="innovation-page">

      <header className="innovation-header">

        <button
          className="innovation-back"
          onClick={() =>
            navigate(
              `/government/innovation/${rfp.innovation_opportunity_id}`,
            )
          }
        >
          <ArrowLeft size={16} />
          Innovation Opportunity
        </button>

        <span className="innovation-eyebrow">
          REQUEST FOR PROPOSAL
        </span>

        <h1>
          {rfp.title}
        </h1>

        <p>
          RFP #{rfp.id}
          {" • "}
          Opportunity #
          {rfp.innovation_opportunity_id}
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


        <section className="rfp-status-card">

          <div className="rfp-status-main">

            <div className="rfp-icon">
              <Users size={21} />
            </div>

            <div>

              <span>
                RFP Status
              </span>

              <strong>
                {formatValue(
                  rfp.status,
                )}
              </strong>

            </div>

          </div>


          <div className="opportunity-actions">

            {canPublish && (
              <button
                className="innovation-primary-button"
                onClick={handlePublish}
                disabled={actionLoading}
              >
                {actionLoading ? (
                  <Loader2
                    size={16}
                    className="button-spin"
                  />
                ) : (
                  <Send size={16} />
                )}

                Publish RFP
              </button>
            )}


            {rfp.status === "PUBLISHED" && (
              <>
                {/* ==================================================
                    University Matching
                ================================================== */}

                <button
                  className="innovation-primary-button"
                  onClick={() =>
                    navigate(
                      `/government/rfps/${rfp.id}/universities`,
                    )
                  }
                >
                  <Users size={16} />
                  Match Universities
                </button>


                {/* ==================================================
                    View University Proposals
                ================================================== */}

                <button
                  className="innovation-primary-button"
                  onClick={() =>
                    navigate(
                      `/government/rfps/${rfp.id}/proposals`,
                    )
                  }
                >
                  <FileText size={16} />
                  View Proposals
                </button>
              </>
            )}


            {canClose && (
              <button
                className="innovation-danger-button"
                onClick={handleClose}
                disabled={actionLoading}
              >
                {actionLoading ? (
                  <Loader2
                    size={16}
                    className="button-spin"
                  />
                ) : (
                  <Lock size={16} />
                )}

                Close RFP
              </button>
            )}

          </div>

        </section>


        <section className="rfp-content-card">

          <h2>
            Description
          </h2>

          <p>
            {rfp.description}
          </p>

        </section>


        <section className="opportunity-grid">

          <ContentCard
            title="Objectives"
            value={
              rfp.objectives ||
              "Not specified."
            }
          />

          <ContentCard
            title="Technical Requirements"
            value={
              rfp.technical_requirements ||
              "Not specified."
            }
          />

          <ContentCard
            title="Expected Outcomes"
            value={
              rfp.expected_outcomes ||
              "Not specified."
            }
          />

        </section>


        <section className="opportunity-metadata">

          <MetadataItem
            label="Estimated Budget"
            value={
              rfp.estimated_budget != null
                ? `₹${rfp.estimated_budget.toLocaleString()}`
                : "Not specified"
            }
          />

          <MetadataItem
            label="Duration"
            value={
              rfp.expected_duration_days !=
                null
                ? `${rfp.expected_duration_days} days`
                : "Not specified"
            }
          />

          <MetadataItem
            label="Proposal Deadline"
            value={
              rfp.proposal_deadline
                ? formatDate(
                    rfp.proposal_deadline,
                  )
                : "Not specified"
            }
          />

          <MetadataItem
            label="Published"
            value={
              rfp.published_at
                ? formatDate(
                    rfp.published_at,
                  )
                : "Not published"
            }
          />

          <MetadataItem
            label="Created"
            value={formatDate(
              rfp.created_at,
            )}
          />

        </section>


        {rfp.status === "PUBLISHED" && (
          <section className="rfp-next-step">

            <CheckCircle2 size={20} />

            <div>

              <strong>
                RFP is now accepting university participation
              </strong>

              <p>
                Universities can be matched and invited,
                and submitted proposals can now be reviewed
                by authorized government officers.
              </p>

            </div>

          </section>
        )}

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

      <h2>{title}</h2>

      <p>{value}</p>

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

      <span>{label}</span>

      <strong>{value}</strong>

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