import {
    AlertCircle,
    ArrowRight,
    BarChart3,
    Building2,
    CheckCircle2,
    ChevronRight,
    Clock3,
    FileText,
    IndianRupee,
    LogOut,
    MapPin,
    Rocket,
    ShieldAlert,
    ShieldCheck,
    Target,
    TrendingUp,
    Users,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
    dashboardService,
    type ActionCenter,
    type AnalyticsOverview,
    type DistrictAnalytics,
    type GovernmentDashboard as GovernmentDashboardData,
    type IndustryLeaderboardItem,
    type UniversityLeaderboardItem,
} from "../../services/dashboardService";

import { getCurrentUser } from "../../services/authService";
import { listRfps, type RFP } from "../../services/rfpService";
import type { User } from "../../types/auth";

import "./GovernmentDashboard.css";


interface DashboardState {
    dashboard: GovernmentDashboardData | null;
    analytics: AnalyticsOverview | null;
    districts: DistrictAnalytics[];
    universities: UniversityLeaderboardItem[];
    industries: IndustryLeaderboardItem[];
    actionCenter: ActionCenter | null;
}


const initialData: DashboardState = {
    dashboard: null,
    analytics: null,
    districts: [],
    universities: [],
    industries: [],
    actionCenter: null,
};


export default function GovernmentDashboard() {
    const navigate = useNavigate();

    const [user, setUser] = useState<User | null>(null);

    const [data, setData] =
        useState<DashboardState>(initialData);

    const [rfps, setRfps] = useState<RFP[]>([]);

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
                    analytics,
                    districts,
                    universities,
                    industries,
                    actionCenter,
                    rfpList,
                ] = await Promise.all([
                    getCurrentUser(),
                    dashboardService.getGovernmentDashboard(),
                    dashboardService.getAnalyticsOverview(),
                    dashboardService.getDistrictAnalytics(),
                    dashboardService.getUniversityLeaderboard(),
                    dashboardService.getIndustryLeaderboard(),
                    dashboardService.getActionCenter(),
                    listRfps(),
                ]);

                setRfps(rfpList);

                setUser(currentUser);

                setData({
                    dashboard,
                    analytics,
                    districts,
                    universities,
                    industries,
                    actionCenter,
                });

                localStorage.setItem(
                    "user",
                    JSON.stringify(currentUser)
                );
            } catch (requestError: any) {
                console.error(requestError);

                if (
                    requestError.response?.status === 401
                ) {
                    handleLogout();
                    return;
                }

                setError(
                    requestError.response?.data?.detail ||
                        "Unable to load the government dashboard."
                );
            } finally {
                setLoading(false);
            }
        }

        void loadDashboard();
    }, []);


    function handleLogout() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");

        navigate("/login");
    }


    const dashboard = data.dashboard;
    const analytics = data.analytics;


    const topDistricts = useMemo(() => {
        return [...data.districts]
            .sort(
                (a, b) =>
                    b.challenge_count - a.challenge_count
            )
            .slice(0, 6);
    }, [data.districts]);


    const topUniversities = useMemo(() => {
        return data.universities.slice(0, 5);
    }, [data.universities]);


    const topIndustries = useMemo(() => {
        return data.industries.slice(0, 5);
    }, [data.industries]);


    if (loading) {
        return (
            <main className="government-page">

                <div className="government-loading">

                    <div className="loading-spinner" />

                    <span>
                        Loading government dashboard...
                    </span>

                </div>

            </main>
        );
    }


    if (error || !dashboard) {
        return (
            <main className="government-page">

                <div className="government-error">

                    <AlertCircle size={24} />

                    <div>

                        <strong>
                            Unable to load dashboard
                        </strong>

                        <p>
                            {error ||
                                "Government dashboard data is unavailable."}
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
        <main className="government-page">

            {/* ====================================================
                Header
            ==================================================== */}

            <header className="government-header">

                <div className="government-header-inner">

                    <button
                        className="government-brand"
                        onClick={() => navigate("/")}
                    >

                        <div className="government-brand-icon">
                            <BarChart3 size={20} />
                        </div>

                        <div>

                            <strong>
                                Societal Innovation Platform
                            </strong>

                            <span>
                                Government Command Center
                            </span>

                        </div>

                    </button>


                    <div className="government-header-actions">

                        <div className="government-user">

                            <div className="government-user-avatar">
                                <Users size={17} />
                            </div>

                            <div className="government-user-info">

                                <strong>
                                    {user?.full_name ||
                                        "Government Officer"}
                                </strong>

                                <span>
                                    {user?.role?.replaceAll(
                                        "_",
                                        " "
                                    ) ||
                                        "Government"}
                                </span>

                            </div>

                        </div>


                        <button
                            className="government-primary-action"
                            onClick={() =>
                                navigate(
                                    "/government/challenges"
                                )
                            }
                        >
                            Manage Challenges
                            <ArrowRight size={16} />
                        </button>


                        <button
                            className="government-primary-action"
                            onClick={() =>
                                navigate(
                                    "/government/reviews"
                                )
                            }
                        >
                            Human Review Queue
                            <ShieldCheck size={16} />
                        </button>


                        {/* ====================================================
                            NEW: ACCEPTED COLLABORATIONS
                        ==================================================== */}

                        <button
                            className="government-primary-action"
                            onClick={() =>
                                navigate(
                                    "/government/collaborations"
                                )
                            }
                        >
                            Accepted Collaborations
                            <HandshakeIcon />
                        </button>


                        <button
                            className="government-logout"
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

            <div className="government-container">

                {/* --------------------------------------------------
                    Hero
                -------------------------------------------------- */}

                <section className="government-hero">

                    <div>

                        <span className="government-eyebrow">
                            GOVERNMENT COMMAND CENTER
                        </span>

                        <h1>
                            Societal challenges,
                            {" "}
                            <span>
                                from issue to impact.
                            </span>
                        </h1>

                        <p>
                            Monitor challenges, innovation pipelines,
                            projects, funding, risks and measurable
                            societal outcomes from one operational view.
                        </p>

                    </div>


                    <div className="hero-date">

                        <Clock3 size={16} />

                        <span>
                            Live platform overview
                        </span>

                    </div>

                </section>


                {/* --------------------------------------------------
                    KPI Cards
                -------------------------------------------------- */}

                <section className="government-kpis">

                    <MetricCard
                        icon={<FileText size={20} />}
                        label="Total Challenges"
                        value={
                            dashboard.challenge_stats.total
                        }
                        detail={`${dashboard.challenge_stats.high_priority} high priority`}
                    />

                    <MetricCard
                        icon={<LightbulbIcon />}
                        label="Innovation Challenges"
                        value={
                            dashboard.challenge_stats
                                .innovation_required
                        }
                        detail="Require ecosystem intervention"
                    />

                    <MetricCard
                        icon={<CheckCircle2 size={20} />}
                        label="Resolved Challenges"
                        value={
                            dashboard.challenge_stats.resolved
                        }
                        detail={`${analytics?.challenges.resolution_rate ?? 0}% resolution rate`}
                    />

                    <MetricCard
                        icon={<Target size={20} />}
                        label="Active Projects"
                        value={
                            dashboard.project_stats.active
                        }
                        detail={`${dashboard.project_stats.completed} completed`}
                    />

                    <MetricCard
                        icon={<ShieldAlert size={20} />}
                        label="Projects At Risk"
                        value={
                            dashboard.project_health.at_risk +
                            dashboard.project_health.delayed +
                            dashboard.project_health.critical
                        }
                        detail={`${dashboard.project_health.critical} critical`}
                        alert
                    />

                    <MetricCard
                        icon={<Building2 size={20} />}
                        label="Ecosystem Partners"
                        value={
                            dashboard.ecosystem.universities +
                            dashboard.ecosystem.industries
                        }
                        detail={`${dashboard.ecosystem.universities} universities · ${dashboard.ecosystem.industries} industries`}
                    />

                </section>


                {/* --------------------------------------------------
                    Main Grid
                -------------------------------------------------- */}

                <section className="government-main-grid">

                    {/* ==================================================
                        Challenge Status
                    ================================================== */}

                    <DashboardPanel
                        title="Challenge Pipeline"
                        subtitle="Current challenge lifecycle"
                        icon={<FileText size={18} />}
                    >

                        <StatusRows
                            rows={[
                                [
                                    "Submitted",
                                    dashboard.challenge_stats.submitted,
                                    "default",
                                ],
                                [
                                    "Under Review",
                                    dashboard.challenge_stats.under_review,
                                    "warning",
                                ],
                                [
                                    "Routed",
                                    dashboard.challenge_stats.routed,
                                    "info",
                                ],
                                [
                                    "In Progress",
                                    dashboard.challenge_stats.in_progress,
                                    "progress",
                                ],
                                [
                                    "Resolved",
                                    dashboard.challenge_stats.resolved,
                                    "success",
                                ],
                                [
                                    "Rejected",
                                    dashboard.challenge_stats.rejected,
                                    "danger",
                                ],
                            ]}
                        />

                    </DashboardPanel>


                    {/* ==================================================
                        Project Health
                    ================================================== */}

                    <DashboardPanel
                        title="Project Health"
                        subtitle="Execution health across projects"
                        icon={<ShieldAlert size={18} />}
                    >

                        <StatusRows
                            rows={[
                                [
                                    "On Track",
                                    dashboard.project_health.on_track,
                                    "success",
                                ],
                                [
                                    "At Risk",
                                    dashboard.project_health.at_risk,
                                    "warning",
                                ],
                                [
                                    "Delayed",
                                    dashboard.project_health.delayed,
                                    "danger",
                                ],
                                [
                                    "Critical",
                                    dashboard.project_health.critical,
                                    "critical",
                                ],
                            ]}
                        />

                    </DashboardPanel>


                    {/* ==================================================
                        Funding + Impact
                    ================================================== */}

                    <DashboardPanel
                        title="Funding & Impact"
                        subtitle="Financial and societal outcomes"
                        icon={<IndianRupee size={18} />}
                    >

                        <div className="funding-grid">

                            <FundingMetric
                                label="Allocated"
                                value={
                                    dashboard.funding.allocated
                                }
                            />

                            <FundingMetric
                                label="Disbursed"
                                value={
                                    dashboard.funding.disbursed
                                }
                            />

                            <FundingMetric
                                label="Utilized"
                                value={
                                    dashboard.funding.utilized
                                }
                            />

                            <FundingMetric
                                label="Remaining"
                                value={
                                    dashboard.funding.remaining
                                }
                            />

                        </div>


                        <div className="impact-strip">

                            <div>

                                <span>
                                    Verified Outcomes
                                </span>

                                <strong>
                                    {
                                        dashboard.impact
                                            .verified_outcomes
                                    }
                                </strong>

                            </div>

                            <div>

                                <span>
                                    Beneficiaries
                                </span>

                                <strong>
                                    {
                                        dashboard.impact
                                            .total_beneficiaries
                                    .toLocaleString()
                                    }
                                </strong>

                            </div>

                            <div>

                                <span>
                                    Avg. Project Progress
                                </span>

                                <strong>
                                    {
                                        dashboard.impact
                                            .average_project_progress
                                    }%
                                </strong>

                            </div>

                        </div>

                    </DashboardPanel>


                    {/* ==================================================
                        District Analytics
                    ================================================== */}

                    <DashboardPanel
                        title="District Challenge Distribution"
                        subtitle="Where societal challenges are concentrated"
                        icon={<MapPin size={18} />}
                        wide
                    >

                        {topDistricts.length === 0 ? (

                            <EmptyChartState />

                        ) : (

                            <div className="district-list">

                                {topDistricts.map(
                                    (district) => {

                                        const maxChallenges =
                                            topDistricts[0]
                                                ?.challenge_count ||
                                            1;

                                        const percentage =
                                            (district.challenge_count /
                                                maxChallenges) *
                                            100;

                                        return (
                                            <div
                                                className="district-row"
                                                key={
                                                    district.district
                                                }
                                            >

                                                <div className="district-label">

                                                    <span>
                                                        {
                                                            district.district
                                                        }
                                                    </span>

                                                    <strong>
                                                        {
                                                            district.challenge_count
                                                        }
                                                    </strong>

                                                </div>

                                                <div className="district-bar">

                                                    <div
                                                        style={{
                                                            width: `${percentage}%`,
                                                        }}
                                                    />

                                                </div>

                                                <div className="district-meta">

                                                    <span>
                                                        {
                                                            district.resolved_count
                                                        }{" "}
                                                        resolved
                                                    </span>

                                                    <span>
                                                        {
                                                            district.innovation_count
                                                        }{" "}
                                                        innovation
                                                    </span>

                                                </div>

                                            </div>
                                        );
                                    }
                                )}

                            </div>

                        )}

                    </DashboardPanel>


                    {/* ==================================================
                        University Leaderboard
                    ================================================== */}

                    <DashboardPanel
                        title="University Performance"
                        subtitle="Top ecosystem contributors"
                        icon={<Building2 size={18} />}
                    >

                        <Leaderboard
                            items={topUniversities.map(
                                (university) => ({
                                    name:
                                        university.organization_name,
                                    score:
                                        university.reputation_points,
                                    meta:
                                        `${university.projects} projects · ${university.completed_projects} completed`,
                                })
                            )}
                        />

                    </DashboardPanel>


                    {/* ==================================================
                        Industry Leaderboard
                    ================================================== */}

                    <DashboardPanel
                        title="Industry Contribution"
                        subtitle="Leading industry partners"
                        icon={<TrendingUp size={18} />}
                    >

                        <Leaderboard
                            items={topIndustries.map(
                                (industry) => ({
                                    name:
                                        industry.organization_name,
                                    score:
                                        industry.reputation_points,
                                    meta:
                                        `₹${industry.funding_contribution.toLocaleString()} contribution`,
                                })
                            )}
                        />

                    </DashboardPanel>


                    {/* ==================================================
                        Action Center
                    ================================================== */}

                    <DashboardPanel
                        title="Action Center"
                        subtitle="Items requiring attention"
                        icon={<ShieldAlert size={18} />}
                        wide
                    >

                        {!data.actionCenter ||
                        data.actionCenter.notifications
                            .length === 0 ? (

                            <div className="action-empty">
                                <CheckCircle2 size={23} />

                                <span>
                                    No pending actions.
                                </span>
                            </div>

                        ) : (

                            <div className="action-list">

                                {data.actionCenter.notifications
                                    .slice(0, 8)
                                    .map(
                                        (notification) => (

                                            <div
                                                className={`action-item action-${notification.priority.toLowerCase()}`}
                                                key={
                                                    notification.id
                                                }
                                            >

                                                <div className="action-item-icon">
                                                    <AlertCircle size={17} />
                                                </div>

                                                <div className="action-item-content">

                                                    <strong>
                                                        {
                                                            notification.title
                                                        }
                                                    </strong>

                                                    <p>
                                                        {
                                                            notification.message
                                                        }
                                                    </p>

                                                </div>

                                                <ChevronRight
                                                    size={18}
                                                    className="action-arrow"
                                                />

                                            </div>

                                        )
                                    )}

                            </div>

                        )}

                    </DashboardPanel>


                    {/* ==================================================
                        Project Initiation CTA
                    ================================================== */}

                    <DashboardPanel
                        title="Project Initiation"
                        subtitle="Convert accepted partnerships into executable projects"
                        icon={<Rocket size={18} />}
                        wide
                    >

                        <div className="government-project-cta">

                            <div>

                                <strong>
                                    Accepted collaborations are ready
                                    for project creation
                                </strong>

                                <p>
                                    Review university-industry
                                    partnerships that have been
                                    accepted and convert them into
                                    projects with automatic milestone
                                    planning.
                                </p>

                            </div>

                            <button
                                type="button"
                                className="government-primary-action"
                                onClick={() =>
                                    navigate(
                                        "/government/collaborations"
                                    )
                                }
                            >
                                <Rocket size={17} />
                                View Accepted Collaborations
                                <ArrowRight size={16} />
                            </button>

                        </div>

                    </DashboardPanel>


                    {/* ==================================================
                        RFP Pipeline
                    ================================================== */}

                    <DashboardPanel
                        title="RFP Pipeline"
                        subtitle="Request for Proposals — live status"
                        icon={<FileText size={18} />}
                        wide
                    >

                        <div className="rfp-header-row">
                            <span className="rfp-count-badge">
                                {rfps.length} RFP{rfps.length !== 1 ? "s" : ""}
                            </span>
                            <button
                                className="rfp-create-btn"
                                onClick={() => navigate("/government/rfps/new")}
                            >
                                <ArrowRight size={14} />
                                Create New RFP
                            </button>
                        </div>

                        {rfps.length === 0 ? (

                            <div className="rfp-empty">
                                <FileText size={28} strokeWidth={1.4} />
                                <p>No RFPs created yet.</p>
                                <span>
                                    Create an RFP from an approved Innovation
                                    Opportunity to invite university proposals.
                                </span>
                                <button
                                    className="rfp-empty-cta"
                                    onClick={() =>
                                        navigate("/government/rfps/new")
                                    }
                                >
                                    Create First RFP
                                    <ArrowRight size={14} />
                                </button>
                            </div>

                        ) : (

                            <div className="rfp-list">
                                {rfps.map((rfp) => (
                                    <div
                                        key={rfp.id}
                                        className={`rfp-card rfp-card--${rfp.status.toLowerCase()}`}
                                    >
                                        <div className="rfp-card-main">
                                            <div className="rfp-card-left">
                                                <span className={`rfp-status-badge rfp-status--${rfp.status.toLowerCase()}`}>
                                                    {rfp.status}
                                                </span>
                                                <strong className="rfp-title">
                                                    {rfp.title}
                                                </strong>
                                                <p className="rfp-desc">
                                                    {rfp.description.length > 100
                                                        ? rfp.description.slice(0, 100) + "…"
                                                        : rfp.description}
                                                </p>
                                            </div>

                                            <div className="rfp-card-meta">
                                                {rfp.estimated_budget && (
                                                    <div className="rfp-meta-item">
                                                        <IndianRupee size={13} />
                                                        <span>
                                                            ₹{rfp.estimated_budget.toLocaleString()}
                                                        </span>
                                                    </div>
                                                )}
                                                {rfp.proposal_deadline && (
                                                    <div className="rfp-meta-item">
                                                        <Clock3 size={13} />
                                                        <span>
                                                            Due{" "}
                                                            {new Date(
                                                                rfp.proposal_deadline
                                                            ).toLocaleDateString("en-IN", {
                                                                day: "numeric",
                                                                month: "short",
                                                                year: "numeric",
                                                            })}
                                                        </span>
                                                    </div>
                                                )}
                                                {rfp.expected_duration_days && (
                                                    <div className="rfp-meta-item">
                                                        <Target size={13} />
                                                        <span>
                                                            {rfp.expected_duration_days} days
                                                        </span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        <div className="rfp-card-actions">
                                            <button
                                                className="rfp-action-btn rfp-action-btn--view"
                                                onClick={() =>
                                                    navigate(`/government/rfps/${rfp.id}`)
                                                }
                                            >
                                                View
                                                <ChevronRight size={14} />
                                            </button>

                                            {rfp.status === "DRAFT" && (
                                                <button
                                                    className="rfp-action-btn rfp-action-btn--match"
                                                    onClick={() =>
                                                        navigate(
                                                            `/government/rfps/${rfp.id}/universities`
                                                        )
                                                    }
                                                >
                                                    Match Universities
                                                    <ArrowRight size={14} />
                                                </button>
                                            )}

                                            {rfp.status === "PUBLISHED" && (
                                                <button
                                                    className="rfp-action-btn rfp-action-btn--proposals"
                                                    onClick={() =>
                                                        navigate(
                                                            `/government/rfps/${rfp.id}/proposals`
                                                        )
                                                    }
                                                >
                                                    View Proposals
                                                    <ArrowRight size={14} />
                                                </button>
                                            )}
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

function LightbulbIcon() {
    return (
        <TrendingUp size={20} />
    );
}


function HandshakeIcon() {
    return (
        <Users size={17} />
    );
}


interface MetricCardProps {
    icon: React.ReactNode;
    label: string;
    value: number;
    detail: string;
    alert?: boolean;
}


function MetricCard({
    icon,
    label,
    value,
    detail,
    alert = false,
}: MetricCardProps) {

    return (
        <div
            className={`government-metric-card${
                alert
                    ? " government-metric-alert"
                    : ""
            }`}
        >

            <div className="government-metric-icon">
                {icon}
            </div>

            <div className="government-metric-content">

                <span>
                    {label}
                </span>

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
            className={`government-panel${
                wide
                    ? " government-panel-wide"
                    : ""
            }`}
        >

            <div className="government-panel-header">

                <div className="government-panel-title">

                    <div className="government-panel-icon">
                        {icon}
                    </div>

                    <div>
                        <h2>{title}</h2>
                        <p>{subtitle}</p>
                    </div>

                </div>

            </div>

            <div className="government-panel-body">
                {children}
            </div>

        </section>
    );
}


type StatusTone =
    | "default"
    | "warning"
    | "info"
    | "progress"
    | "success"
    | "danger"
    | "critical";


function StatusRows({
    rows,
}: {
    rows: [string, number, StatusTone][];
}) {

    return (
        <div className="status-rows">

            {rows.map(
                ([label, value, tone]) => (

                    <div
                        className="status-row"
                        key={label}
                    >

                        <div className="status-row-left">

                            <span
                                className={`status-dot status-dot-${tone}`}
                            />

                            <span>
                                {label}
                            </span>

                        </div>

                        <strong>
                            {value}
                        </strong>

                    </div>
                )
            )}

        </div>
    );
}


function FundingMetric({
    label,
    value,
}: {
    label: string;
    value: number;
}) {

    return (
        <div className="funding-metric">

            <span>
                {label}
            </span>

            <strong>
                ₹{value.toLocaleString()}
            </strong>

        </div>
    );
}


function Leaderboard({
    items,
}: {
    items: {
        name: string;
        score: number;
        meta: string;
    }[];
}) {

    if (items.length === 0) {
        return <EmptyChartState />;
    }

    return (
        <div className="leaderboard">

            {items.map((item, index) => (

                <div
                    className="leaderboard-item"
                    key={item.name}
                >

                    <div className="leaderboard-rank">
                        #{index + 1}
                    </div>

                    <div className="leaderboard-main">

                        <strong>
                            {item.name}
                        </strong>

                        <span>
                            {item.meta}
                        </span>

                    </div>

                    <div className="leaderboard-score">

                        {item.score}

                        <small>
                            {" "}pts
                        </small>

                    </div>

                </div>

            ))}

        </div>
    );
}


function EmptyChartState() {
    return (
        <div className="dashboard-empty-chart">

            <BarChart3 size={28} />

            <span>
                No analytics data available yet.
            </span>

        </div>
    );
}