import { Navigate, Route, Routes } from "react-router-dom";

import LandingPage from "../pages/public/LandingPage";
import LoginPage from "../pages/auth/LoginPage";
import RegisterPage from "../pages/auth/RegisterPage";

import CitizenDashboard from "../pages/citizen/CitizenDashboard";
import ProtectedRoute from "./ProtectedRoute";
import SubmitChallengePage from "../pages/citizen/SubmitChallengePage";
import ChallengeDetailsPage from "../pages/citizen/ChallengeDetailsPage";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Citizen protected routes */}
      <Route
        element={<ProtectedRoute allowedRoles={["CITIZEN"]} />}
      >
        <Route
          path="/citizen/dashboard"
          element={<CitizenDashboard />}
        />

        <Route
            path="/citizen/challenges/new"
            element={<SubmitChallengePage />}
        />

        <Route
            path="/citizen/challenges/:id"
            element={<ChallengeDetailsPage />}
        />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}