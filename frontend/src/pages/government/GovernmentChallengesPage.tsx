import {
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Filter,
  Flag,
  Search,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  challengeService,
  type Challenge,
} from "../../services/challengeService";

import "./GovernmentChallengesPage.css";


const statusOptions = [
  "ALL",
  "SUBMITTED",
  "UNDER_REVIEW",
  "ROUTED",
  "IN_PROGRESS",
  "RESOLVED",
  "REJECTED",
  "CLOSED",
];


const urgencyOptions = [
  "ALL",
  "LOW",
  "MEDIUM",
  "HIGH",
  "CRITICAL",
];


export default function GovernmentChallengesPage() {
  const navigate = useNavigate();

  const [challenges, setChallenges] =
    useState<Challenge[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] =
    useState("ALL");

  const [urgencyFilter, setUrgencyFilter] =
    useState("ALL");

  const [innovationOnly, setInnovationOnly] =
    useState(false);


  async function loadChallenges() {
    try {
      setLoading(true);
      setError("");

      const data =
        await challengeService.getChallenges(
          0,
          100,
        );

      setChallenges(data);
    } catch (err: any) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Unable to load challenges.",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadChallenges();
  }, []);


  const filteredChallenges = useMemo(() => {
    const normalizedSearch =
      search.trim().toLowerCase();

    return challenges.filter((challenge) => {

      const matchesSearch =
        !normalizedSearch ||
        challenge.title
          ?.toLowerCase()
          .includes(normalizedSearch) ||
        challenge.description
          ?.toLowerCase()
          .includes(normalizedSearch) ||
        challenge.category
          ?.toLowerCase()
          .includes(normalizedSearch) ||
        challenge.district
          ?.toLowerCase()
          .includes(normalizedSearch);

      const matchesStatus =
        statusFilter === "ALL" ||
        challenge.status === statusFilter;

      const matchesUrgency =
        urgencyFilter === "ALL" ||
        challenge.urgency === urgencyFilter;

      const matchesInnovation =
        !innovationOnly ||
        challenge.innovation_required;

      return (
        matchesSearch &&
        matchesStatus &&
        matchesUrgency &&
        matchesInnovation
      );
    });
  }, [
    challenges,
    search,
    statusFilter,
    urgencyFilter,
    innovationOnly,
  ]);


  const reviewCount =
    challenges.filter(
      (challenge) =>
        challenge.status === "UNDER_REVIEW" ||
        challenge.ai_requires_human_review === true,
    ).length;


  const highPriorityCount =
    challenges.filter(
      (challenge) =>
        challenge.urgency === "HIGH" ||
        challenge.urgency === "CRITICAL",
    ).length;


  const innovationCount =
    challenges.filter(
      (challenge) =>
        challenge.innovation_required,
    ).length;


  return (
    <main className="government-challenges-page">

      {/* ====================================================
          HEADER
      ==================================================== */}

      <header className="government-challenges-header">

        <div>
          <span className="government-page-eyebrow">
            GOVERNMENT OPERATIONS
          </span>

          <h1>
            Challenge Management
          </h1>

          <p>
            Review, route, assign and monitor
            societal challenges across the ecosystem.
          </p>
        </div>

        <button
          className="back-dashboard-button"
          onClick={() =>
            navigate("/government/dashboard")
          }
        >
          Back to Dashboard
        </button>

      </header>


      {/* ====================================================
          SUMMARY
      ==================================================== */}

      <section className="challenge-summary">

        <SummaryCard
          icon={<Flag size={19} />}
          label="Total Challenges"
          value={challenges.length}
        />

        <SummaryCard
          icon={<AlertCircle size={19} />}
          label="Human Review"
          value={reviewCount}
          danger
        />

        <SummaryCard
          icon={<Clock3 size={19} />}
          label="High Priority"
          value={highPriorityCount}
          warning
        />

        <SummaryCard
          icon={<ShieldCheck size={19} />}
          label="Innovation"
          value={innovationCount}
          info
        />

      </section>


      {/* ====================================================
          FILTERS
      ==================================================== */}

      <section className="challenge-toolbar">

        <div className="challenge-search">

          <Search size={17} />

          <input
            type="text"
            placeholder="Search challenge, category or district..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />

        </div>


        <div className="challenge-filter">

          <Filter size={16} />

          <select
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(
                event.target.value,
              )
            }
          >
            {statusOptions.map((status) => (
              <option
                key={status}
                value={status}
              >
                {status === "ALL"
                  ? "All statuses"
                  : status.replaceAll("_", " ")}
              </option>
            ))}
          </select>

        </div>


        <div className="challenge-filter">

          <select
            value={urgencyFilter}
            onChange={(event) =>
              setUrgencyFilter(
                event.target.value,
              )
            }
          >
            {urgencyOptions.map((urgency) => (
              <option
                key={urgency}
                value={urgency}
              >
                {urgency === "ALL"
                  ? "All urgency"
                  : urgency}
              </option>
            ))}
          </select>

        </div>


        <button
          className={`innovation-filter ${
            innovationOnly
              ? "active"
              : ""
          }`}
          onClick={() =>
            setInnovationOnly(
              (value) => !value,
            )
          }
        >
          Innovation only
        </button>

      </section>


      {/* ====================================================
          ERROR
      ==================================================== */}

      {error && (
        <div className="challenge-error">
          <AlertCircle size={19} />

          <span>{error}</span>

          <button onClick={loadChallenges}>
            Retry
          </button>
        </div>
      )}


      {/* ====================================================
          TABLE
      ==================================================== */}

      <section className="challenge-table-card">

        <div className="challenge-table-header">

          <div>
            <h2>
              Societal Challenges
            </h2>

            <span>
              Showing{" "}
              {filteredChallenges.length}{" "}
              of {challenges.length}
            </span>
          </div>

        </div>


        {loading ? (

          <div className="challenge-loading">
            <div className="challenge-spinner" />
            Loading challenges...
          </div>

        ) : filteredChallenges.length === 0 ? (

          <div className="challenge-empty">
            <CheckCircle2 size={26} />

            <strong>
              No challenges found
            </strong>

            <span>
              Try changing your search or filters.
            </span>
          </div>

        ) : (

          <div className="challenge-table-wrapper">

            <table className="challenge-table">

              <thead>
                <tr>
                  <th>ID</th>
                  <th>Challenge</th>
                  <th>Category</th>
                  <th>Location</th>
                  <th>Urgency</th>
                  <th>Status</th>
                  <th />
                </tr>
              </thead>

              <tbody>

                {filteredChallenges.map(
                  (challenge) => (

                    <tr
                      key={challenge.id}
                      onClick={() =>
                        navigate(
                          `/government/challenges/${challenge.id}`,
                        )
                      }
                    >

                      <td>
                        <span className="challenge-id">
                          CH-{challenge.id}
                        </span>
                      </td>


                      <td>
                        <div className="challenge-title-cell">

                          <strong>
                            {challenge.title}
                          </strong>

                          <span>
                            {truncate(
                              challenge.description,
                              90,
                            )}
                          </span>

                          {challenge.innovation_required && (
                            <em>
                              Innovation pathway
                            </em>
                          )}

                        </div>
                      </td>


                      <td>
                        <span className="category-pill">
                          {formatValue(
                            challenge.category,
                          )}
                        </span>
                      </td>


                      <td>
                        <div className="location-cell">
                          <strong>
                            {challenge.district ||
                              "—"}
                          </strong>

                          <span>
                            {challenge.state ||
                              "—"}
                          </span>
                        </div>
                      </td>


                      <td>
                        <UrgencyBadge
                          urgency={
                            challenge.urgency
                          }
                        />
                      </td>


                      <td>
                        <StatusBadge
                          status={
                            challenge.status
                          }
                        />
                      </td>


                      <td>
                        <ChevronRight
                          size={18}
                          className="challenge-row-arrow"
                        />
                      </td>

                    </tr>

                  ),
                )}

              </tbody>

            </table>

          </div>
        )}

      </section>

    </main>
  );
}


/* ============================================================
   COMPONENTS
============================================================ */

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
    <div className="summary-card">

      <div
        className={`summary-icon ${
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


function StatusBadge({
  status,
}: {
  status: string;
}) {
  const className =
    status.toLowerCase();

  return (
    <span
      className={`status-badge status-${className}`}
    >
      {formatValue(status)}
    </span>
  );
}


function UrgencyBadge({
  urgency,
}: {
  urgency: string;
}) {
  return (
    <span
      className={`urgency-badge urgency-${urgency.toLowerCase()}`}
    >
      {urgency}
    </span>
  );
}


function formatValue(value: string) {
  return value
    ?.replaceAll("_", " ")
    .replace(/\b\w/g, (character) =>
      character.toUpperCase(),
    );
}


function truncate(
  value: string | null | undefined,
  length: number,
) {
  if (!value) {
    return "";
  }

  return value.length > length
    ? `${value.slice(0, length)}...`
    : value;
}