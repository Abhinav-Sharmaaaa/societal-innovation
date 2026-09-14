import { Navigate, Route, Routes } from "react-router-dom";

// Public
import LandingPage from "../pages/public/LandingPage";
import LoginPage from "../pages/auth/LoginPage";
import RegisterPage from "../pages/auth/RegisterPage";

// Citizen
import CitizenDashboard from "../pages/citizen/CitizenDashboard";
import SubmitChallengePage from "../pages/citizen/SubmitChallengePage";
import ChallengeDetailsPage from "../pages/citizen/ChallengeDetailsPage";

// Government
import GovernmentDashboard from "../pages/government/GovernmentDashboard";
import GovernmentChallengesPage from "../pages/government/GovernmentChallengesPage";
import GovernmentChallengeDetailsPage from "../pages/government/GovernmentChallengeDetailsPage";
import HumanReviewQueuePage from "../pages/government/HumanReviewQueuePage";
import CreateInnovationOpportunityPage from "../pages/government/CreateInnovationOpportunityPage";
import InnovationOpportunityDetailsPage from "../pages/government/InnovationOpportunityDetailsPage";
import CreateRFPPage from "../pages/government/CreateRFPPage";
import RFPDetailsPage from "../pages/government/RFPDetailsPage";
import RFPUniversityMatchingPage from "../pages/government/RFPUniversityMatchingPage";

// University
import UniversityDashboard from "../pages/university/UniversityDashboard";
import UniversityInvitationsPage from "../pages/university/UniversityInvitationsPage";
import CreateUniversityProposalPage from "../pages/university/CreateUniversityProposalPage";
import UniversityProposalDetailsPage from "../pages/university/UniversityProposalDetailsPage";

// Industry
import IndustryDashboard from "../pages/industry/IndustryDashboard";

// Security
import ProtectedRoute from "./ProtectedRoute";

import RFPProposalsPage from "../pages/government/RFPProposalsPage";
import ProposalEvaluationPage from "../pages/government/ProposalEvaluationPage";
import IndustryOpportunitiesPage from "../pages/industry/IndustryOpportunitiesPage";
import CreateIndustryCollaborationPage from "../pages/industry/CreateIndustryCollaborationPage";
import IndustryOpportunityDetailsPage from "../pages/industry/IndustryOpportunityDetailsPage";

export default function AppRoutes() {
  return (
    <Routes>

      {/* ======================================================
          PUBLIC ROUTES
      ====================================================== */}

      <Route
        path="/"
        element={<LandingPage />}
      />

      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route
        path="/register"
        element={<RegisterPage />}
      />


      {/* ======================================================
          CITIZEN ROUTES
      ====================================================== */}

      <Route
        element={
          <ProtectedRoute
            allowedRoles={["CITIZEN"]}
          />
        }
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


      {/* ======================================================
          GOVERNMENT ROUTES
      ====================================================== */}

      <Route
        element={
          <ProtectedRoute
            allowedRoles={[
              "SUPER_ADMIN",
              "REVIEW_OFFICER",
              "GOVERNMENT_OFFICER",
              "MUNICIPALITY_OFFICER",
            ]}
          />
        }
      >

        {/* Dashboard */}
        <Route
          path="/government/dashboard"
          element={<GovernmentDashboard />}
        />

        {/* Challenges */}
        <Route
          path="/government/challenges"
          element={<GovernmentChallengesPage />}
        />

        <Route
          path="/government/challenges/:id"
          element={<GovernmentChallengeDetailsPage />}
        />

        {/* Human Review */}
        <Route
          path="/government/reviews"
          element={<HumanReviewQueuePage />}
        />

        {/* Innovation Opportunity */}
        <Route
          path="/government/innovation/new"
          element={<CreateInnovationOpportunityPage />}
        />

        <Route
          path="/government/innovation/:id"
          element={<InnovationOpportunityDetailsPage />}
        />

        {/* RFP */}
        <Route
          path="/government/rfps/new"
          element={<CreateRFPPage />}
        />

        <Route
          path="/government/rfps/:id"
          element={<RFPDetailsPage />}
        />

        <Route
          path="/government/rfps/:id/universities"
          element={<RFPUniversityMatchingPage />}
        />
        <Route
          path="/government/rfps/:id/proposals"
          element={<RFPProposalsPage />}
        />

        <Route
          path="/government/proposals/:id/evaluate"
          element={<ProposalEvaluationPage />}
        />

      </Route>


      {/* ======================================================
          UNIVERSITY ROUTES
      ====================================================== */}

      {/* University Dashboard */}
      <Route
        element={
          <ProtectedRoute
            allowedRoles={[
              "UNIVERSITY_ADMIN",
              "FACULTY",
              "STUDENT",
            ]}
          />
        }
      >
        <Route
          path="/university/dashboard"
          element={<UniversityDashboard />}
        />
      </Route>


      {/* University Invitations */}
      <Route
        element={
          <ProtectedRoute
            allowedRoles={[
              "UNIVERSITY_ADMIN",
              "FACULTY",
            ]}
          />
        }
      >
        <Route
          path="/university/invitations"
          element={<UniversityInvitationsPage />}
        />
      </Route>


      {/* Create University Proposal */}
      <Route
        element={
          <ProtectedRoute
            allowedRoles={[
              "UNIVERSITY_ADMIN",
              "FACULTY",
            ]}
          />
        }
      >
        <Route
          path="/university/proposals/new"
          element={<CreateUniversityProposalPage />}
        />
      </Route>


      {/* University Proposal Details */}
      <Route
        element={
          <ProtectedRoute
            allowedRoles={[
              "UNIVERSITY_ADMIN",
              "FACULTY",
              "STUDENT",
            ]}
          />
        }
      >
        <Route
          path="/university/proposals/:id"
          element={<UniversityProposalDetailsPage />}
        />
      </Route>


      {/* ======================================================
          INDUSTRY ROUTES
      ====================================================== */}

      <Route
        element={
          <ProtectedRoute
            allowedRoles={[
              "INDUSTRY_ADMIN",
              "INDUSTRY_MEMBER",
            ]}
          />
        }
      >
        <Route
          path="/industry/dashboard"
          element={<IndustryDashboard />}
        />

        <Route
          path="/industry/opportunities"
          element={<IndustryOpportunitiesPage />}
        />

        <Route
          path="/industry/opportunities/:proposalId"
          element={<IndustryOpportunityDetailsPage />}
        />

        <Route
          path="/industry/collaborations/new"
          element={<CreateIndustryCollaborationPage />}
        />
      </Route>


      {/* ======================================================
          FALLBACK
      ====================================================== */}

      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />

    </Routes>
  );
}