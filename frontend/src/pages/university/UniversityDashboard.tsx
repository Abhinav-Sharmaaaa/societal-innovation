import {
  AlertCircle,
  Award,
  BarChart3,
  CheckCircle2,
  FileCheck2,
  FileText,
  Lightbulb,
  LogOut,
  MessageSquare,
  Target,
  TrendingUp,
  Users,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getCurrentUser } from "../../services/authService";
import {
  dashboardService,
  type ActionCenter,
  type UniversityDashboard as UniversityDashboardData,
} from "../../services/dashboardService";

import type { User } from "../../types/auth";

import "./UniversityDashboard.css";


interface DashboardState {
  dashboard: UniversityDashboardData | null;
  actionCenter: ActionCenter | null;
}


export default function UniversityDashboard() {
  const navigate = useNavigate();

  const [user, setUser] = useState<User | null>(null);

  const [data, setData] = useState<DashboardState>({
    dashboard: null,
    actionCenter: null,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [
          currentUser,
          dashboard,
          actionCenter,
        ] = await Promise.all([
          getCurrentUser(),
          dashboardService.getUniversityDashboard(),
          dashboardService.getActionCenter(),
        ]);

        setUser(currentUser);

        setData({
          dashboard,
          actionCenter,
        });

        localStorage.setItem(
          "user",
          JSON.stringify(currentUser)
        );
      } catch (requestError: any) {
        console.error(requestError);

        if (requestError.response?.status === 401) {
          handleLogout();
          return;
        }

        setError(
          requestError.response?.data?.detail ||
            "Unable to load the university dashboard."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);


  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");

    navigate("/login");
  }


  const dashboard = data.dashboard;


  const pendingItems = useMemo(() => {
    if (!dashboard) {
      return 0;
    }

    return (
      dashboard.invitations.total -
      dashboard.invitations.declined -
      dashboard.invitations.proposal_submitted
    );
  }, [dashboard]);


  if (loading) {
    return (
      <main className="university-page">
        <div className="university-loading">
          <div className="university-spinner" />
          Loading university dashboard...
        </div>
      </main>
    );
  }


  if (error || !dashboard) {
    return (
      <main className="university-page">
        <div className="university-error">
          <AlertCircle size={23} />

          <div>
            <strong>
              Unable to load dashboard
            </strong>

            <p>
              {error ||
                "University dashboard data is unavailable."}
            </p>
          </div>

          <button
            onClick={() =>
              window.location.reload()
            }
          >
            Retry
          </button>
        </div>
      </main>
    );
  }


  return (
    <main className="university-page">

      {/* ====================================================
          Header
      ==================================================== */}

      <header className="university-header">

        <div className="university-header-inner">

          <button
            className="university-brand"
            onClick={() => navigate("/")}
          >
            <div className="university-brand-icon">
              <Lightbulb size={20} />
            </div>

            <div>
              <strong>
                Societal Innovation Platform
              </strong>

              <span>
                University Innovation Workspace
              </span>
            </div>
          </button>


          <div className="university-header-actions">

            <div className="university-user">

              <div className="university-user-avatar">
                <Users size={17} />
              </div>

              <div className="university-user-info">
                <strong>
                  {user?.full_name ||
                    "University User"}
                </strong>

                <span>
                  {user?.role?.replaceAll("_", " ")}
                </span>
              </div>

            </div>


            <button
              className="university-logout"
              onClick={handleLogout}
              title="Logout"
            >
              <LogOut size={18} />
            </button>

          </div>

        </div>

      </header>


      {/* ====================================================
          Main
      ==================================================== */}

      <div className="university-container">

        {/* --------------------------------------------------
            Hero
        -------------------------------------------------- */}

        <section className="university-hero">

          <div>

            <span className="university-eyebrow">
              UNIVERSITY PORTAL
            </span>

            <h1>
              Turn research into
              <span> real-world impact.</span>
            </h1>

            <p>
              Discover societal challenges, submit proposals,
              collaborate with industry, execute projects,
              and measure outcomes.
            </p>

          </div>


          <div className="university-hero-actions">

            <div className="university-status">
              <span className="status-dot-live" />
              Ecosystem participation active
            </div>

            {/* ====================================================
                NEW: RFP Invitations Button
            ==================================================== */}

            <button
              type="button"
              className="university-rfp-button"
              onClick={() =>
                navigate("/university/invitations")
              }
            >
              <FileText size={18} />
              View RFP Invitations
            </button>

          </div>

        </section>


        {/* --------------------------------------------------
            KPI Cards
        -------------------------------------------------- */}

        <section className="university-kpis">

          <MetricCard
            icon={<MailIcon />}
            label="Invitations"
            value={dashboard.invitations.total}
            detail={`${pendingItems} requiring attention`}
          />

          <MetricCard
            icon={<FileText size={20} />}
            label="Proposals"
            value={dashboard.proposals.total}
            detail={`${dashboard.proposals.shortlisted} shortlisted`}
          />

          <MetricCard
            icon={<MessageSquare size={20} />}
            label="Collaborations"
            value={dashboard.industry_collaboration.total}
            detail={`${dashboard.industry_collaboration.accepted} accepted`}
          />

          <MetricCard
            icon={<Target size={20} />}
            label="Projects"
            value={dashboard.projects.total}
            detail={`${dashboard.projects.active} active`}
          />

          <MetricCard
            icon={<Award size={20} />}
            label="Reputation"
            value={dashboard.reputation.total_points}
            detail={`${dashboard.reputation.contribution_count} contributions`}
          />

        </section>


        {/* --------------------------------------------------
            Pipeline
        -------------------------------------------------- */}

        <section className="university-grid">

          <DashboardPanel
            title="Opportunity Pipeline"
            subtitle="From invitations to collaboration"
            icon={<BarChart3 size={18} />}
          >

            <PipelineRow
              label="Invitations"
              value={dashboard.invitations.total}
              tone="neutral"
            />

            <PipelineRow
              label="Interested"
              value={dashboard.invitations.interested}
              tone="info"
            />

            <PipelineRow
              label="Proposals Submitted"
              value={dashboard.proposals.submitted}
              tone="progress"
            />

            <PipelineRow
              label="Under Evaluation"
              value={dashboard.proposals.under_evaluation}
              tone="warning"
            />

            <PipelineRow
              label="Shortlisted"
              value={dashboard.proposals.shortlisted}
              tone="success"
            />

            <PipelineRow
              label="Industry Accepted"
              value={dashboard.industry_collaboration.accepted}
              tone="success"
            />

          </DashboardPanel>


          <DashboardPanel
            title="Project Execution"
            subtitle="Current research implementation"
            icon={<Target size={18} />}
          >

            <PipelineRow
              label="Planning"
              value={dashboard.projects.planning}
              tone="neutral"
            />

            <PipelineRow
              label="Active"
              value={dashboard.projects.active}
              tone="progress"
            />

            <PipelineRow
              label="On Hold"
              value={dashboard.projects.on_hold}
              tone="warning"
            />

            <PipelineRow
              label="Completed"
              value={dashboard.projects.completed}
              tone="success"
            />

            <PipelineRow
              label="Milestones Completed"
              value={dashboard.milestones.completed}
              tone="success"
            />

            <PipelineRow
              label="Milestones Delayed"
              value={dashboard.milestones.delayed}
              tone="danger"
            />

          </DashboardPanel>


          {/* --------------------------------------------------
              Progress
          -------------------------------------------------- */}

          <DashboardPanel
            title="Research Progress"
            subtitle="Overall project execution"
            icon={<TrendingUp size={18} />}
            wide
          >

            <div className="progress-overview">

              <div className="progress-score">
                <strong>
                  {dashboard.impact.average_project_progress}%
                </strong>

                <span>
                  Average project progress
                </span>
              </div>

              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{
                    width: `${Math.min(
                      dashboard.impact
                        .average_project_progress,
                      100
                    )}%`,
                  }}
                />
              </div>

            </div>


            <div className="research-stats">

              <ResearchStat
                icon={<FileCheck2 size={18} />}
                label="Approved Deliverables"
                value={
                  dashboard.deliverables.approved
                }
              />

              <ResearchStat
                icon={<AlertCircle size={18} />}
                label="Rejected Deliverables"
                value={
                  dashboard.deliverables.rejected
                }
              />

              <ResearchStat
                icon={<CheckCircle2 size={18} />}
                label="Verified Outcomes"
                value={
                  dashboard.impact.verified_outcomes
                }
              />

              <ResearchStat
                icon={<Users size={18} />}
                label="Beneficiaries"
                value={
                  dashboard.impact.beneficiaries
                }
              />

            </div>

          </DashboardPanel>


          {/* --------------------------------------------------
              Action Center
          -------------------------------------------------- */}

          <DashboardPanel
            title="Action Center"
            subtitle="Items requiring your attention"
            icon={<AlertCircle size={18} />}
            wide
          >

            {!data.actionCenter ||
            data.actionCenter.notifications.length === 0 ? (

              <div className="university-empty">
                <CheckCircle2 size={22} />

                <span>
                  No pending actions.
                </span>
              </div>

            ) : (

              <div className="university-actions">

                {data.actionCenter.notifications
                  .slice(0, 8)
                  .map((notification) => (

                    <div
                      className={`university-action university-action-${notification.priority.toLowerCase()}`}
                      key={notification.id}
                    >

                      <div className="university-action-icon">
                        <AlertCircle size={17} />
                      </div>

                      <div>
                        <strong>
                          {notification.title}
                        </strong>

                        <p>
                          {notification.message}
                        </p>
                      </div>

                    </div>

                  ))}

              </div>

            )}

          </DashboardPanel>

        </section>

      </div>

    </main>
  );
}


/* ============================================================
   COMPONENTS
   ============================================================ */

function MailIcon() {
  return <FileText size={20} />;
}


interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  detail: string;
}


function MetricCard({
  icon,
  label,
  value,
  detail,
}: MetricCardProps) {

  return (
    <div className="university-metric">

      <div className="university-metric-icon">
        {icon}
      </div>

      <div>
        <span>{label}</span>

        <strong>
          {value.toLocaleString()}
        </strong>

        <small>
          {detail}
        </small>
      </div>

    </div>
  );
}


interface DashboardPanelProps {
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  wide?: boolean;
}


function DashboardPanel({
  title,
  subtitle,
  icon,
  children,
  wide = false,
}: DashboardPanelProps) {

  return (
    <section
      className={`university-panel${
        wide ? " university-panel-wide" : ""
      }`}
    >

      <div className="university-panel-header">

        <div className="university-panel-icon">
          {icon}
        </div>

        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>

      </div>

      <div className="university-panel-body">
        {children}
      </div>

    </section>
  );
}


type PipelineTone =
  | "neutral"
  | "info"
  | "progress"
  | "warning"
  | "success"
  | "danger";


function PipelineRow({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: PipelineTone;
}) {

  return (
    <div className="pipeline-row">

      <div className="pipeline-left">

        <span
          className={`pipeline-dot pipeline-${tone}`}
        />

        <span>
          {label}
        </span>

      </div>

      <strong>
        {value}
      </strong>

    </div>
  );
}


function ResearchStat({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {

  return (
    <div className="research-stat">

      <div className="research-stat-icon">
        {icon}
      </div>

      <div>
        <span>{label}</span>
        <strong>{value.toLocaleString()}</strong>
      </div>

    </div>
  );
}