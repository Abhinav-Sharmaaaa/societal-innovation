import { Navigate, Route, Routes } from "react-router-dom";

// Layout
import AppLayout from "../layouts/AppLayout";

// Admin
import AdminDashboard from "../pages/admin/AdminDashboard";

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
import RFPProposalsPage from "../pages/government/RFPProposalsPage";
import ProposalEvaluationPage from "../pages/government/ProposalEvaluationPage";
import CreateProjectPage from "../pages/government/CreateProjectPage";
import GovernmentCollaborationsPage from "../pages/government/GovernmentCollaborationsPage";
import GovernmentCollaborationDetailsPage from "../pages/government/GovernmentCollaborationDetailsPage";

// Project Execution
import ProjectsPage from "../pages/government/ProjectsPage";
import ProjectDetailsPage from "../pages/government/ProjectDetailsPage";

// University
import UniversityDashboard from "../pages/university/UniversityDashboard";
import UniversityInvitationsPage from "../pages/university/UniversityInvitationsPage";
import CreateUniversityProposalPage from "../pages/university/CreateUniversityProposalPage";
import UniversityMyProposalsPage from "../pages/university/UniversityMyProposalsPage";
import UniversityProposalDetailsPage from "../pages/university/UniversityProposalDetailsPage";
import UniversityCollaborationsPage from "../pages/university/UniversityCollaborationsPage";
import UniversityCollaborationDetailsPage from "../pages/university/UniversityCollaborationDetailsPage";

// Industry
import IndustryDashboard from "../pages/industry/IndustryDashboard";
import IndustryOpportunitiesPage from "../pages/industry/IndustryOpportunitiesPage";
import CreateIndustryCollaborationPage from "../pages/industry/CreateIndustryCollaborationPage";
import IndustryOpportunityDetailsPage from "../pages/industry/IndustryOpportunityDetailsPage";

// Security
import ProtectedRoute from "./ProtectedRoute";


export default function AppRoutes() {
  return (
    <Routes>

      {/* ======================================================
          PUBLIC ROUTES (no navbar)
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
          AUTHENTICATED ROUTES — wrapped in AppLayout (Navbar)
      ====================================================== */}

      <Route element={<AppLayout />}>

        {/* ------------------------------------------------
            SUPER ADMIN ROUTE
        ------------------------------------------------ */}

        <Route
          element={
            <ProtectedRoute
              allowedRoles={["SUPER_ADMIN"]}
            />
          }
        >
          <Route
            path="/admin"
            element={<AdminDashboard />}
          />
        </Route>


        {/* ------------------------------------------------
            CITIZEN ROUTES
        ------------------------------------------------ */}

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


        {/* ------------------------------------------------
            GOVERNMENT ROUTES
        ------------------------------------------------ */}

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

          {/* Proposal Evaluation */}
          <Route
            path="/government/proposals/:id/evaluate"
            element={<ProposalEvaluationPage />}
          />

          {/* Accepted Collaborations */}
          <Route
            path="/government/collaborations"
            element={<GovernmentCollaborationsPage />}
          />

          <Route
            path="/government/collaborations/:id"
            element={<GovernmentCollaborationDetailsPage />}
          />

          {/* Project Creation */}
          <Route
            path="/government/projects/new"
            element={<CreateProjectPage />}
          />

          {/* Project Execution */}
          <Route
            path="/government/projects"
            element={<ProjectsPage />}
          />

          <Route
            path="/government/projects/:id"
            element={<ProjectDetailsPage />}
          />
        </Route>


        {/* ------------------------------------------------
            UNIVERSITY ROUTES
        ------------------------------------------------ */}

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

          <Route
            path="/university/collaborations"
            element={<UniversityCollaborationsPage />}
          />

          <Route
            path="/university/collaborations/:id"
            element={<UniversityCollaborationDetailsPage />}
          />

          <Route
            path="/university/proposals/new"
            element={<CreateUniversityProposalPage />}
          />

          <Route
            path="/university/proposals"
            element={<UniversityMyProposalsPage />}
          />
        </Route>

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


        {/* ------------------------------------------------
            INDUSTRY ROUTES
        ------------------------------------------------ */}

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