import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Clock3,
  Eye,
  Filter,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  challengeService,
  type Challenge,
} from "../../services/challengeService";

import "./HumanReviewQueuePage.css";


export default function HumanReviewQueuePage() {
  const navigate = useNavigate();

  const [reviews, setReviews] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [urgency, setUrgency] = useState("ALL");


  async function loadQueue(showRefresh = false) {
    try {
      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const data =
        await challengeService.getReviewQueue();

      setReviews(data);
    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to load the human review queue.",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }


  useEffect(() => {
    loadQueue();
  }, []);


  const filteredReviews = useMemo(() => {
    const query = search
      .trim()
      .toLowerCase();

    return reviews.filter((challenge) => {
      const matchesSearch =
        !query ||
        challenge.title
          ?.toLowerCase()
          .includes(query) ||
        challenge.description
          ?.toLowerCase()
          .includes(query) ||
        challenge.category
          ?.toLowerCase()
          .includes(query) ||
        challenge.district
          ?.toLowerCase()
          .includes(query);

      const matchesUrgency =
        urgency === "ALL" ||
        challenge.urgency === urgency;

      return (
        matchesSearch &&
        matchesUrgency
      );
    });
  }, [reviews, search, urgency]);


  const criticalCount = reviews.filter(
    (challenge) =>
      challenge.urgency === "CRITICAL",
  ).length;


  const highCount = reviews.filter(
    (challenge) =>
      challenge.urgency === "HIGH",
  ).length;


  const innovationCount = reviews.filter(
    (challenge) =>
      challenge.innovation_required,
  ).length;


  return (
    <main className="review-queue-page">

      <header className="review-queue-header">

        <div>
          <span className="review-eyebrow">
            HUMAN-IN-THE-LOOP
          </span>

          <h1>
            Human Review Queue
          </h1>

          <p>
            Review ambiguous AI decisions before
            official routing and authority assignment.
          </p>
        </div>


        <div className="review-header-actions">

          <button
            className="review-back-button"
            onClick={() =>
              navigate("/government/dashboard")
            }
          >
            Dashboard
          </button>

          <button
            className="review-refresh-button"
            onClick={() => loadQueue(true)}
            disabled={refreshing}
          >
            <RefreshCw
              size={16}
              className={
                refreshing
                  ? "refresh-spinning"
                  : ""
              }
            />

            Refresh
          </button>

        </div>

      </header>


      <div className="review-queue-container">

        {/* Summary */}

        <section className="review-summary">

          <SummaryCard
            icon={<ShieldCheck size={19} />}
            label="Awaiting Review"
            value={reviews.length}
          />

          <SummaryCard
            icon={<AlertCircle size={19} />}
            label="Critical"
            value={criticalCount}
            danger
          />

          <SummaryCard
            icon={<Clock3 size={19} />}
            label="High Urgency"
            value={highCount}
            warning
          />

          <SummaryCard
            icon={<Sparkles size={19} />}
            label="Innovation"
            value={innovationCount}
            info
          />

        </section>


        {/* Filters */}

        <section className="review-toolbar">

          <div className="review-search">

            <Search size={17} />

            <input
              placeholder="Search challenge, category or district..."
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value,
                )
              }
            />

          </div>


          <div className="review-filter">

            <Filter size={15} />

            <select
              value={urgency}
              onChange={(event) =>
                setUrgency(
                  event.target.value,
                )
              }
            >
              <option value="ALL">
                All urgency
              </option>

              <option value="CRITICAL">
                Critical
              </option>

              <option value="HIGH">
                High
              </option>

              <option value="MEDIUM">
                Medium
              </option>

              <option value="LOW">
                Low
              </option>
            </select>

          </div>

        </section>


        {error && (
          <div className="review-error">

            <AlertCircle size={18} />

            <span>{error}</span>

            <button
              onClick={() => loadQueue()}
            >
              Retry
            </button>

          </div>
        )}


        {/* Queue */}

        <section className="review-queue-card">

          <div className="review-queue-card-header">

            <div>
              <h2>
                Pending Human Decisions
              </h2>

              <span>
                {filteredReviews.length} challenges
              </span>
            </div>

          </div>


          {loading ? (

            <div className="review-loading">

              <div className="review-spinner" />

              Loading review queue...

            </div>

          ) : filteredReviews.length === 0 ? (

            <div className="review-empty">

              <CheckCircle2 size={28} />

              <strong>
                No pending reviews
              </strong>

              <span>
                All currently eligible challenges
                have been reviewed.
              </span>

            </div>

          ) : (

            <div className="review-list">

              {filteredReviews.map(
                (challenge) => (

                  <article
                    className="review-item"
                    key={challenge.id}
                  >

                    <div className="review-item-main">

                      <div className="review-item-title-row">

                        <span className="review-challenge-id">
                          CH-{challenge.id}
                        </span>

                        <UrgencyBadge
                          urgency={
                            challenge.urgency
                          }
                        />

                      </div>


                      <h3>
                        {challenge.title}
                      </h3>


                      <p>
                        {truncate(
                          challenge.description,
                          170,
                        )}
                      </p>


                      <div className="review-meta">

                        <span>
                          Category:{" "}
                          <strong>
                            {formatValue(
                              challenge.category,
                            )}
                          </strong>
                        </span>

                        <span>
                          Location:{" "}
                          <strong>
                            {challenge.district ||
                              "Unknown"}
                          </strong>
                        </span>

                        <span>
                          AI confidence:{" "}
                          <strong>
                            {formatConfidence(
                              challenge.ai_confidence_score,
                            )}
                          </strong>
                        </span>

                      </div>

                    </div>


                    <div className="review-decision">

                      <div className="review-reason">

                        <Sparkles
                          size={15}
                        />

                        <span>
                          {getReviewReason(
                            challenge,
                          )}
                        </span>

                      </div>


                      {challenge.ai_category_decision && (
                        <span className="decision-pill">
                          {formatValue(
                            challenge.ai_category_decision,
                          )}
                        </span>
                      )}


                      <button
                        className="review-open-button"
                        onClick={() =>
                          navigate(
                            `/government/challenges/${challenge.id}`,
                          )
                        }
                      >
                        <Eye size={15} />
                        Review
                        <ArrowRight
                          size={15}
                        />
                      </button>

                    </div>

                  </article>

                ),
              )}

            </div>

          )}

        </section>

      </div>

    </main>
  );
}


function SummaryCard({
  icon,
  label,
  value,
  danger = false,
  warning = false,
  info = false,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  danger?: boolean;
  warning?: boolean;
  info?: boolean;
}) {
  return (
    <div className="review-summary-card">

      <div
        className={`review-summary-icon ${
          danger
            ? "danger"
            : warning
            ? "warning"
            : info
            ? "info"
            : ""
        }`}
      >
        {icon}
      </div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>

    </div>
  );
}


function UrgencyBadge({
  urgency,
}: {
  urgency: string;
}) {
  return (
    <span
      className={`review-urgency review-urgency-${urgency.toLowerCase()}`}
    >
      {urgency}
    </span>
  );
}


function getReviewReason(
  challenge: Challenge,
) {
  if (
    challenge.ai_category_margin != null &&
    challenge.ai_category_margin < 0.05
  ) {
    return "Low category confidence margin";
  }

  if (
    challenge.ai_innovation_requires_human_review
  ) {
    return "Innovation decision requires review";
  }

  if (
    challenge.ai_innovation_type_requires_human_review
  ) {
    return "Innovation type requires review";
  }

  return "AI decision requires human validation";
}


function formatValue(
  value?: string | null,
) {
  if (!value) {
    return "—";
  }

  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) =>
      character.toUpperCase(),
    );
}


function formatConfidence(
  value?: number | null,
) {
  if (value == null) {
    return "—";
  }

  return `${(value * 100).toFixed(1)}%`;
}


function truncate(
  value: string,
  length: number,
) {
  if (value.length <= length) {
    return value;
  }

  return `${value.slice(0, length)}...`;
}