import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  AlertTriangle,
  ArrowLeft,
  BrainCircuit,
  CalendarDays,
  CheckCircle2,
  Clock3,
  FileText,
  MapPin,
  Users,
} from "lucide-react";

import { api } from "../../services/api";
import "./ChallengeDetailsPage.css";

interface Evidence {
  id: number;
  evidence_type: string;
  original_filename: string;
  content_type: string | null;
  file_size: number | null;
  file_url: string | null;
  uploaded_by: number;
  created_at: string;
}

interface CategoryPrediction {
  rank: number;
  category: string;
  confidence: number;
}

interface Challenge {
  id: number;
  title: string;
  description: string;
  submitted_by: number;

  category: string;
  severity: string;
  urgency: string;

  affected_population: number | null;
  estimated_economic_loss: number | null;

  address: string | null;
  district: string | null;
  state: string | null;
  latitude: number | null;
  longitude: number | null;

  innovation_required: boolean;

  // Persisted AI fields
  ai_confidence_score: number | null;
  ai_model_version: string | null;

  ai_category_confidence: number | null;
  ai_second_category: string | null;
  ai_second_category_confidence: number | null;
  ai_category_margin: number | null;
  ai_category_decision: string | null;
  ai_requires_human_review: boolean | null;
  ai_category_top_3: CategoryPrediction[] | null;
  ai_analysis_at: string | null;

  routing_type: string;
  routing_reason: string | null;

  status: string;

  is_master_challenge: boolean;
  master_challenge_id: number | null;
  duplicate_similarity_score: number | null;

  evidence: Evidence[];

  created_at: string;
  updated_at: string;
}

const statusSteps = [
  {
    key: "SUBMITTED",
    label: "Submitted",
    description: "Challenge has been submitted successfully.",
  },
  {
    key: "UNDER_AI_ANALYSIS",
    label: "AI Analysis",
    description: "The challenge is being analyzed and classified.",
  },
  {
    key: "UNDER_REVIEW",
    label: "Human Review",
    description: "An authorized officer may review the challenge.",
  },
  {
    key: "ROUTED",
    label: "Routed",
    description:
      "The challenge has been sent to the appropriate pathway.",
  },
  {
    key: "IN_PROGRESS",
    label: "In Progress",
    description: "Action or solution development is underway.",
  },
  {
    key: "RESOLVED",
    label: "Resolved",
    description: "The reported challenge has been addressed.",
  },
  {
    key: "CLOSED",
    label: "Closed",
    description: "The challenge lifecycle has been completed.",
  },
];

const statusOrder = statusSteps.map((step) => step.key);

function formatLabel(value: string) {
  return value.replaceAll("_", " ");
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function getStatusIndex(status: string) {
  const index = statusOrder.indexOf(status);
  return index === -1 ? 0 : index;
}

function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export default function ChallengeDetailsPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadChallenge() {
      if (!id) {
        setError("Challenge ID is missing.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const response = await api.get<Challenge>(
          `/challenges/${id}`
        );

        setChallenge(response.data);
      } catch (err: any) {
        const message =
          err?.response?.data?.detail ||
          "Unable to load challenge details.";

        setError(
          Array.isArray(message)
            ? message.map((item) => item.msg).join(", ")
            : message
        );
      } finally {
        setLoading(false);
      }
    }

    loadChallenge();
  }, [id]);

  if (loading) {
    return (
      <div className="challenge-details-page">
        <div className="details-container">
          <div className="details-loading">
            Loading challenge details...
          </div>
        </div>
      </div>
    );
  }

  if (error || !challenge) {
    return (
      <div className="challenge-details-page">
        <div className="details-container">
          <button
            type="button"
            className="details-back-button"
            onClick={() => navigate("/citizen/dashboard")}
          >
            <ArrowLeft size={18} />
            Back to Dashboard
          </button>

          <div className="details-error">
            {error || "Challenge not found."}
          </div>
        </div>
      </div>
    );
  }

  const currentStatusIndex = getStatusIndex(challenge.status);

  const hasPersistedAI =
    challenge.ai_category_confidence !== null ||
    challenge.ai_category_decision !== null ||
    challenge.ai_analysis_at !== null;

  const resolvedConfidence =
    challenge.ai_category_confidence ??
    challenge.ai_confidence_score;

  const resolvedRouting =
    challenge.routing_type || "PENDING";

  const resolvedRoutingReason =
    challenge.routing_reason ||
    "Routing analysis has not been completed yet.";

  return (
    <div className="challenge-details-page">
      <div className="details-container">
        <button
          type="button"
          className="details-back-button"
          onClick={() => navigate("/citizen/dashboard")}
        >
          <ArrowLeft size={18} />
          Back to Dashboard
        </button>

        <div className="details-header">
          <div>
            <span className="details-eyebrow">
              CHALLENGE #{challenge.id}
            </span>

            <h1>{challenge.title}</h1>

            <div className="header-meta">
              <span>
                <CalendarDays size={15} />
                {formatDate(challenge.created_at)}
              </span>

              {challenge.district && (
                <span>
                  <MapPin size={15} />
                  {challenge.district}
                  {challenge.state
                    ? `, ${challenge.state}`
                    : ""}
                </span>
              )}
            </div>
          </div>

          <div
            className={`main-status status-${challenge.status.toLowerCase()}`}
          >
            {formatLabel(challenge.status)}
          </div>
        </div>

        {/* =========================================================
            AI TRIAGE ANALYSIS
           ========================================================= */}

        {hasPersistedAI && (
          <section className="details-card ai-summary-card">
            <div className="card-title">
              <BrainCircuit size={19} />
              <h2>AI Triage Analysis</h2>
            </div>

            <div className="ai-summary-grid">
              <div className="ai-metric">
                <span>Primary Category</span>
                <strong>
                  {formatLabel(challenge.category)}
                </strong>
              </div>

              <div className="ai-metric">
                <span>Confidence</span>
                <strong>
                  {challenge.ai_category_confidence !== null
                    ? percent(
                        challenge.ai_category_confidence
                      )
                    : "N/A"}
                </strong>
              </div>

              <div className="ai-metric">
                <span>Decision</span>
                <strong>
                  {challenge.ai_category_decision
                    ? formatLabel(
                        challenge.ai_category_decision
                      )
                    : "N/A"}
                </strong>
              </div>

              <div className="ai-metric">
                <span>Routing</span>
                <strong>
                  {formatLabel(resolvedRouting)}
                </strong>
              </div>
            </div>

            {challenge.ai_requires_human_review && (
              <div className="ai-review-banner">
                <AlertTriangle size={18} />

                <div>
                  <strong>Human Review Required</strong>

                  <p>
                    The AI classification is ambiguous or
                    low-confidence, so automated routing has
                    been paused.
                  </p>
                </div>
              </div>
            )}

            {challenge.ai_category_top_3 &&
              challenge.ai_category_top_3.length > 0 && (
                <div className="ai-alternatives">
                  <div className="ai-alternatives-title">
                    Top Category Predictions
                  </div>

                  {challenge.ai_category_top_3.map(
                    (item) => (
                      <div
                        className="ai-alternative-row"
                        key={`${item.rank}-${item.category}`}
                      >
                        <div>
                          <span>#{item.rank}</span>

                          <strong>
                            {formatLabel(item.category)}
                          </strong>
                        </div>

                        <strong>
                          {percent(item.confidence)}
                        </strong>
                      </div>
                    )
                  )}
                </div>
              )}

            {challenge.ai_category_margin !== null && (
              <div className="ai-details-row">
                <span>Top-1 / Top-2 Margin</span>

                <strong>
                  {percent(
                    Math.max(
                      0,
                      challenge.ai_category_margin
                    )
                  )}
                </strong>
              </div>
            )}

            <div className="ai-details-row">
              <span>Severity</span>

              <strong>
                {formatLabel(challenge.severity)}
              </strong>
            </div>

            <div className="ai-details-row">
              <span>Urgency</span>

              <strong>
                {formatLabel(challenge.urgency)}
              </strong>
            </div>

            <div className="ai-details-row">
              <span>Innovation Required</span>

              <strong>
                {challenge.innovation_required
                  ? "Yes"
                  : "No"}
              </strong>
            </div>

            <div className="ai-model-version">
              <strong>Routing Explanation</strong>

              <p>
                {challenge.routing_reason ||
                  "No routing explanation available."}
              </p>
            </div>

            <p className="ai-model-version">
              Model:{" "}
              {challenge.ai_model_version || "N/A"}
            </p>

            {challenge.ai_analysis_at && (
              <p className="ai-model-version">
                Analyzed:{" "}
                {formatDate(
                  challenge.ai_analysis_at
                )}
              </p>
            )}
          </section>
        )}

        <div className="details-grid">
          <main className="details-main">
            {/* =====================================================
                PROBLEM DESCRIPTION
               ===================================================== */}

            <section className="details-card">
              <div className="card-title">
                <FileText size={19} />
                <h2>Problem Description</h2>
              </div>

              <p className="description-text">
                {challenge.description}
              </p>
            </section>

            {/* =====================================================
                CHALLENGE STATUS
               ===================================================== */}

            <section className="details-card">
              <div className="card-title">
                <Clock3 size={19} />
                <h2>Challenge Status</h2>
              </div>

              <div className="timeline">
                {statusSteps.map((step, index) => {
                  const completed =
                    index <= currentStatusIndex;

                  const current =
                    index === currentStatusIndex;

                  return (
                    <div
                      className={`timeline-item ${
                        completed ? "completed" : ""
                      } ${current ? "current" : ""}`}
                      key={step.key}
                    >
                      <div className="timeline-marker">
                        {completed ? (
                          <CheckCircle2 size={17} />
                        ) : (
                          <span />
                        )}
                      </div>

                      <div className="timeline-content">
                        <strong>{step.label}</strong>
                        <p>{step.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* =====================================================
                EVIDENCE
               ===================================================== */}

            <section className="details-card">
              <div className="card-title">
                <FileText size={19} />
                <h2>Evidence</h2>
              </div>

              {challenge.evidence.length === 0 ? (
                <div className="empty-evidence">
                  No evidence has been uploaded.
                </div>
              ) : (
                <div className="evidence-list">
                  {challenge.evidence.map((item) => (
                    <div
                      className="evidence-item"
                      key={item.id}
                    >
                      <div className="evidence-icon">
                        <FileText size={18} />
                      </div>

                      <div className="evidence-info">
                        <strong>
                          {item.original_filename}
                        </strong>

                        <span>
                          {formatLabel(
                            item.evidence_type
                          )}

                          {item.file_size
                            ? ` • ${(
                                item.file_size /
                                1024 /
                                1024
                              ).toFixed(2)} MB`
                            : ""}
                        </span>
                      </div>

                      {item.file_url && (
                        <a
                          href={item.file_url}
                          target="_blank"
                          rel="noreferrer"
                          className="evidence-link"
                        >
                          View
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </section>
          </main>

          <aside className="details-sidebar">
            {/* =====================================================
                CHALLENGE INFORMATION
               ===================================================== */}

            <section className="details-card">
              <div className="card-title">
                <Users size={19} />
                <h2>Challenge Information</h2>
              </div>

              <div className="info-list">
                <div className="info-row">
                  <span>Category</span>

                  <strong>
                    {formatLabel(challenge.category)}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Urgency</span>

                  <strong
                    className={`urgency-${challenge.urgency.toLowerCase()}`}
                  >
                    {formatLabel(challenge.urgency)}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Severity</span>

                  <strong>
                    {formatLabel(challenge.severity)}
                  </strong>
                </div>

                <div className="info-row">
                  <span>People affected</span>

                  <strong>
                    {challenge.affected_population ??
                      "Not specified"}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Economic loss</span>

                  <strong>
                    {challenge.estimated_economic_loss !==
                    null
                      ? `₹${challenge.estimated_economic_loss.toLocaleString(
                          "en-IN"
                        )}`
                      : "Not specified"}
                  </strong>
                </div>

                <div className="info-row">
                  <span>Innovation required</span>

                  <strong>
                    {challenge.innovation_required
                      ? "Yes"
                      : "No"}
                  </strong>
                </div>
              </div>
            </section>

            {/* =====================================================
                ROUTING
               ===================================================== */}

            <section className="details-card routing-card">
              <div className="card-title">
                <MapPin size={19} />
                <h2>Routing</h2>
              </div>

              <div className="routing-type">
                {formatLabel(resolvedRouting)}
              </div>

              <p>
                {resolvedRoutingReason}
              </p>

              {resolvedConfidence !== null &&
                resolvedConfidence !== undefined && (
                  <div className="confidence-block">
                    <div className="confidence-header">
                      <span>AI Confidence</span>

                      <strong>
                        {percent(resolvedConfidence)}
                      </strong>
                    </div>

                    <div className="confidence-bar">
                      <div
                        className="confidence-fill"
                        style={{
                          width: `${Math.min(
                            100,
                            Math.max(
                              0,
                              resolvedConfidence * 100
                            )
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                )}

              {challenge.ai_category_margin !== null && (
                <div className="confidence-block">
                  <div className="confidence-header">
                    <span>Category Margin</span>

                    <strong>
                      {percent(
                        Math.max(
                          0,
                          challenge.ai_category_margin
                        )
                      )}
                    </strong>
                  </div>

                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(
                            0,
                            challenge.ai_category_margin *
                              100
                          )
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </section>

            {/* =====================================================
                LOCATION
               ===================================================== */}

            <section className="details-card location-card">
              <div className="card-title">
                <MapPin size={19} />
                <h2>Location</h2>
              </div>

              {challenge.address && (
                <p>{challenge.address}</p>
              )}

              <p>
                {challenge.district ||
                  "District not specified"}

                {challenge.state
                  ? `, ${challenge.state}`
                  : ""}
              </p>

              {challenge.latitude !== null &&
                challenge.longitude !== null && (
                  <div className="coordinates">
                    {challenge.latitude.toFixed(6)},{" "}
                    {challenge.longitude.toFixed(6)}
                  </div>
                )}
            </section>
          </aside>
        </div>
      </div>
    </div>
  );
}