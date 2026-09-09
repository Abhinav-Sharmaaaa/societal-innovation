import { FormEvent, useState } from "react";
import {
  ArrowRight,
  LockKeyhole,
  Mail,
  Phone,
  UserRound,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { registerUser } from "../../services/authService";

import "./RegisterPage.css";


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

    // --------------------------------------------------------
    // Client-side validation
    // --------------------------------------------------------

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
        "Account created successfully. Redirecting to login..."
      );

      setTimeout(() => {
        navigate("/login");
      }, 1000);

    } catch (requestError: any) {
      setError(
        requestError.response?.data?.detail ||
          "Unable to create your account."
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="register-page">

      <div className="register-card">

        {/* ==================================================
            Header
        ================================================== */}

        <div className="register-header">

          <div className="register-icon">
            <UserRound size={22} />
          </div>

          <h1>Create your account</h1>

          <p>
            Join the Societal Innovation Platform and help
            turn real-world problems into solutions.
          </p>

        </div>


        {/* ==================================================
            Messages
        ================================================== */}

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


        {/* ==================================================
            Form
        ================================================== */}

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
                onChange={(event) =>
                  setFullName(event.target.value)
                }
                required
                minLength={2}
                maxLength={150}
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
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                required
              />
            </div>
          </label>


          {/* Phone */}

          <label>
            Phone number
            <span className="optional-label">
              Optional
            </span>

            <div className="register-input-wrapper">
              <Phone size={18} />

              <input
                type="tel"
                placeholder="9876543210"
                value={phone}
                onChange={(event) =>
                  setPhone(event.target.value)
                }
                maxLength={20}
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
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                required
                minLength={8}
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
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                required
              />
            </div>
          </label>


          {/* Submit */}

          <button
            className="btn btn-primary register-submit"
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Creating account..."
              : "Create account"}

            {!loading && (
              <ArrowRight size={18} />
            )}
          </button>

        </form>


        {/* ==================================================
            Footer
        ================================================== */}

        <div className="register-footer">

          Already have an account?

          <button
            type="button"
            onClick={() => navigate("/login")}
          >
            Sign in
          </button>

        </div>

      </div>

    </main>
  );
}