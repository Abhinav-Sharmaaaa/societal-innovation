import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Building2,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Rocket,
  ShieldCheck,
  User,
} from "lucide-react";
import NotificationBell from "../NotificationBell/NotificationBell";
import type { User as UserType, UserRole } from "../../types/auth";
import "./Navbar.css";


// ============================================================
// Role → dashboard route
// ============================================================

function getDashboardPath(role: UserRole): string {
  switch (role) {
    case "CITIZEN":
      return "/citizen/dashboard";
    case "SUPER_ADMIN":
    case "REVIEW_OFFICER":
    case "GOVERNMENT_OFFICER":
    case "MUNICIPALITY_OFFICER":
      return "/government/dashboard";
    case "UNIVERSITY_ADMIN":
    case "FACULTY":
    case "STUDENT":
      return "/university/dashboard";
    case "INDUSTRY_ADMIN":
    case "INDUSTRY_MEMBER":
      return "/industry/dashboard";
    default:
      return "/";
  }
}


// ============================================================
// Role → color + icon
// ============================================================

interface RoleMeta {
  label: string;
  color: string;
  Icon: React.ElementType;
}

function getRoleMeta(role: UserRole): RoleMeta {
  switch (role) {
    case "CITIZEN":
      return { label: "Citizen", color: "#10b981", Icon: User };
    case "SUPER_ADMIN":
      return { label: "Super Admin", color: "#7c3aed", Icon: ShieldCheck };
    case "REVIEW_OFFICER":
    case "GOVERNMENT_OFFICER":
    case "MUNICIPALITY_OFFICER":
      return { label: "Government", color: "#2563eb", Icon: LayoutDashboard };
    case "UNIVERSITY_ADMIN":
    case "FACULTY":
    case "STUDENT":
      return { label: "University", color: "#d97706", Icon: GraduationCap };
    case "INDUSTRY_ADMIN":
    case "INDUSTRY_MEMBER":
      return { label: "Industry", color: "#0891b2", Icon: Building2 };
    default:
      return { label: role, color: "#64748b", Icon: User };
  }
}


// ============================================================
// Nav Links per role
// ============================================================

interface NavLink {
  label: string;
  to: string;
}

function getNavLinks(role: UserRole): NavLink[] {
  switch (role) {
    case "CITIZEN":
      return [
        { label: "Dashboard", to: "/citizen/dashboard" },
        { label: "Submit Challenge", to: "/citizen/challenges/new" },
      ];
    case "SUPER_ADMIN":
    case "REVIEW_OFFICER":
    case "GOVERNMENT_OFFICER":
    case "MUNICIPALITY_OFFICER":
      return [
        { label: "Dashboard", to: "/government/dashboard" },
        { label: "Challenges", to: "/government/challenges" },
        { label: "Reviews", to: "/government/reviews" },
        { label: "Projects", to: "/government/projects" },
        { label: "Collaborations", to: "/government/collaborations" },
        ...(role === "SUPER_ADMIN"
          ? [{ label: "⚙ Admin", to: "/admin" }]
          : []),
      ];
    case "UNIVERSITY_ADMIN":
    case "FACULTY":
      return [
        { label: "Dashboard",     to: "/university/dashboard" },
        { label: "Invitations",   to: "/university/invitations" },
        { label: "My Proposals",  to: "/university/proposals" },
        { label: "Collaborations", to: "/university/collaborations" },
      ];
    case "STUDENT":
      return [
        { label: "Dashboard", to: "/university/dashboard" },
      ];
    case "INDUSTRY_ADMIN":
    case "INDUSTRY_MEMBER":
      return [
        { label: "Dashboard", to: "/industry/dashboard" },
        { label: "Opportunities", to: "/industry/opportunities" },
      ];
    default:
      return [];
  }
}


// ============================================================
// Navbar Component
// ============================================================

export default function Navbar() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserType | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem("user");
    if (raw) {
      try {
        setUser(JSON.parse(raw));
      } catch {/* ignore */}
    }
  }, []);

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    navigate("/login");
  }

  if (!user) return null;

  const { label, color, Icon } = getRoleMeta(user.role);
  const dashPath = getDashboardPath(user.role);
  const navLinks = getNavLinks(user.role);

  return (
    <nav className="navbar" role="navigation" aria-label="Main navigation">

      {/* ---- Brand ---- */}
      <Link to={dashPath} className="navbar-brand" aria-label="Go to dashboard">
        <div className="navbar-logo">
          <Rocket size={18} />
        </div>
        <span className="navbar-brand-text">SIP</span>
      </Link>


      {/* ---- Links (Desktop) ---- */}
      <ul className="navbar-links" role="list">
        {navLinks.map((link) => (
          <li key={link.to}>
            <Link
              to={link.to}
              className="navbar-link"
            >
              {link.label}
            </Link>
          </li>
        ))}
      </ul>


      {/* ---- Right Section ---- */}
      <div className="navbar-right">

        {/* Notification Bell */}
        <NotificationBell />

        {/* Role Badge */}
        <span
          className="navbar-role-badge"
          style={{ "--role-color": color } as React.CSSProperties}
        >
          <Icon size={11} />
          {label}
        </span>

        {/* User Avatar + Dropdown */}
        <div className="navbar-user" onClick={() => setMenuOpen((o) => !o)}>
          <div className="navbar-avatar">
            {user.full_name.charAt(0).toUpperCase()}
          </div>
          <span className="navbar-user-name">
            {user.full_name.split(" ")[0]}
          </span>

          {menuOpen && (
            <div className="navbar-dropdown">
              <div className="navbar-dropdown-header">
                <strong>{user.full_name}</strong>
                <span>{user.email}</span>
              </div>
              <button
                className="navbar-dropdown-item navbar-logout"
                onClick={handleLogout}
              >
                <LogOut size={14} />
                Sign out
              </button>
            </div>
          )}
        </div>

      </div>


      {/* ---- Mobile Hamburger ---- */}
      <button
        className="navbar-hamburger"
        aria-label="Toggle menu"
        onClick={() => setMenuOpen((o) => !o)}
      >
        <span />
        <span />
        <span />
      </button>

    </nav>
  );
}
