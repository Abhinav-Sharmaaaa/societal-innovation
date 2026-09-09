import { FormEvent, useState } from "react";
import { ArrowRight, LockKeyhole, Mail } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { loginUser } from "../../services/authService";


export default function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const result = await loginUser({
        email,
        password,
      });

      /*
      |--------------------------------------------------------------------------
      | Store Authentication State
      |--------------------------------------------------------------------------
      */

      localStorage.setItem(
        "access_token",
        result.tokens.access_token
      );

      localStorage.setItem(
        "refresh_token",
        result.tokens.refresh_token
      );

      localStorage.setItem(
        "user",
        JSON.stringify(result.user)
      );


      /*
      |--------------------------------------------------------------------------
      | Role-Based Redirect
      |--------------------------------------------------------------------------
      */

      switch (result.user.role) {
        case "CITIZEN":
          navigate("/citizen/dashboard");
          break;

        default:
          navigate("/");
      }

    } catch (requestError: any) {
      setError(
        requestError.response?.data?.detail ||
          "Unable to login. Please check your credentials."
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="auth-page">

      <div className="auth-card">

        <div className="auth-header">

          <div className="auth-icon">
            <LockKeyhole size={22} />
          </div>

          <h1>Welcome back</h1>

          <p>
            Sign in to continue to the
            Societal Innovation Platform.
          </p>

        </div>


        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}


        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >

          <label>
            Email

            <div className="input-wrapper">
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


          <label>
            Password

            <div className="input-wrapper">
              <LockKeyhole size={18} />

              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                required
              />
            </div>
          </label>


          <button
            className="btn btn-primary auth-submit"
            type="submit"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign in"}

            {!loading && (
              <ArrowRight size={18} />
            )}
          </button>

        </form>


        <div className="auth-footer">
          Don't have an account?

          <button
            type="button"
            onClick={() => navigate("/register")}
          >
            Create one
          </button>
        </div>

      </div>

    </main>
  );
}