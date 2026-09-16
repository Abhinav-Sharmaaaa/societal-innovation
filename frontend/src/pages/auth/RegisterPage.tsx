import { useState } from "react";
import type { FormEvent } from "react";
import {
  ArrowRight,
  Building2,
  GraduationCap,
  Info,
  LockKeyhole,
  Mail,
  Phone,
  ShieldCheck,
  UserRound,
  Users,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { registerUser } from "../../services/authService";

import "./RegisterPage.css";


// ============================================================
// Role info cards shown beneath the form
// ============================================================

const ROLE_INFO = [
  {
    icon: <Users size={16} />,
    title: "Citizens",
    description: "Register here to submit civic challenges and track their resolution.",
    color: "#10b981",
    highlight: true,
  },
  {
    icon: <ShieldCheck size={16} />,
    title: "Government / Municipality Officers",
    description: "Accounts are created by the platform SUPER_ADMIN. Contact your administrator.",
    color: "#2563eb",
  },
  {
    icon: <GraduationCap size={16} />,
    title: "University Faculty & Students",
    description: "Accounts are created by the platform SUPER_ADMIN after your institution is registered.",
    color: "#d97706",
  },
  {
    icon: <Building2 size={16} />,
    title: "Industry Partners",
    description: "Accounts are created by the platform SUPER_ADMIN after your organisation is registered.",
    color: "#0891b2",
  },
];


export default function RegisterPage() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    setLoading(true);

    try {
      await registerUser({
        full_name: fullName.trim(),
        email: email.trim().toLowerCase(),
        phone: phone.trim() || undefined,
        password,
        role: "CITIZEN",
      });

      setSuccess(
        "Account created successfully! Redirecting to login…"
      );

      setTimeout(() => navigate("/login"), 1200);

    } catch (requestError: any) {
      setError(
        requestError.response?.data?.detail ||
          "Unable to create your account. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="register-page">

      <div className="register-card">

        {/* ================================================
            Header
        ================================================ */}

        <div className="register-header">

          <div className="register-icon">
            <UserRound size={22} />
          </div>

          <h1>Create your account</h1>

          <p>
            Join as a <strong>Citizen</strong> to submit real-world civic
            challenges and track their resolution on the Societal Innovation
            Platform.
          </p>

        </div>


        {/* ================================================
            Messages
        ================================================ */}

        {error && (
          <div className="register-message register-error">
            {error}
          </div>
        )}

        {success && (
          <div className="register-message register-success">
            {success}
          </div>
        )}


        {/* ================================================
            Form
        ================================================ */}

        <form
          className="register-form"
          onSubmit={handleSubmit}
        >

          {/* Full Name */}
          <label>
            Full name
            <div className="register-input-wrapper">
              <UserRound size={18} />
              <input
                type="text"
                placeholder="Your full name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                minLength={2}
                maxLength={150}
                id="register-full-name"
              />
            </div>
          </label>


          {/* Email */}
          <label>
            Email
            <div className="register-input-wrapper">
              <Mail size={18} />
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                id="register-email"
              />
            </div>
          </label>


          {/* Phone */}
          <label>
            Phone number
            <span className="optional-label">Optional</span>
            <div className="register-input-wrapper">
              <Phone size={18} />
              <input
                type="tel"
                placeholder="9876543210"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                maxLength={20}
                id="register-phone"
              />
            </div>
          </label>


          {/* Password */}
          <label>
            Password
            <div className="register-input-wrapper">
              <LockKeyhole size={18} />
              <input
                type="password"
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                id="register-password"
              />
            </div>
          </label>


          {/* Confirm Password */}
          <label>
            Confirm password
            <div className="register-input-wrapper">
              <LockKeyhole size={18} />
              <input
                type="password"
                placeholder="Re-enter your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                id="register-confirm-password"
              />
            </div>
          </label>


          {/* Account type info badge */}
          <div className="register-role-badge">
            <Info size={14} />
            Registering as: <strong>Citizen</strong>
          </div>


          {/* Submit */}
          <button
            className="btn btn-primary register-submit"
            type="submit"
            id="register-submit-btn"
            disabled={loading}
          >
            {loading ? "Creating account…" : "Create Citizen account"}
            {!loading && <ArrowRight size={18} />}
          </button>

        </form>


        {/* ================================================
            Other Account Types Info
        ================================================ */}

        <div className="register-roles-section">
          <p className="register-roles-label">
            Looking for a different account type?
          </p>

          <div className="register-roles-grid">
            {ROLE_INFO.map((role) => (
              <div
                key={role.title}
                className={`register-role-card ${role.highlight ? "register-role-card--active" : ""}`}
                style={{ "--role-color": role.color } as React.CSSProperties}
              >
                <span className="register-role-icon">{role.icon}</span>
                <div>
                  <strong>{role.title}</strong>
                  <p>{role.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>


        {/* ================================================
            Footer
        ================================================ */}

        <div className="register-footer">
          Already have an account?
          <button
            type="button"
            onClick={() => navigate("/login")}
            id="register-signin-link"
          >
            Sign in
          </button>
        </div>

      </div>

    </main>
  );
}