import {
  Activity,
  AlertCircle,
  Award,
  CheckCircle2,
  DollarSign,
  FileText,
  Handshake,
  Lightbulb,
  LogOut,
  Rocket,
  Target,
  TrendingUp,
  Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getCurrentUser } from "../../services/authService";
import { dashboardService } from "../../services/dashboardService";

import "./IndustryDashboard.css";


interface IndustryData {
  collaborations: {
    total: number;
    draft: number;
    submitted: number;
    under_review: number;
    accepted: number;
    rejected: number;
  };

  projects: {
    total: number;
    planning: number;
    active: number;
    on_hold: number;
    completed: number;
  };

  milestones: {
    total: number;
    completed: number;
    delayed: number;
    blocked: number;
  };

  deliverables: {
    total: number;
    approved: number;
    rejected: number;
  };

  funding: {
    allocated: number;
    disbursed: number;
    utilized: number;
    refunded: number;
  };

  impact: {
    verified_outcomes: number;
    beneficiaries: number;
    average_project_progress: number;
  };

  reputation: {
    total_points: number;
    contribution_count: number;
  };
}


interface CurrentUser {
  full_name?: string;
  role?: string;
}


export default function IndustryDashboard() {
  const navigate = useNavigate();

  const [user, setUser] =
    useState<CurrentUser | null>(null);

  const [dashboard, setDashboard] =
    useState<IndustryData | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [currentUser, industryDashboard] =
          await Promise.all([
            getCurrentUser(),
            dashboardService.getIndustryDashboard(),
          ]);

        setUser(currentUser);

        setDashboard(industryDashboard);

        localStorage.setItem(
          "user",
          JSON.stringify(currentUser)
        );
      } catch (err: any) {
        console.error(err);

        if (err.response?.status === 401) {
          handleLogout();
          return;
        }

        setError(
          err.response?.data?.detail ||
            "Unable to load industry dashboard."
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

    navigate("/login", {
      replace: true,
    });
  }


  if (loading) {
    return (
      <main className="industry-page">
        <div className="industry-loading">
          <div className="industry-spinner" />
          Loading industry dashboard...
        </div>
      </main>
    );
  }


  if (error || !dashboard) {
    return (
      <main className="industry-page">
        <div className="industry-error">

          <AlertCircle size={22} />

          <div>
            <strong>
              Unable to load dashboard
            </strong>

            <p>
              {error ||
                "Industry dashboard data is unavailable."}
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


  const collaborations =
    dashboard.collaborations || {};

  const projects =
    dashboard.projects || {};

  const milestones =
    dashboard.milestones || {};

  const deliverables =
    dashboard.deliverables || {};

  const funding =
    dashboard.funding || {};

  const reputation =
    dashboard.reputation || {};

  const impact =
    dashboard.impact || {};


  const totalFunding =
    funding.allocated ?? 0;


  return (
    <main className="industry-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="industry-header">

        <div className="industry-header-inner">

          <button
            className="industry-brand"
            onClick={() => navigate("/")}
          >

            <div className="industry-brand-icon">
              <Rocket size={20} />
            </div>

            <div>
              <strong>
                Societal Innovation Platform
              </strong>

              <span>
                Industry Innovation Workspace
              </span>
            </div>

          </button>


          <div className="industry-header-actions">

            <div className="industry-user">

              <div className="industry-avatar">
                <Users size={17} />
              </div>

              <div className="industry-user-info">

                <strong>
                  {user?.full_name ||
                    "Industry User"}
                </strong>

                <span>
                  {user?.role?.replaceAll(
                    "_",
                    " "
                  )}
                </span>

              </div>

            </div>


            <button
              className="industry-logout"
              onClick={handleLogout}
              title="Logout"
            >
              <LogOut size={18} />
            </button>

          </div>

        </div>

      </header>


      <div className="industry-container">

        {/* =================================================
            HERO
        ================================================= */}

        <section className="industry-hero">

          <div>

            <span className="industry-eyebrow">
              INDUSTRY PORTAL
            </span>

            <h1>
              Turn innovation into
              <span> deployment.</span>
            </h1>

            <p>
              Discover university solutions, support
              high-impact projects, provide funding and
              mentorship, and help deploy innovations in
              the real world.
            </p>

          </div>


          <div className="industry-hero-actions">

            <div className="industry-live-status">
              <span />
              Industry participation active
            </div>

            {/* =================================================
                COLLABORATION OPPORTUNITIES
            ================================================= */}

            <button
              type="button"
              className="industry-opportunities-button"
              onClick={() =>
                navigate(
                  "/industry/opportunities"
                )
              }
            >
              <FileText size={18} />
              Collaboration Opportunities
            </button>

            <button
              type="button"
              className="industry-my-collabs-button"
              onClick={() =>
                navigate(
                  "/industry/collaborations"
                )
              }
            >
              <Handshake size={18} />
              My Collaborations
            </button>

          </div>

        </section>


        {/* =================================================
            KPI CARDS
        ================================================= */}

        <section className="industry-kpis">

          <MetricCard
            icon={<Handshake size={20} />}
            label="Collaborations"
            value={collaborations.total ?? 0}
            detail={`${collaborations.accepted ?? 0} accepted`}
          />

          <MetricCard
            icon={<Activity size={20} />}
            label="Active Projects"
            value={projects.active ?? 0}
            detail={`${projects.total ?? 0} total projects`}
          />

          <MetricCard
            icon={<DollarSign size={20} />}
            label="Funding"
            value={`₹${formatAmount(totalFunding)}`}
            detail={`${formatAmount(
              funding.disbursed ?? 0
            )} disbursed`}
          />

          <MetricCard
            icon={<Target size={20} />}
            label="Progress"
            value={`${impact.average_project_progress ?? 0}%`}
            detail="Average project progress"
          />

          <MetricCard
            icon={<Award size={20} />}
            label="Reputation"
            value={reputation.total_points ?? 0}
            detail={`${reputation.contribution_count ?? 0} contributions`}
          />

        </section>


        {/* =================================================
            MAIN GRID
        ================================================= */}

        <section className="industry-grid">

          {/* -----------------------------------------------
              COLLABORATION PIPELINE
          ------------------------------------------------ */}

          <Panel
            title="Collaboration Pipeline"
            subtitle="Industry participation across proposals"
            icon={<Handshake size={18} />}
          >

            <PipelineRow
              label="Total"
              value={collaborations.total ?? 0}
            />

            <PipelineRow
              label="Submitted"
              value={collaborations.submitted ?? 0}
            />

            <PipelineRow
              label="Under Review"
              value={
                collaborations.under_review ?? 0
              }
            />

            <PipelineRow
              label="Accepted"
              value={
                collaborations.accepted ?? 0
              }
              success
            />

            <PipelineRow
              label="Rejected"
              value={
                collaborations.rejected ?? 0
              }
              danger
            />

          </Panel>


          {/* -----------------------------------------------
              PROJECT EXECUTION
          ------------------------------------------------ */}

          <Panel
            title="Project Execution"
            subtitle="Current industry-supported projects"
            icon={<Rocket size={18} />}
          >

            <PipelineRow
              label="Planning"
              value={projects.planning ?? 0}
            />

            <PipelineRow
              label="Active"
              value={projects.active ?? 0}
            />

            <PipelineRow
              label="On Hold"
              value={projects.on_hold ?? 0}
            />

            <PipelineRow
              label="Completed"
              value={projects.completed ?? 0}
              success
            />

            <PipelineRow
              label="Milestones Completed"
              value={milestones.completed ?? 0}
              success
            />

            <PipelineRow
              label="Delayed Milestones"
              value={milestones.delayed ?? 0}
              danger
            />

          </Panel>


          {/* -----------------------------------------------
              FUNDING + IMPACT
          ------------------------------------------------ */}

          <Panel
            title="Funding & Impact"
            subtitle="Investment and real-world outcomes"
            icon={<TrendingUp size={18} />}
            wide
          >

            <div className="industry-impact-grid">

              <ImpactCard
                icon={<DollarSign size={18} />}
                label="Committed"
                value={`₹${formatAmount(
                  funding.allocated ?? 0
                )}`}
              />

              <ImpactCard
                icon={<DollarSign size={18} />}
                label="Disbursed"
                value={`₹${formatAmount(
                  funding.disbursed ?? 0
                )}`}
              />

              <ImpactCard
                icon={<Activity size={18} />}
                label="Utilized"
                value={`₹${formatAmount(
                  funding.utilized ?? 0
                )}`}
              />

              <ImpactCard
                icon={<Users size={18} />}
                label="Beneficiaries"
                value={(
                  impact.beneficiaries ?? 0
                ).toLocaleString()}
              />

            </div>


            <div className="industry-progress-section">

              <div className="industry-progress-heading">

                <span>
                  Average Project Progress
                </span>

                <strong>
                  {impact.average_project_progress ??
                    0}
                  %
                </strong>

              </div>

              <div className="industry-progress-track">

                <div
                  className="industry-progress-fill"
                  style={{
                    width: `${Math.min(
                      impact.average_project_progress ??
                        0,
                      100
                    )}%`,
                  }}
                />

              </div>

            </div>

          </Panel>


          {/* -----------------------------------------------
              DELIVERY STATUS
          ------------------------------------------------ */}

          <Panel
            title="Delivery Status"
            subtitle="Solution development and deployment"
            icon={<FileText size={18} />}
            wide
          >

            <div className="delivery-grid">

              <DeliveryCard
                label="Total Deliverables"
                value={deliverables.total ?? 0}
                icon={<FileText size={18} />}
              />

              <DeliveryCard
                label="Approved"
                value={deliverables.approved ?? 0}
                icon={<CheckCircle2 size={18} />}
              />

              <DeliveryCard
                label="Rejected"
                value={deliverables.rejected ?? 0}
                icon={<AlertCircle size={18} />}
              />

            </div>

          </Panel>


          {/* -----------------------------------------------
              INDUSTRY ROLE
          ------------------------------------------------ */}

          <Panel
            title="Industry Contribution"
            subtitle="How industry participates in innovation"
            icon={<Lightbulb size={18} />}
            wide
          >

            <div className="contribution-grid">

              <ContributionCard
                icon={<DollarSign size={20} />}
                title="Funding"
                description="Provide financial support for research, pilots and deployment."
              />

              <ContributionCard
                icon={<Users size={20} />}
                title="Technical Mentorship"
                description="Connect university teams with industry experts and engineers."
              />

              <ContributionCard
                icon={<Rocket size={20} />}
                title="Pilot Deployment"
                description="Help transform prototypes into field-tested solutions."
              />

              <ContributionCard
                icon={<TrendingUp size={20} />}
                title="Commercialization"
                description="Support scaling and adoption of successful innovations."
              />

            </div>

          </Panel>


          {/* -----------------------------------------------
              COLLABORATION CTA
          ------------------------------------------------ */}

          <Panel
            title="Find New Opportunities"
            subtitle="Support shortlisted university innovations"
            icon={<Handshake size={18} />}
            wide
          >

            <div className="industry-opportunity-cta">

              <div>
                <strong>
                  Discover shortlisted university proposals
                </strong>

                <p>
                  Review solutions selected for industry
                  collaboration and offer funding,
                  mentorship, technology or deployment
                  support.
                </p>
              </div>

              <button
                type="button"
                className="industry-opportunities-button"
                onClick={() =>
                  navigate(
                    "/industry/opportunities"
                  )
                }
              >
                <FileText size={18} />
                Browse Opportunities
              </button>

            </div>

          </Panel>

        </section>

      </div>

    </main>
  );
}


/* ============================================================
   COMPONENTS
============================================================ */

function MetricCard({
  icon,
  label,
  value,
  detail,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  detail: string;
}) {
  return (
    <div className="industry-metric">

      <div className="industry-metric-icon">
        {icon}
      </div>

      <div>

        <span>{label}</span>

        <strong>
          {typeof value === "number"
            ? value.toLocaleString()
            : value}
        </strong>

        <small>{detail}</small>

      </div>

    </div>
  );
}


function Panel({
  title,
  subtitle,
  icon,
  children,
  wide = false,
}: {
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  wide?: boolean;
}) {
  return (
    <section
      className={`industry-panel${
        wide
          ? " industry-panel-wide"
          : ""
      }`}
    >

      <div className="industry-panel-header">

        <div className="industry-panel-icon">
          {icon}
        </div>

        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>

      </div>

      <div className="industry-panel-body">
        {children}
      </div>

    </section>
  );
}


function PipelineRow({
  label,
  value,
  success = false,
  danger = false,
}: {
  label: string;
  value: number;
  success?: boolean;
  danger?: boolean;
}) {
  return (
    <div className="industry-pipeline-row">

      <div>
        <span
          className={`industry-pipeline-dot ${
            success
              ? "success"
              : danger
                ? "danger"
                : ""
          }`}
        />

        <span>{label}</span>
      </div>

      <strong>{value}</strong>

    </div>
  );
}


function ImpactCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}) {
  return (
    <div className="industry-impact-card">

      <div className="industry-impact-icon">
        {icon}
      </div>

      <span>{label}</span>

      <strong>{value}</strong>

    </div>
  );
}


function DeliveryCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {
  return (
    <div className="industry-delivery-card">

      <div className="industry-delivery-icon">
        {icon}
      </div>

      <span>{label}</span>

      <strong>{value}</strong>

    </div>
  );
}


function ContributionCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="industry-contribution-card">

      <div className="industry-contribution-icon">
        {icon}
      </div>

      <div>

        <strong>{title}</strong>

        <p>{description}</p>

      </div>

    </div>
  );
}


function formatAmount(amount: number) {
  if (!amount) {
    return "0";
  }

  if (amount >= 10000000) {
    return `${(amount / 10000000).toFixed(1)} Cr`;
  }

  if (amount >= 100000) {
    return `${(amount / 100000).toFixed(1)} L`;
  }

  if (amount >= 1000) {
    return `${(amount / 1000).toFixed(1)} K`;
  }

  return amount.toLocaleString();
}