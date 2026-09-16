import {
  AlertCircle,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  Clock3,
  FolderKanban,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getProjects,
  type Project,
  type ProjectHealth,
  type ProjectStatus,
} from "../../services/projectService";

import "./ProjectPages.css";

type StatusFilter = "ALL" | ProjectStatus;
type HealthFilter = "ALL" | ProjectHealth;

function formatDate(value: string | null): string {
  if (!value) return "Not specified";

  return new Date(value).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatBudget(value: number | null): string {
  if (value === null || value === undefined) {
    return "Not specified";
  }

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function getStatusLabel(status: ProjectStatus): string {
  return status.replaceAll("_", " ");
}

function getHealthLabel(health: ProjectHealth): string {
  return health.replaceAll("_", " ");
}

function statusClass(status: ProjectStatus): string {
  return status.toLowerCase().replaceAll("_", "-");
}

function healthClass(health: ProjectHealth): string {
  return health.toLowerCase().replaceAll("_", "-");
}

export default function ProjectsPage() {
  const navigate = useNavigate();

  const [projects, setProjects] = useState<Project[]>([]);
  const [statusFilter, setStatusFilter] =
    useState<StatusFilter>("ALL");
  const [healthFilter, setHealthFilter] =
    useState<HealthFilter>("ALL");

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadProjects = useCallback(async (isRefresh = false) => {
    try {
      setError("");

      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      const data = await getProjects();
      setProjects(data);
    } catch (err) {
      console.error("Failed to load projects:", err);
      setError(
        "Unable to load projects. Please check the backend connection and try again."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void loadProjects();
  }, [loadProjects]);

  const filteredProjects = useMemo(() => {
    return projects.filter((project) => {
      const statusMatch =
        statusFilter === "ALL" ||
        project.status === statusFilter;

      const healthMatch =
        healthFilter === "ALL" ||
        project.health === healthFilter;

      return statusMatch && healthMatch;
    });
  }, [projects, statusFilter, healthFilter]);

  const summary = useMemo(() => {
    return {
      total: projects.length,
      planning: projects.filter(
        (project) => project.status === "PLANNING"
      ).length,
      active: projects.filter(
        (project) => project.status === "ACTIVE"
      ).length,
      completed: projects.filter(
        (project) => project.status === "COMPLETED"
      ).length,
      risks: projects.filter(
        (project) =>
          project.health === "AT_RISK" ||
          project.health === "DELAYED" ||
          project.health === "CRITICAL"
      ).length,
    };
  }, [projects]);

  if (loading) {
    return (
      <div className="project-page">
        <div className="project-loading">
          <Loader2 className="spin" size={28} />
          <p>Loading project portfolio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="project-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="project-page-header">
        <div>
          <div className="project-eyebrow">
            PROJECT EXECUTION
          </div>

          <h1>Projects</h1>

          <p>
            Monitor societal innovation projects from
            planning through deployment and impact.
          </p>
        </div>

        <button
          type="button"
          className="project-secondary-button"
          onClick={() => void loadProjects(true)}
          disabled={refreshing}
        >
          <RefreshCw
            size={16}
            className={refreshing ? "spin" : ""}
          />
          Refresh
        </button>
      </div>

      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="project-error-banner">
          <AlertCircle size={18} />
          <span>{error}</span>

          <button
            type="button"
            onClick={() => void loadProjects(true)}
          >
            Retry
          </button>
        </div>
      )}

      {/* =====================================================
          SUMMARY
      ===================================================== */}

      <div className="project-summary-grid">

        <div className="project-summary-card">
          <div className="project-summary-icon">
            <FolderKanban size={20} />
          </div>

          <div>
            <span>Total Projects</span>
            <strong>{summary.total}</strong>
          </div>
        </div>

        <div className="project-summary-card">
          <div className="project-summary-icon">
            <Clock3 size={20} />
          </div>

          <div>
            <span>Planning</span>
            <strong>{summary.planning}</strong>
          </div>
        </div>

        <div className="project-summary-card">
          <div className="project-summary-icon">
            <ArrowRight size={20} />
          </div>

          <div>
            <span>Active</span>
            <strong>{summary.active}</strong>
          </div>
        </div>

        <div className="project-summary-card">
          <div className="project-summary-icon">
            <CheckCircle2 size={20} />
          </div>

          <div>
            <span>Completed</span>
            <strong>{summary.completed}</strong>
          </div>
        </div>

        <div className="project-summary-card">
          <div className="project-summary-icon">
            <AlertCircle size={20} />
          </div>

          <div>
            <span>Needs Attention</span>
            <strong>{summary.risks}</strong>
          </div>
        </div>

      </div>

      {/* =====================================================
          FILTERS
      ===================================================== */}

      <div className="project-filter-panel">

        <div>
          <span className="project-filter-label">
            Status
          </span>

          <div className="project-filter-group">
            {(
              [
                "ALL",
                "PLANNING",
                "ACTIVE",
                "ON_HOLD",
                "COMPLETED",
                "CANCELLED",
              ] as StatusFilter[]
            ).map((status) => (
              <button
                key={status}
                type="button"
                className={
                  statusFilter === status
                    ? "project-filter-button active"
                    : "project-filter-button"
                }
                onClick={() => setStatusFilter(status)}
              >
                {status === "ALL"
                  ? "All"
                  : getStatusLabel(status)}
              </button>
            ))}
          </div>
        </div>

        <div>
          <span className="project-filter-label">
            Health
          </span>

          <div className="project-filter-group">
            {(
              [
                "ALL",
                "ON_TRACK",
                "AT_RISK",
                "DELAYED",
                "CRITICAL",
              ] as HealthFilter[]
            ).map((health) => (
              <button
                key={health}
                type="button"
                className={
                  healthFilter === health
                    ? "project-filter-button active"
                    : "project-filter-button"
                }
                onClick={() => setHealthFilter(health)}
              >
                {health === "ALL"
                  ? "All"
                  : getHealthLabel(health)}
              </button>
            ))}
          </div>
        </div>

      </div>

      {/* =====================================================
          PROJECT LIST
      ===================================================== */}

      {filteredProjects.length === 0 ? (
        <div className="project-empty-state">
          <FolderKanban size={36} />

          <h3>No projects found</h3>

          <p>
            There are no projects matching the selected
            filters.
          </p>
        </div>
      ) : (
        <div className="project-card-grid">

          {filteredProjects.map((project) => (
            <article
              key={project.id}
              className="project-card"
            >
              <div className="project-card-top">

                <div>
                  <span className="project-card-id">
                    PROJECT #{project.id}
                  </span>

                  <h2>{project.title}</h2>
                </div>

                <span
                  className={`project-status-badge ${statusClass(
                    project.status
                  )}`}
                >
                  {getStatusLabel(project.status)}
                </span>

              </div>

              <p className="project-card-description">
                {project.description ||
                  "No project description available."}
              </p>

              <div className="project-progress-block">

                <div className="project-progress-header">
                  <span>Execution Progress</span>
                  <strong>
                    {Math.round(
                      project.progress_percentage
                    )}
                    %
                  </strong>
                </div>

                <div className="project-progress-track">
                  <div
                    className="project-progress-fill"
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(
                          0,
                          project.progress_percentage
                        )
                      )}%`,
                    }}
                  />
                </div>

              </div>

              <div className="project-card-meta">

                <div>
                  <span>Health</span>
                  <strong
                    className={`project-health-text ${healthClass(
                      project.health
                    )}`}
                  >
                    {getHealthLabel(project.health)}
                  </strong>
                </div>

                <div>
                  <span>Budget</span>
                  <strong>
                    {formatBudget(
                      project.total_budget
                    )}
                  </strong>
                </div>

                <div>
                  <span>Target</span>
                  <strong>
                    {formatDate(
                      project.target_completion_date
                    )}
                  </strong>
                </div>

              </div>

              <div className="project-card-footer">

                <div className="project-date">
                  <CalendarDays size={15} />

                  <span>
                    Started{" "}
                    {formatDate(project.start_date)}
                  </span>
                </div>

                <button
                  type="button"
                  className="project-primary-button"
                  onClick={() =>
                    navigate(
                      `/government/projects/${project.id}`
                    )
                  }
                >
                  Open Project
                  <ArrowRight size={16} />
                </button>

              </div>
            </article>
          ))}

        </div>
      )}
    </div>
  );
}