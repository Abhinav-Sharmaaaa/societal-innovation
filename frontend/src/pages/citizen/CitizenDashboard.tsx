import {
  AlertCircle,
  ArrowRight,
  Award,
  CheckCircle2,
  Clock3,
  FileText,
  Lightbulb,
  LogOut,
  MapPin,
  Plus,
  UserRound,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getCurrentUser } from "../../services/authService";
import { api } from "../../services/api";
import {
  dashboardService,
  type CitizenDashboard as CitizenDashboardData,
} from "../../services/dashboardService";

import type { User } from "../../types/auth";
import "./CitizenDashboard.css";


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

  ai_confidence_score: number | null;
  ai_model_version: string | null;

  routing_type: string;
  routing_reason: string | null;

  status: string;

  is_master_challenge: boolean;
  master_challenge_id: number | null;
  duplicate_similarity_score: number | null;

  evidence: unknown[];

  created_at: string;
  updated_at: string;
}


export default function CitizenDashboard() {
  const navigate = useNavigate();

  const [user, setUser] = useState<User | null>(null);
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [dashboard, setDashboard] =
    useState<CitizenDashboardData | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  /*
  |--------------------------------------------------------------------------
  | Load Dashboard Data
  |--------------------------------------------------------------------------
  */

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [
          currentUserResponse,
          dashboardResponse,
          challengesResponse,
        ] = await Promise.all([
          getCurrentUser(),
          dashboardService.getCitizenDashboard(),
          api.get<Challenge[]>("/challenges/my"),
        ]);

        setUser(currentUserResponse);
        setDashboard(dashboardResponse);
        setChallenges(challengesResponse.data);

        localStorage.setItem(
          "user",
          JSON.stringify(currentUserResponse)
        );
      } catch (requestError: any) {
        console.error(requestError);

        if (requestError.response?.status === 401) {
          handleLogout();
          return;
        }

        setError(
          requestError.response?.data?.detail ||
            "Unable to load your dashboard."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);


  /*
  |--------------------------------------------------------------------------
  | Logout
  |--------------------------------------------------------------------------
  */

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");

    navigate("/login");
  }


  /*
  |--------------------------------------------------------------------------
  | Loading
  |--------------------------------------------------------------------------
  */

  if (loading) {
    return (
      <main className="dashboard-page">
        <div className="dashboard-loading">
          Loading your dashboard...
        </div>
      </main>
    );
  }


  /*
  |--------------------------------------------------------------------------
  | Error
  |--------------------------------------------------------------------------
  */

  if (error) {
    return (
      <main className="dashboard-page">
        <div className="dashboard-error">
          <AlertCircle size={22} />

          <div>
            <strong>
              Unable to load dashboard
            </strong>

            <p>{error}</p>
          </div>
        </div>
      </main>
    );
  }


  /*
  |--------------------------------------------------------------------------
  | Backend Statistics
  |--------------------------------------------------------------------------
  */

  const stats = dashboard?.challenge_stats;

  const totalChallenges =
    stats?.total ?? challenges.length;

  const submittedChallenges =
    stats?.submitted ?? 0;

  const inProgressChallenges =
    stats?.in_progress ?? 0;

  const resolvedChallenges =
    stats?.resolved ?? 0;

  const innovationChallenges =
    stats?.innovation_required ?? 0;

  const reputationPoints =
    dashboard?.reputation.total_points ?? 0;

  const reputationContributions =
    dashboard?.reputation.contribution_count ?? 0;


  return (
    <main className="dashboard-page">

      {/* ====================================================
          Header
      ==================================================== */}

      <header className="dashboard-header">

        <div className="dashboard-header-inner">

          <button
            className="dashboard-brand"
            onClick={() => navigate("/")}
          >
            <div className="dashboard-brand-icon">
              <FileText size={20} />
            </div>

            <span>
              Societal Innovation Platform
            </span>
          </button>


          <div className="dashboard-user">

            <div className="dashboard-user-avatar">
              <UserRound size={17} />
            </div>

            <div className="dashboard-user-info">
              <strong>
                {user?.full_name}
              </strong>

              <span>
                Citizen
              </span>
            </div>

            <button
              className="dashboard-logout"
              onClick={handleLogout}
              title="Logout"
            >
              <LogOut size={18} />
            </button>

          </div>

        </div>

      </header>


      {/* ====================================================
          Main Content
      ==================================================== */}

      <div className="dashboard-container">

        {/* --------------------------------------------------
            Welcome
        -------------------------------------------------- */}

        <section className="dashboard-welcome">

          <div>

            <span className="dashboard-eyebrow">
              CITIZEN PORTAL
            </span>

            <h1>
              Welcome back{" "}
              {user?.full_name?.split(" ")[0] ||
                "Citizen"}
              .
            </h1>

            <p>
              Report societal challenges, track their progress,
              and see how your submissions move toward
              real-world solutions.
            </p>

          </div>

          <button
            className="btn btn-primary btn-large"
            onClick={() =>
              navigate(
                "/citizen/challenges/new"
              )
            }
          >
            <Plus size={18} />
            Report a Challenge
          </button>

        </section>


        {/* --------------------------------------------------
            Main Stats
        -------------------------------------------------- */}

        <section className="dashboard-stats">

          <StatCard
            icon={<FileText size={19} />}
            label="Total Challenges"
            value={totalChallenges}
          />

          <StatCard
            icon={<Clock3 size={19} />}
            label="Submitted"
            value={submittedChallenges}
          />

          <StatCard
            icon={<AlertCircle size={19} />}
            label="In Progress"
            value={inProgressChallenges}
          />

          <StatCard
            icon={<CheckCircle2 size={19} />}
            label="Resolved"
            value={resolvedChallenges}
          />

        </section>


        {/* --------------------------------------------------
            Reputation
        -------------------------------------------------- */}

        <section className="dashboard-section">

          <div className="dashboard-section-header">

            <div>
              <h2>
                Your Contribution
              </h2>

              <p>
                Your participation and contribution
                to the societal innovation ecosystem.
              </p>
            </div>

          </div>

          <div className="dashboard-stats">

            <StatCard
              icon={<Award size={19} />}
              label="Reputation Points"
              value={reputationPoints}
            />

            <StatCard
              icon={<CheckCircle2 size={19} />}
              label="Contributions"
              value={reputationContributions}
            />

            <StatCard
              icon={<Lightbulb size={19} />}
              label="Innovation Challenges"
              value={innovationChallenges}
            />

          </div>

        </section>


        {/* --------------------------------------------------
            Challenges
        -------------------------------------------------- */}

        <section className="dashboard-section">

          <div className="dashboard-section-header">

            <div>
              <h2>
                My Challenges
              </h2>

              <p>
                Challenges you have submitted to
                the platform.
              </p>
            </div>

            {challenges.length > 0 && (
              <span className="challenge-count">
                {challenges.length}
              </span>
            )}

          </div>


          {challenges.length === 0 ? (

            <div className="empty-state">

              <div className="empty-state-icon">
                <FileText size={25} />
              </div>

              <h3>
                No challenges yet
              </h3>

              <p>
                Have a societal problem that needs
                solving? Submit the first challenge.
              </p>

              <button
                className="btn btn-primary"
                onClick={() =>
                  navigate(
                    "/citizen/challenges/new"
                  )
                }
              >
                Report a Challenge
                <ArrowRight size={17} />
              </button>

            </div>

          ) : (

            <div className="challenge-list">

              {challenges.map((challenge) => (

                <ChallengeCard
                  key={challenge.id}
                  challenge={challenge}
                  onClick={() =>
                    navigate(
                      `/citizen/challenges/${challenge.id}`
                    )
                  }
                />

              ))}

            </div>

          )}

        </section>

      </div>

    </main>
  );
}


/* ============================================================
   Stat Card
   ============================================================ */

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
}


function StatCard({
  icon,
  label,
  value,
}: StatCardProps) {

  return (
    <div className="stat-card">

      <div className="stat-icon">
        {icon}
      </div>

      <div>
        <span>
          {label}
        </span>

        <strong>
          {value}
        </strong>
      </div>

    </div>
  );
}


/* ============================================================
   Challenge Card
   ============================================================ */

interface ChallengeCardProps {
  challenge: Challenge;
  onClick: () => void;
}


function ChallengeCard({
  challenge,
  onClick,
}: ChallengeCardProps) {

  const status = challenge.status;

  return (
    <button
      className="challenge-card"
      onClick={onClick}
    >

      <div className="challenge-card-main">

        <div className="challenge-card-top">

          <span className="challenge-id">
            CHL-
            {String(challenge.id).padStart(
              5,
              "0"
            )}
          </span>

          <StatusBadge
            status={status}
          />

        </div>

        <h3>
          {challenge.title}
        </h3>

        <p>
          {challenge.description}
        </p>

        <div className="challenge-meta">

          <span>
            <FileText size={14} />
            {challenge.category}
          </span>

          {challenge.district && (
            <span>
              <MapPin size={14} />

              {challenge.district}

              {challenge.state &&
                `, ${challenge.state}`}
            </span>
          )}

        </div>

      </div>


      <ArrowRight
        size={19}
        className="challenge-arrow"
      />

    </button>
  );
}


/* ============================================================
   Status Badge
   ============================================================ */

function StatusBadge({
  status,
}: {
  status: string;
}) {

  const label = status
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      (char) => char.toUpperCase()
    );

  return (
    <span
      className={`status-badge status-${status.toLowerCase()}`}
    >
      {label}
    </span>
  );
}