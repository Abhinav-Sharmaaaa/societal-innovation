import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  FileCheck2,
  FileText,
  Loader2,
  Milestone,
  Plus,
  RefreshCw,
  Target,
  Upload,
  IndianRupee,
  X,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  getProject,
  getProjectMilestones,
  getProjectDeliverables,
  getProjectFundingSummary,
  getProjectFundingTransactions,
  createProjectFunding,
  approveProjectFunding,
  completeProjectFunding,
  getProjectReports,
  getProjectEvidence,
  createProjectReport,
  reviewProjectReport,
  createProjectEvidence,
  getProjectOutcomes,
  getProjectRisks,

  updateProjectMilestone,

  createProjectDeliverable,
  submitProjectDeliverable,
  reviewProjectDeliverable,

  type Project,
  type ProjectMilestone,
  type ProjectDeliverable,
  type ProjectFundingSummary,
  type ProjectFundingTransaction,
  type ProjectFundingTransactionType,
  type ProjectReport,
  type ProjectOutcome,
  type ProjectRisk,
  type ProjectEvidence as ProjectEvidenceRecord,
  type ProjectEvidenceType,
  type ProjectReportType,
  type ProjectMilestoneStatus,
} from "../../services/projectService";

import "./ProjectPages.css";
import ProjectMilestones from "./project/ProjectMilestones";
import ProjectDeliverables from "./project/ProjectDeliverables";
import ProjectFunding from "./project/ProjectFunding";
import ProjectReports from "./project/ProjectReports";
import ProjectEvidence from "./project/ProjectEvidence";
import ProjectOutcomes from "./project/ProjectOutcomes";
import ProjectRisks from "./project/ProjectRisks";


/* =========================================================
   HELPERS
========================================================= */

function formatDate(value: string | null): string {
  if (!value) return "Not specified";

  return new Date(value).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}


function formatDateTimeLocal(value: string | null): string {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const offset = date.getTimezoneOffset();

  const localDate = new Date(
    date.getTime() - offset * 60 * 1000
  );

  return localDate.toISOString().slice(0, 16);
}


function formatBudget(value: number | null): string {
  if (value === null || value === undefined) {
    return "Not specified";
  }

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}


function label(value: string): string {
  return value.replaceAll("_", " ");
}


function badgeClass(value: string): string {
  return value
    .toLowerCase()
    .replaceAll("_", "-");
}


/* =========================================================
   PAGE
========================================================= */

export default function ProjectDetailsPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const projectId = Number(id);

  /* =======================================================
     PROJECT DATA
  ======================================================= */

  const [project, setProject] =
    useState<Project | null>(null);

  const [milestones, setMilestones] =
    useState<ProjectMilestone[]>([]);

  const [deliverables, setDeliverables] =
    useState<ProjectDeliverable[]>([]);

  const [funding, setFunding] =
    useState<ProjectFundingSummary | null>(null);

  const [fundingTransactions, setFundingTransactions] =
    useState<ProjectFundingTransaction[]>([]);

  const [isCreateFundingOpen, setIsCreateFundingOpen] =
    useState(false);

  const [fundingTransactionType, setFundingTransactionType] =
    useState<ProjectFundingTransactionType>("ALLOCATION");

  const [fundingAmount, setFundingAmount] =
    useState("");

  const [fundingTransactionDate, setFundingTransactionDate] =
    useState("");

  const [fundingDescription, setFundingDescription] =
    useState("");

  const [fundingReference, setFundingReference] =
    useState("");

  const [savingFunding, setSavingFunding] =
    useState(false);

  const [fundingActionId, setFundingActionId] =
    useState<number | null>(null);

  const [fundingError, setFundingError] =
    useState("");

  const [reports, setReports] =
    useState<ProjectReport[]>([]);

  const [evidence, setEvidence] =
    useState<ProjectEvidenceRecord[]>([]);

  const [isCreateReportOpen, setIsCreateReportOpen] =
    useState(false);

  const [reportType, setReportType] =
    useState<ProjectReportType>("PROGRESS");

  const [reportMilestoneId, setReportMilestoneId] =
    useState("");

  const [reportTitle, setReportTitle] =
    useState("");

  const [reportSummary, setReportSummary] =
    useState("");

  const [reportFindings, setReportFindings] =
    useState("");

  const [reportChallenges, setReportChallenges] =
    useState("");

  const [reportNextSteps, setReportNextSteps] =
    useState("");

  const [savingReport, setSavingReport] =
    useState(false);

  const [reportError, setReportError] =
    useState("");

  const [reviewingReport, setReviewingReport] =
    useState<ProjectReport | null>(null);

  const [reportReviewDecision, setReportReviewDecision] =
    useState<"APPROVED" | "REJECTED">("APPROVED");

  const [reportReviewRemarks, setReportReviewRemarks] =
    useState("");

  const [savingReportReview, setSavingReportReview] =
    useState(false);

  const [reportReviewError, setReportReviewError] =
    useState("");

  const [isCreateEvidenceOpen, setIsCreateEvidenceOpen] =
    useState(false);

  const [evidenceReportId, setEvidenceReportId] =
    useState("");

  const [evidenceType, setEvidenceType] =
    useState<ProjectEvidenceType>("DOCUMENT");

  const [evidenceTitle, setEvidenceTitle] =
    useState("");

  const [evidenceFileUrl, setEvidenceFileUrl] =
    useState("");

  const [evidenceExternalUrl, setEvidenceExternalUrl] =
    useState("");

  const [evidenceDescription, setEvidenceDescription] =
    useState("");

  const [savingEvidence, setSavingEvidence] =
    useState(false);

  const [evidenceError, setEvidenceError] =
    useState("");

  const [outcomes, setOutcomes] =
    useState<ProjectOutcome[]>([]);

  const [risks, setRisks] =
    useState<ProjectRisk[]>([]);

  /* =======================================================
     PAGE STATE
  ======================================================= */

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState("");


  /* =======================================================
     MILESTONE EDITOR
  ======================================================= */

  const [editingMilestone, setEditingMilestone] =
    useState<ProjectMilestone | null>(null);

  const [milestoneProgress, setMilestoneProgress] =
    useState(0);

  const [milestoneStatus, setMilestoneStatus] =
    useState<ProjectMilestoneStatus>(
      "NOT_STARTED"
    );

  const [milestoneRemarks, setMilestoneRemarks] =
    useState("");

  const [savingMilestone, setSavingMilestone] =
    useState(false);

  const [milestoneError, setMilestoneError] =
    useState("");


  /* =======================================================
     CREATE DELIVERABLE
  ======================================================= */

  const [isCreateDeliverableOpen, setIsCreateDeliverableOpen] =
    useState(false);

  const [deliverableMilestoneId, setDeliverableMilestoneId] =
    useState<number | "">("");

  const [deliverableTitle, setDeliverableTitle] =
    useState("");

  const [deliverableDescription, setDeliverableDescription] =
    useState("");

  const [deliverableDueDate, setDeliverableDueDate] =
    useState("");

  const [deliverableMandatory, setDeliverableMandatory] =
    useState(true);

  const [savingDeliverable, setSavingDeliverable] =
    useState(false);

  const [deliverableCreateError, setDeliverableCreateError] =
    useState("");


  /* =======================================================
     SUBMIT DELIVERABLE
  ======================================================= */

  const [submittingDeliverable, setSubmittingDeliverable] =
    useState<ProjectDeliverable | null>(null);

  const [submissionReference, setSubmissionReference] =
    useState("");

  const [savingSubmission, setSavingSubmission] =
    useState(false);

  const [submissionError, setSubmissionError] =
    useState("");


  /* =======================================================
     REVIEW DELIVERABLE
  ======================================================= */

  const [reviewingDeliverable, setReviewingDeliverable] =
    useState<ProjectDeliverable | null>(null);

  const [deliverableReviewDecision, setDeliverableReviewDecision] =
    useState<"APPROVED" | "REJECTED">("APPROVED");

  const [deliverableReviewRemarks, setDeliverableReviewRemarks] =
    useState("");

  const [savingDeliverableReview, setSavingDeliverableReview] =
    useState(false);

  const [deliverableReviewError, setDeliverableReviewError] =
    useState("");


  /* =======================================================
     LOAD PROJECT
  ======================================================= */

  const loadProject = useCallback(
    async (isRefresh = false) => {
      if (!Number.isFinite(projectId)) {
        setError("Invalid project ID.");
        setLoading(false);
        return;
      }

      try {
        setError("");

        if (isRefresh) {
          setRefreshing(true);
        } else {
          setLoading(true);
        }

        const [
          projectData,
          milestoneData,
          deliverableData,
          fundingData,
          fundingTransactionData,
          reportData,
          evidenceData,
          outcomeData,
          riskData,
        ] = await Promise.all([
          getProject(projectId),
          getProjectMilestones(projectId),
          getProjectDeliverables(projectId),
          getProjectFundingSummary(projectId),
          getProjectFundingTransactions(projectId),
          getProjectReports(projectId),
          getProjectEvidence(projectId),
          getProjectOutcomes(projectId),
          getProjectRisks(projectId),
        ]);

        setProject(projectData);
        setMilestones(milestoneData);
        setDeliverables(deliverableData);
        setFunding(fundingData);
        setFundingTransactions(fundingTransactionData);
        setReports(reportData);
        setEvidence(evidenceData);
        setOutcomes(outcomeData);
        setRisks(riskData);
      } catch (err) {
        console.error(
          "Failed to load project details:",
          err
        );

        setError(
          "Unable to load the project execution data."
        );
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [projectId]
  );


  useEffect(() => {
    void loadProject();
  }, [loadProject]);


  /* =======================================================
     MILESTONE EDITOR
  ======================================================= */

  const openMilestoneEditor = (
    milestone: ProjectMilestone
  ) => {
    setEditingMilestone(milestone);

    setMilestoneProgress(
      milestone.progress_percentage
    );

    setMilestoneStatus(
      milestone.status
    );

    setMilestoneRemarks(
      milestone.completion_remarks || ""
    );

    setMilestoneError("");
  };


  const closeMilestoneEditor = () => {
    if (savingMilestone) {
      return;
    }

    setEditingMilestone(null);
    setMilestoneError("");
  };


  const saveMilestone = async () => {
    if (!editingMilestone) {
      return;
    }

    if (
      milestoneProgress < 0 ||
      milestoneProgress > 100
    ) {
      setMilestoneError(
        "Progress must be between 0 and 100."
      );
      return;
    }

    try {
      setSavingMilestone(true);
      setMilestoneError("");

      await updateProjectMilestone(
        editingMilestone.id,
        {
          progress_percentage:
            milestoneStatus === "COMPLETED"
              ? 100
              : milestoneProgress,

          status: milestoneStatus,

          completion_remarks:
            milestoneRemarks.trim() ||
            undefined,
        }
      );

      setEditingMilestone(null);

      await loadProject(true);
    } catch (err) {
      console.error(
        "Failed to update milestone:",
        err
      );

      setMilestoneError(
        "Unable to update milestone. Please try again."
      );
    } finally {
      setSavingMilestone(false);
    }
  };


  /* =======================================================
     CREATE DELIVERABLE
  ======================================================= */

  const openCreateDeliverable = () => {
    setDeliverableMilestoneId(
      milestones[0]?.id ?? ""
    );

    setDeliverableTitle("");
    setDeliverableDescription("");
    setDeliverableDueDate("");
    setDeliverableMandatory(true);
    setDeliverableCreateError("");

    setIsCreateDeliverableOpen(true);
  };


  const closeCreateDeliverable = () => {
    if (savingDeliverable) {
      return;
    }

    setIsCreateDeliverableOpen(false);
    setDeliverableCreateError("");
  };


  const saveNewDeliverable = async () => {
    if (deliverableMilestoneId === "") {
      setDeliverableCreateError(
        "Please select a milestone."
      );
      return;
    }

    if (
      deliverableTitle.trim().length < 5
    ) {
      setDeliverableCreateError(
        "Deliverable title must be at least 5 characters."
      );
      return;
    }

    try {
      setSavingDeliverable(true);
      setDeliverableCreateError("");

      await createProjectDeliverable({
        milestone_id:
          Number(
            deliverableMilestoneId
          ),

        title:
          deliverableTitle.trim(),

        description:
          deliverableDescription.trim() ||
          undefined,

        due_date:
          deliverableDueDate ||
          undefined,

        is_mandatory:
          deliverableMandatory,
      });

      setIsCreateDeliverableOpen(false);

      await loadProject(true);
    } catch (err) {
      console.error(
        "Failed to create deliverable:",
        err
      );

      setDeliverableCreateError(
        "Unable to create deliverable. Please verify the milestone and due date."
      );
    } finally {
      setSavingDeliverable(false);
    }
  };


  /* =======================================================
     SUBMIT DELIVERABLE
  ======================================================= */

  const openSubmitDeliverable = (
    deliverable: ProjectDeliverable
  ) => {
    setSubmittingDeliverable(
      deliverable
    );

    setSubmissionReference(
      ""
    );

    setSubmissionError("");
  };


  const closeSubmitDeliverable = () => {
    if (savingSubmission) {
      return;
    }

    setSubmittingDeliverable(null);
    setSubmissionError("");
  };


  const saveDeliverableSubmission = async () => {
    if (!submittingDeliverable) {
      return;
    }

    if (
      submissionReference.trim().length < 3
    ) {
      setSubmissionError(
        "Submission reference must be at least 3 characters."
      );
      return;
    }

    try {
      setSavingSubmission(true);
      setSubmissionError("");

      await submitProjectDeliverable(
        submittingDeliverable.id,
        {
          submission_reference:
            submissionReference.trim(),
        }
      );

      setSubmittingDeliverable(null);

      await loadProject(true);
    } catch (err) {
      console.error(
        "Failed to submit deliverable:",
        err
      );

      setSubmissionError(
        "Unable to submit deliverable. Please try again."
      );
    } finally {
      setSavingSubmission(false);
    }
  };


  /* =======================================================
     REVIEW DELIVERABLE
  ======================================================= */

  const openReviewDeliverable = (
    deliverable: ProjectDeliverable
  ) => {
    setReviewingDeliverable(
      deliverable
    );

    setDeliverableReviewDecision(
      "APPROVED"
    );

    setDeliverableReviewRemarks("");

    setDeliverableReviewError("");
  };


  const closeReviewDeliverable = () => {
    if (savingDeliverableReview) {
      return;
    }

    setReviewingDeliverable(null);
    setDeliverableReviewError("");
  };


  const saveDeliverableReview = async () => {
    if (!reviewingDeliverable) {
      return;
    }

    try {
      setSavingDeliverableReview(true);
      setDeliverableReviewError("");

      await reviewProjectDeliverable(
        reviewingDeliverable.id,
        {
          decision:
            deliverableReviewDecision,

          review_remarks:
            deliverableReviewRemarks.trim() ||
            undefined,
        }
      );

      setReviewingDeliverable(null);

      await loadProject(true);
    } catch (err) {
      console.error(
        "Failed to review deliverable:",
        err
      );

      setDeliverableReviewError(
        "Unable to review deliverable. Please try again."
      );
    } finally {
      setSavingDeliverableReview(false);
    }
  };


  /* =======================================================
     FUNDING
  ======================================================= */

  const openCreateFunding = () => {
    setFundingTransactionType("ALLOCATION");
    setFundingAmount("");
    setFundingTransactionDate("");
    setFundingDescription("");
    setFundingReference("");
    setFundingError("");
    setIsCreateFundingOpen(true);
  };

  const closeCreateFunding = () => {
    if (savingFunding) {
      return;
    }

    setIsCreateFundingOpen(false);
    setFundingError("");
  };

  const saveFundingTransaction = async () => {
    const amount = Number(fundingAmount);

    if (!Number.isFinite(amount) || amount <= 0) {
      setFundingError(
        "Funding amount must be greater than zero."
      );
      return;
    }

    try {
      setSavingFunding(true);
      setFundingError("");

      await createProjectFunding({
        project_id: projectId,
        transaction_type: fundingTransactionType,
        amount,
        transaction_date:
          fundingTransactionDate || undefined,
        description:
          fundingDescription.trim() || undefined,
        reference_number:
          fundingReference.trim() || undefined,
      });

      setIsCreateFundingOpen(false);

      await loadProject(true);
    } catch (err: any) {
      console.error(
        "Failed to create funding transaction:",
        err
      );

      setFundingError(
        err?.response?.data?.detail ||
        "Unable to create funding transaction. Please try again."
      );
    } finally {
      setSavingFunding(false);
    }
  };

  const approveFunding = async (
    transactionId: number
  ) => {
    try {
      setFundingActionId(transactionId);
      setFundingError("");

      await approveProjectFunding(
        transactionId,
        {
          decision: "APPROVED",
        }
      );

      await loadProject(true);
    } catch (err: any) {
      console.error(
        "Failed to approve funding transaction:",
        err
      );

      setFundingError(
        err?.response?.data?.detail ||
        "Unable to approve funding transaction."
      );
    } finally {
      setFundingActionId(null);
    }
  };

  const rejectFunding = async (
    transactionId: number
  ) => {
    try {
      setFundingActionId(transactionId);
      setFundingError("");

      await approveProjectFunding(
        transactionId,
        {
          decision: "REJECTED",
        }
      );

      await loadProject(true);
    } catch (err: any) {
      console.error(
        "Failed to reject funding transaction:",
        err
      );

      setFundingError(
        err?.response?.data?.detail ||
        "Unable to reject funding transaction."
      );
    } finally {
      setFundingActionId(null);
    }
  };

  const completeFunding = async (
    transactionId: number
  ) => {
    try {
      setFundingActionId(transactionId);
      setFundingError("");

      await completeProjectFunding(
        transactionId
      );

      await loadProject(true);
    } catch (err: any) {
      console.error(
        "Failed to complete funding transaction:",
        err
      );

      setFundingError(
        err?.response?.data?.detail ||
        "Unable to complete funding transaction."
      );
    } finally {
      setFundingActionId(null);
    }
  };

  /* =======================================================
     REPORTS
  ======================================================= */

  const openCreateReport = () => {
    setReportType("PROGRESS");
    setReportMilestoneId("");
    setReportTitle("");
    setReportSummary("");
    setReportFindings("");
    setReportChallenges("");
    setReportNextSteps("");
    setReportError("");
    setIsCreateReportOpen(true);
  };

  const closeCreateReport = () => {
    if (savingReport) return;
    setIsCreateReportOpen(false);
    setReportError("");
  };

  const saveProjectReport = async () => {
    if (reportTitle.trim().length < 3) {
      setReportError("Report title must be at least 3 characters.");
      return;
    }

    if (reportSummary.trim().length < 5) {
      setReportError("Report summary must be at least 5 characters.");
      return;
    }

    try {
      setSavingReport(true);
      setReportError("");

      await createProjectReport({
        project_id: projectId,
        milestone_id: reportMilestoneId ? Number(reportMilestoneId) : undefined,
        report_type: reportType,
        title: reportTitle.trim(),
        summary: reportSummary.trim(),
        findings: reportFindings.trim() || undefined,
        challenges: reportChallenges.trim() || undefined,
        next_steps: reportNextSteps.trim() || undefined,
      });

      setIsCreateReportOpen(false);
      await loadProject(true);
    } catch (err: any) {
      console.error("Failed to create project report:", err);
      setReportError(
        err?.response?.data?.detail ||
        "Unable to create report. Please try again."
      );
    } finally {
      setSavingReport(false);
    }
  };

  const openReviewReport = (report: ProjectReport) => {
    setReviewingReport(report);
    setReportReviewDecision("APPROVED");
    setReportReviewRemarks("");
    setReportReviewError("");
  };

  const closeReviewReport = () => {
    if (savingReportReview) return;
    setReviewingReport(null);
    setReportReviewError("");
  };

  const saveReportReview = async () => {
    if (!reviewingReport) return;

    try {
      setSavingReportReview(true);
      setReportReviewError("");

      await reviewProjectReport(
        reviewingReport.id,
        {
          decision: reportReviewDecision,
          review_remarks: reportReviewRemarks.trim() || undefined,
        }
      );

      setReviewingReport(null);
      await loadProject(true);
    } catch (err: any) {
      console.error("Failed to review project report:", err);
      setReportReviewError(
        err?.response?.data?.detail ||
        "Unable to review report. Please try again."
      );
    } finally {
      setSavingReportReview(false);
    }
  };


  /* =======================================================
     EVIDENCE
  ======================================================= */

  const openCreateEvidence = () => {
    setEvidenceReportId("");
    setEvidenceType("DOCUMENT");
    setEvidenceTitle("");
    setEvidenceFileUrl("");
    setEvidenceExternalUrl("");
    setEvidenceDescription("");
    setEvidenceError("");
    setIsCreateEvidenceOpen(true);
  };

  const closeCreateEvidence = () => {
    if (savingEvidence) return;
    setIsCreateEvidenceOpen(false);
    setEvidenceError("");
  };

  const saveProjectEvidence = async () => {
    if (evidenceTitle.trim().length < 3) {
      setEvidenceError("Evidence title must be at least 3 characters.");
      return;
    }

    if (!evidenceFileUrl.trim() && !evidenceExternalUrl.trim()) {
      setEvidenceError("Provide either a file URL or an external URL.");
      return;
    }

    try {
      setSavingEvidence(true);
      setEvidenceError("");

      await createProjectEvidence({
        project_id: projectId,
        report_id: evidenceReportId ? Number(evidenceReportId) : undefined,
        evidence_type: evidenceType,
        title: evidenceTitle.trim(),
        file_url: evidenceFileUrl.trim() || undefined,
        external_url: evidenceExternalUrl.trim() || undefined,
        description: evidenceDescription.trim() || undefined,
      });

      setIsCreateEvidenceOpen(false);
      await loadProject(true);
    } catch (err: any) {
      console.error("Failed to create project evidence:", err);
      setEvidenceError(
        err?.response?.data?.detail ||
        "Unable to add evidence. Please try again."
      );
    } finally {
      setSavingEvidence(false);
    }
  };


  /* =======================================================
     SUMMARY
  ======================================================= */

  const completedMilestones = useMemo(
    () =>
      milestones.filter(
        (item) =>
          item.status === "COMPLETED"
      ).length,
    [milestones]
  );


  const approvedDeliverables = useMemo(
    () =>
      deliverables.filter(
        (item) =>
          item.status === "APPROVED"
      ).length,
    [deliverables]
  );


  const verifiedOutcomes = useMemo(
    () =>
      outcomes.filter(
        (item) =>
          item.status === "VERIFIED"
      ).length,
    [outcomes]
  );


  const latestRisk =
    risks[0] ?? null;


  /* =======================================================
     LOADING
  ======================================================= */

  if (loading) {
    return (
      <div className="project-page">

        <div className="project-loading">

          <Loader2
            className="spin"
            size={28}
          />

          <p>
            Loading project execution data...
          </p>

        </div>

      </div>
    );
  }


  /* =======================================================
     PROJECT NOT FOUND
  ======================================================= */

  if (!project) {
    return (
      <div className="project-page">

        <div className="project-error-panel">

          <AlertCircle size={30} />

          <h2>
            Project unavailable
          </h2>

          <p>
            {error ||
              "The requested project could not be loaded."}
          </p>

          <button
            type="button"
            className="project-primary-button"
            onClick={() =>
              navigate(
                "/government/projects"
              )
            }
          >
            <ArrowLeft size={16} />

            Back to Projects
          </button>

        </div>

      </div>
    );
  }


  /* =======================================================
     RENDER
  ======================================================= */

  return (
    <div className="project-page">

      {/* ===================================================
          TOP BAR
      =================================================== */}

      <div className="project-details-topbar">

        <button
          type="button"
          className="project-back-button"
          onClick={() =>
            navigate(
              "/government/projects"
            )
          }
        >
          <ArrowLeft size={17} />
          Projects
        </button>


        <button
          type="button"
          className="project-secondary-button"
          onClick={() =>
            void loadProject(true)
          }
          disabled={refreshing}
        >
          <RefreshCw
            size={16}
            className={
              refreshing
                ? "spin"
                : ""
            }
          />

          Refresh
        </button>

      </div>


      {/* ===================================================
          ERROR
      =================================================== */}

      {error && (
        <div className="project-error-banner">

          <AlertCircle size={18} />

          <span>
            {error}
          </span>

        </div>
      )}


      {/* ===================================================
          PROJECT HEADER
      =================================================== */}

      <section className="project-hero">

        <div className="project-hero-main">

          <div className="project-eyebrow">
            PROJECT #{project.id}
          </div>

          <h1>
            {project.title}
          </h1>

          <p>
            {project.description ||
              "No project description available."}
          </p>


          <div className="project-badge-row">

            <span
              className={`project-status-badge ${badgeClass(
                project.status
              )}`}
            >
              {label(project.status)}
            </span>


            <span
              className={`project-health-badge ${badgeClass(
                project.health
              )}`}
            >
              {label(project.health)}
            </span>

          </div>

        </div>


        <div className="project-hero-progress">

          <div className="project-progress-circle">

            <strong>
              {Math.round(
                project.progress_percentage
              )}
              %
            </strong>

            <span>
              Progress
            </span>

          </div>

        </div>

      </section>


      {/* ===================================================
          PROJECT METADATA
      =================================================== */}

      <div className="project-overview-grid">

        <div className="project-overview-card">

          <span>
            Project Status
          </span>

          <strong>
            {label(project.status)}
          </strong>

        </div>


        <div className="project-overview-card">

          <span>
            Project Health
          </span>

          <strong>
            {label(project.health)}
          </strong>

        </div>


        <div className="project-overview-card">

          <span>
            Total Budget
          </span>

          <strong>
            {formatBudget(
              project.total_budget
            )}
          </strong>

        </div>


        <div className="project-overview-card">

          <span>
            Start Date
          </span>

          <strong>
            {formatDate(
              project.start_date
            )}
          </strong>

        </div>


        <div className="project-overview-card">

          <span>
            Target Completion
          </span>

          <strong>
            {formatDate(
              project.target_completion_date
            )}
          </strong>

        </div>


        <div className="project-overview-card">

          <span>
            Actual Completion
          </span>

          <strong>
            {formatDate(
              project.actual_completion_date
            )}
          </strong>

        </div>

      </div>


      {/* ===================================================
          EXECUTION SUMMARY
      =================================================== */}

      <section className="project-section">

        <div className="project-section-heading">

          <div>

            <span className="project-section-eyebrow">
              EXECUTION
            </span>

            <h2>
              Project execution overview
            </h2>

            <p>
              Current execution state across
              milestones, deliverables,
              funding and impact.
            </p>

          </div>

        </div>


        <div className="project-execution-summary">

          <SummaryMetric
            icon={
              <Milestone size={18} />
            }
            label="Milestones"
            value={`${completedMilestones}/${milestones.length}`}
            subtitle="completed"
          />


          <SummaryMetric
            icon={
              <FileCheck2 size={18} />
            }
            label="Deliverables"
            value={`${approvedDeliverables}/${deliverables.length}`}
            subtitle="approved"
          />


          <SummaryMetric
            icon={
              <FileText size={18} />
            }
            label="Reports"
            value={String(
              reports.length
            )}
            subtitle="submitted"
          />


          <SummaryMetric
            icon={
              <Target size={18} />
            }
            label="Outcomes"
            value={`${verifiedOutcomes}/${outcomes.length}`}
            subtitle="verified"
          />

        </div>

      </section>


      {/* ===================================================
          MILESTONES
      =================================================== */}

      <ProjectMilestones milestones={milestones} onUpdate={openMilestoneEditor} />


      {/* ===================================================
          DELIVERABLES + FUNDING
      =================================================== */}

      <div className="project-two-column-grid">
        <ProjectDeliverables
          project={project}
          milestones={milestones}
          deliverables={deliverables}
          onCreate={openCreateDeliverable}
          onSubmit={openSubmitDeliverable}
          onReview={openReviewDeliverable}
        />
        <ProjectFunding
          projectStatus={project.status}
          funding={funding}
          transactions={fundingTransactions}
          fundingError={fundingError}
          actionId={fundingActionId}
          onCreate={openCreateFunding}
          onApprove={approveFunding}
          onReject={rejectFunding}
          onComplete={completeFunding}
        />
      </div>


      {/* ===================================================
          REPORTS + EVIDENCE
      =================================================== */}

      <div className="project-two-column-grid">
        <ProjectReports
          reports={reports}
          onCreate={openCreateReport}
          onReview={openReviewReport}
        />
        <ProjectEvidence
          evidence={evidence}
          onCreate={openCreateEvidence}
        />
      </div>


      <ProjectOutcomes outcomes={outcomes} />


      <ProjectRisks latestRisk={latestRisk} />


      {/* ===================================================
          PROJECT OBJECTIVES
      =================================================== */}

      {(
        project.objectives ||
        project.expected_outcomes
      ) && (
          <section className="project-section">

            <div className="project-two-column-grid">

              {project.objectives && (
                <div className="project-text-card">

                  <div className="project-section-eyebrow">
                    OBJECTIVES
                  </div>

                  <h3>
                    Project objectives
                  </h3>

                  <p>
                    {project.objectives}
                  </p>

                </div>
              )}


              {project.expected_outcomes && (
                <div className="project-text-card">

                  <div className="project-section-eyebrow">
                    EXPECTED IMPACT
                  </div>

                  <h3>
                    Expected outcomes
                  </h3>

                  <p>
                    {
                      project.expected_outcomes
                    }
                  </p>

                </div>
              )}

            </div>

          </section>
        )}


      {/* ===================================================
          CREATE REPORT MODAL
      =================================================== */}

      {isCreateReportOpen && (
        <div
          className="project-modal-overlay"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget && !savingReport) {
              closeCreateReport();
            }
          }}
        >
          <div className="project-modal" role="dialog" aria-modal="true" aria-labelledby="create-report-title">
            <div className="project-modal-header">
              <div>
                <span className="project-section-eyebrow">REPORTING</span>
                <h2 id="create-report-title">Submit project report</h2>
              </div>
              <button type="button" className="project-modal-close" onClick={closeCreateReport} disabled={savingReport} aria-label="Close">
                <X size={18} />
              </button>
            </div>

            <div className="project-modal-body">
              <div className="project-form-field">
                <label htmlFor="report-type">Report type</label>
                <select id="report-type" value={reportType} onChange={(event) => setReportType(event.target.value as ProjectReportType)}>
                  <option value="PROGRESS">Progress</option>
                  <option value="MILESTONE">Milestone</option>
                  <option value="FINANCIAL">Financial</option>
                  <option value="PILOT">Pilot</option>
                  <option value="FINAL">Final</option>
                </select>
              </div>

              <div className="project-form-field">
                <label htmlFor="report-milestone">Related milestone (optional)</label>
                <select id="report-milestone" value={reportMilestoneId} onChange={(event) => setReportMilestoneId(event.target.value)}>
                  <option value="">Project-level report</option>
                  {milestones.map((milestone) => (
                    <option key={milestone.id} value={milestone.id}>
                      {milestone.title}
                    </option>
                  ))}
                </select>
              </div>

              <div className="project-form-field">
                <label htmlFor="report-title">Title</label>
                <input id="report-title" value={reportTitle} onChange={(event) => setReportTitle(event.target.value)} placeholder="e.g. Sprint 2 Progress Report" />
              </div>

              <div className="project-form-field">
                <label htmlFor="report-summary">Summary</label>
                <textarea id="report-summary" rows={4} value={reportSummary} onChange={(event) => setReportSummary(event.target.value)} placeholder="Summarize the work completed and current status..." />
              </div>

              <div className="project-form-field">
                <label htmlFor="report-findings">Findings (optional)</label>
                <textarea id="report-findings" rows={3} value={reportFindings} onChange={(event) => setReportFindings(event.target.value)} placeholder="Key findings, observations or results..." />
              </div>

              <div className="project-form-field">
                <label htmlFor="report-challenges">Challenges (optional)</label>
                <textarea id="report-challenges" rows={3} value={reportChallenges} onChange={(event) => setReportChallenges(event.target.value)} placeholder="Mention blockers, risks or implementation challenges..." />
              </div>

              <div className="project-form-field">
                <label htmlFor="report-next-steps">Next steps (optional)</label>
                <textarea id="report-next-steps" rows={3} value={reportNextSteps} onChange={(event) => setReportNextSteps(event.target.value)} placeholder="Describe planned next activities..." />
              </div>

              {reportError && (
                <div className="project-form-error"><AlertCircle size={16} />{reportError}</div>
              )}
            </div>

            <div className="project-modal-footer">
              <button type="button" className="project-secondary-button" onClick={closeCreateReport} disabled={savingReport}>Cancel</button>
              <button type="button" className="project-primary-button" onClick={() => void saveProjectReport()} disabled={savingReport}>
                {savingReport ? <Loader2 size={16} className="spin" /> : <FileCheck2 size={16} />}
                Submit Report
              </button>
            </div>
          </div>
        </div>
      )}


      {/* ===================================================
          REVIEW REPORT MODAL
      =================================================== */}

      {reviewingReport && (
        <div
          className="project-modal-overlay"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget && !savingReportReview) {
              closeReviewReport();
            }
          }}
        >
          <div className="project-modal" role="dialog" aria-modal="true" aria-labelledby="review-report-title">
            <div className="project-modal-header">
              <div>
                <span className="project-section-eyebrow">GOVERNMENT REVIEW</span>
                <h2 id="review-report-title">Review report</h2>
              </div>
              <button type="button" className="project-modal-close" onClick={closeReviewReport} disabled={savingReportReview} aria-label="Close">
                <X size={18} />
              </button>
            </div>

            <div className="project-modal-body">
              <div className="project-form-info">
                <strong>{reviewingReport.title}</strong>
                <p>{reviewingReport.summary}</p>
                
                {evidence.filter(e => e.report_id === reviewingReport.id).length > 0 && (
                  <div style={{ marginTop: "16px" }}>
                    <strong>Attached Evidence:</strong>
                    <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "8px" }}>
                      {evidence.filter(e => e.report_id === reviewingReport.id).map(item => (
                        <div key={item.id} style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                          {item.evidence_type === "IMAGE" && (item.external_url || item.file_url) && (
                            <img
                              src={item.external_url || item.file_url || undefined}
                              alt={item.title}
                              style={{ width: "100%", maxHeight: "300px", objectFit: "cover", borderRadius: "8px" }}
                            />
                          )}
                          <a 
                            href={item.external_url || item.file_url || "#"} 
                            target="_blank" 
                            rel="noreferrer"
                            style={{ fontSize: "0.875rem", color: "#3b82f6", textDecoration: "underline" }}
                          >
                            View {item.title}
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="project-form-field">
                <label htmlFor="report-review-decision">Decision</label>
                <select id="report-review-decision" value={reportReviewDecision} onChange={(event) => setReportReviewDecision(event.target.value as "APPROVED" | "REJECTED")}>
                  <option value="APPROVED">Approve</option>
                  <option value="REJECTED">Reject</option>
                </select>
              </div>

              <div className="project-form-field">
                <label htmlFor="report-review-remarks">Review remarks</label>
                <textarea id="report-review-remarks" rows={4} value={reportReviewRemarks} onChange={(event) => setReportReviewRemarks(event.target.value)} placeholder="Add review remarks or required corrections..." />
              </div>

              {reportReviewError && (
                <div className="project-form-error"><AlertCircle size={16} />{reportReviewError}</div>
              )}
            </div>

            <div className="project-modal-footer">
              <button type="button" className="project-secondary-button" onClick={closeReviewReport} disabled={savingReportReview}>Cancel</button>
              <button type="button" className="project-primary-button" onClick={() => void saveReportReview()} disabled={savingReportReview}>
                {savingReportReview ? <Loader2 size={16} className="spin" /> : <CheckCircle2 size={16} />}
                Save Review
              </button>
            </div>
          </div>
        </div>
      )}


      {/* ===================================================
          CREATE EVIDENCE MODAL
      =================================================== */}

      {isCreateEvidenceOpen && (
        <div
          className="project-modal-overlay"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget && !savingEvidence) {
              closeCreateEvidence();
            }
          }}
        >
          <div className="project-modal" role="dialog" aria-modal="true" aria-labelledby="create-evidence-title">
            <div className="project-modal-header">
              <div>
                <span className="project-section-eyebrow">EVIDENCE</span>
                <h2 id="create-evidence-title">Add project evidence</h2>
              </div>
              <button type="button" className="project-modal-close" onClick={closeCreateEvidence} disabled={savingEvidence} aria-label="Close">
                <X size={18} />
              </button>
            </div>

            <div className="project-modal-body">
              <div className="project-form-field">
                <label htmlFor="evidence-type">Evidence type</label>
                <select id="evidence-type" value={evidenceType} onChange={(event) => setEvidenceType(event.target.value as ProjectEvidenceType)}>
                  <option value="DOCUMENT">Document</option>
                  <option value="IMAGE">Image</option>
                  <option value="VIDEO">Video</option>
                  <option value="DATASET">Dataset</option>
                  <option value="LINK">Link</option>
                </select>
              </div>

              <div className="project-form-field">
                <label htmlFor="evidence-report">Attach to report (optional)</label>
                <select id="evidence-report" value={evidenceReportId} onChange={(event) => setEvidenceReportId(event.target.value)}>
                  <option value="">Project-level evidence</option>
                  {reports.map((report) => (
                    <option key={report.id} value={report.id}>
                      {report.title}
                    </option>
                  ))}
                </select>
              </div>

              <div className="project-form-field">
                <label htmlFor="evidence-title">Title</label>
                <input id="evidence-title" value={evidenceTitle} onChange={(event) => setEvidenceTitle(event.target.value)} placeholder="e.g. Pilot test photos" />
              </div>

              <div className="project-form-field">
                <label htmlFor="evidence-file-url">File URL (optional)</label>
                <input id="evidence-file-url" value={evidenceFileUrl} onChange={(event) => setEvidenceFileUrl(event.target.value)} placeholder="https://..." />
              </div>

              <div className="project-form-field">
                <label htmlFor="evidence-external-url">External URL (optional)</label>
                <input id="evidence-external-url" value={evidenceExternalUrl} onChange={(event) => setEvidenceExternalUrl(event.target.value)} placeholder="https://drive.google.com/..." />
              </div>

              <div className="project-form-field">
                <label htmlFor="evidence-description">Description (optional)</label>
                <textarea id="evidence-description" rows={4} value={evidenceDescription} onChange={(event) => setEvidenceDescription(event.target.value)} placeholder="Explain what this evidence demonstrates..." />
              </div>

              {evidenceError && (
                <div className="project-form-error"><AlertCircle size={16} />{evidenceError}</div>
              )}
            </div>

            <div className="project-modal-footer">
              <button type="button" className="project-secondary-button" onClick={closeCreateEvidence} disabled={savingEvidence}>Cancel</button>
              <button type="button" className="project-primary-button" onClick={() => void saveProjectEvidence()} disabled={savingEvidence}>
                {savingEvidence ? <Loader2 size={16} className="spin" /> : <Upload size={16} />}
                Add Evidence
              </button>
            </div>
          </div>
        </div>
      )}


      {/* ===================================================
          MILESTONE EDIT MODAL
      =================================================== */}

      {editingMilestone && (
        <div
          className="project-modal-overlay"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget &&
              !savingMilestone
            ) {
              closeMilestoneEditor();
            }
          }}
        >

          <div
            className="project-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="milestone-editor-title"
          >

            <div className="project-modal-header">

              <div>

                <span className="project-section-eyebrow">
                  MILESTONE UPDATE
                </span>

                <h2 id="milestone-editor-title">
                  {
                    editingMilestone.title
                  }
                </h2>

              </div>


              <button
                type="button"
                className="project-modal-close"
                onClick={
                  closeMilestoneEditor
                }
                disabled={savingMilestone}
                aria-label="Close"
              >
                ×
              </button>

            </div>


            <div className="project-modal-body">

              <div className="project-form-field">

                <label htmlFor="milestone-progress">
                  Progress
                </label>

                <div className="project-progress-input-row">

                  <input
                    id="milestone-progress"
                    type="range"
                    min="0"
                    max="100"
                    value={
                      milestoneProgress
                    }
                    onChange={(event) =>
                      setMilestoneProgress(
                        Number(
                          event.target.value
                        )
                      )
                    }
                  />


                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={
                      milestoneProgress
                    }
                    onChange={(event) => {
                      const rawValue =
                        Number(
                          event.target.value
                        );

                      if (
                        Number.isNaN(
                          rawValue
                        )
                      ) {
                        setMilestoneProgress(
                          0
                        );
                        return;
                      }

                      setMilestoneProgress(
                        Math.min(
                          100,
                          Math.max(
                            0,
                            rawValue
                          )
                        )
                      );
                    }}
                  />

                  <span>
                    %
                  </span>

                </div>

              </div>


              <div className="project-form-field">

                <label htmlFor="milestone-status">
                  Status
                </label>

                <select
                  id="milestone-status"
                  value={
                    milestoneStatus
                  }
                  onChange={(event) =>
                    setMilestoneStatus(
                      event.target
                        .value as ProjectMilestoneStatus
                    )
                  }
                >

                  <option value="NOT_STARTED">
                    Not Started
                  </option>

                  <option value="IN_PROGRESS">
                    In Progress
                  </option>

                  <option value="COMPLETED">
                    Completed
                  </option>

                  <option value="DELAYED">
                    Delayed
                  </option>

                  <option value="BLOCKED">
                    Blocked
                  </option>

                </select>

              </div>


              <div className="project-form-field">

                <label htmlFor="milestone-remarks">
                  Completion / Update Remarks
                </label>

                <textarea
                  id="milestone-remarks"
                  rows={4}
                  value={
                    milestoneRemarks
                  }
                  onChange={(event) =>
                    setMilestoneRemarks(
                      event.target.value
                    )
                  }
                  placeholder="Add relevant progress or completion remarks..."
                />

              </div>


              {milestoneStatus ===
                "COMPLETED" && (
                  <div className="project-form-info">
                    Completing this milestone
                    will set its progress to
                    100% automatically.
                  </div>
                )}


              {milestoneError && (
                <div className="project-form-error">

                  <AlertCircle
                    size={16}
                  />

                  <span>
                    {milestoneError}
                  </span>

                </div>
              )}

            </div>


            <div className="project-modal-footer">

              <button
                type="button"
                className="project-secondary-button"
                onClick={
                  closeMilestoneEditor
                }
                disabled={savingMilestone}
              >
                Cancel
              </button>


              <button
                type="button"
                className="project-primary-button"
                onClick={() =>
                  void saveMilestone()
                }
                disabled={savingMilestone}
              >

                {savingMilestone ? (
                  <>
                    <Loader2
                      size={16}
                      className="spin"
                    />

                    Saving...
                  </>
                ) : (
                  <>
                    <CheckCircle2
                      size={16}
                    />

                    Save Milestone
                  </>
                )}

              </button>

            </div>

          </div>

        </div>
      )}


      {/* ===================================================
          CREATE DELIVERABLE MODAL
      =================================================== */}

      {isCreateDeliverableOpen && (
        <div
          className="project-modal-overlay"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget &&
              !savingDeliverable
            ) {
              closeCreateDeliverable();
            }
          }}
        >

          <div
            className="project-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-deliverable-title"
          >

            <div className="project-modal-header">

              <div>

                <span className="project-section-eyebrow">
                  NEW DELIVERABLE
                </span>

                <h2 id="create-deliverable-title">
                  Add project deliverable
                </h2>

              </div>


              <button
                type="button"
                className="project-modal-close"
                onClick={
                  closeCreateDeliverable
                }
                disabled={savingDeliverable}
                aria-label="Close"
              >
                ×
              </button>

            </div>


            <div className="project-modal-body">

              <div className="project-form-field">

                <label htmlFor="deliverable-milestone">
                  Milestone
                </label>

                <select
                  id="deliverable-milestone"
                  value={
                    deliverableMilestoneId
                  }
                  onChange={(event) =>
                    setDeliverableMilestoneId(
                      event.target.value
                        ? Number(
                          event.target.value
                        )
                        : ""
                    )
                  }
                >

                  <option value="">
                    Select milestone
                  </option>

                  {milestones.map(
                    (milestone) => (
                      <option
                        key={milestone.id}
                        value={milestone.id}
                      >
                        {milestone.sequence_number}.{" "}
                        {milestone.title}
                      </option>
                    )
                  )}

                </select>

              </div>


              <div className="project-form-field">

                <label htmlFor="deliverable-title">
                  Title
                </label>

                <input
                  id="deliverable-title"
                  type="text"
                  value={
                    deliverableTitle
                  }
                  onChange={(event) =>
                    setDeliverableTitle(
                      event.target.value
                    )
                  }
                  placeholder="e.g. Prototype technical documentation"
                />

              </div>


              <div className="project-form-field">

                <label htmlFor="deliverable-description">
                  Description
                </label>

                <textarea
                  id="deliverable-description"
                  rows={4}
                  value={
                    deliverableDescription
                  }
                  onChange={(event) =>
                    setDeliverableDescription(
                      event.target.value
                    )
                  }
                  placeholder="Describe what this deliverable should contain..."
                />

              </div>


              <div className="project-form-field">

                <label htmlFor="deliverable-due-date">
                  Due Date
                </label>

                <input
                  id="deliverable-due-date"
                  type="datetime-local"
                  value={
                    deliverableDueDate
                  }
                  min={formatDateTimeLocal(
                    milestones.find(
                      (item) =>
                        item.id ===
                        deliverableMilestoneId
                    )?.start_date ||
                    null
                  )}
                  max={formatDateTimeLocal(
                    milestones.find(
                      (item) =>
                        item.id ===
                        deliverableMilestoneId
                    )?.due_date ||
                    null
                  )}
                  onChange={(event) =>
                    setDeliverableDueDate(
                      event.target.value
                    )
                  }
                />

                <small className="project-form-hint">
                  The due date must fall within
                  the selected milestone period.
                </small>

              </div>


              <label className="project-checkbox-field">

                <input
                  type="checkbox"
                  checked={
                    deliverableMandatory
                  }
                  onChange={(event) =>
                    setDeliverableMandatory(
                      event.target.checked
                    )
                  }
                />

                <span>
                  Mark as mandatory deliverable
                </span>

              </label>


              {deliverableCreateError && (
                <div className="project-form-error">

                  <AlertCircle
                    size={16}
                  />

                  <span>
                    {
                      deliverableCreateError
                    }
                  </span>

                </div>
              )}

            </div>


            <div className="project-modal-footer">

              <button
                type="button"
                className="project-secondary-button"
                onClick={
                  closeCreateDeliverable
                }
                disabled={
                  savingDeliverable
                }
              >
                Cancel
              </button>


              <button
                type="button"
                className="project-primary-button"
                onClick={() =>
                  void saveNewDeliverable()
                }
                disabled={
                  savingDeliverable
                }
              >

                {savingDeliverable ? (
                  <>
                    <Loader2
                      size={16}
                      className="spin"
                    />

                    Creating...
                  </>
                ) : (
                  <>
                    <Plus size={16} />

                    Create Deliverable
                  </>
                )}

              </button>

            </div>

          </div>

        </div>
      )}


      {/* ===================================================
          SUBMIT DELIVERABLE MODAL
      =================================================== */}

      {submittingDeliverable && (
        <div
          className="project-modal-overlay"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget &&
              !savingSubmission
            ) {
              closeSubmitDeliverable();
            }
          }}
        >

          <div
            className="project-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="submit-deliverable-title"
          >

            <div className="project-modal-header">

              <div>

                <span className="project-section-eyebrow">
                  SUBMIT DELIVERABLE
                </span>

                <h2 id="submit-deliverable-title">
                  {
                    submittingDeliverable.title
                  }
                </h2>

              </div>


              <button
                type="button"
                className="project-modal-close"
                onClick={
                  closeSubmitDeliverable
                }
                disabled={savingSubmission}
                aria-label="Close"
              >
                ×
              </button>

            </div>


            <div className="project-modal-body">

              <div className="project-form-field">

                <label htmlFor="submission-reference">
                  Submission Reference
                </label>

                <input
                  id="submission-reference"
                  type="text"
                  value={
                    submissionReference
                  }
                  onChange={(event) =>
                    setSubmissionReference(
                      event.target.value
                    )
                  }
                  placeholder="e.g. GitHub URL, document reference, report ID or deployment reference"
                />

                <small className="project-form-hint">
                  Provide a reference that allows
                  the reviewing authority to locate
                  the submitted work.
                </small>

              </div>


              {submissionError && (
                <div className="project-form-error">

                  <AlertCircle
                    size={16}
                  />

                  <span>
                    {submissionError}
                  </span>

                </div>
              )}

            </div>


            <div className="project-modal-footer">

              <button
                type="button"
                className="project-secondary-button"
                onClick={
                  closeSubmitDeliverable
                }
                disabled={
                  savingSubmission
                }
              >
                Cancel
              </button>


              <button
                type="button"
                className="project-primary-button"
                onClick={() =>
                  void saveDeliverableSubmission()
                }
                disabled={
                  savingSubmission
                }
              >

                {savingSubmission ? (
                  <>
                    <Loader2
                      size={16}
                      className="spin"
                    />

                    Submitting...
                  </>
                ) : (
                  <>
                    <Upload size={16} />

                    Submit Deliverable
                  </>
                )}

              </button>

            </div>

          </div>

        </div>
      )}


      {/* ===================================================
          CREATE FUNDING TRANSACTION MODAL
      =================================================== */}

      {isCreateFundingOpen && (
        <div
          className="project-modal-overlay"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget &&
              !savingFunding
            ) {
              closeCreateFunding();
            }
          }}
        >
          <div
            className="project-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-funding-title"
          >

            <div className="project-modal-header">

              <div>
                <span className="project-section-eyebrow">
                  NEW FUNDING TRANSACTION
                </span>

                <h2 id="create-funding-title">
                  Add project funding
                </h2>
              </div>

              <button
                type="button"
                className="project-modal-close"
                onClick={closeCreateFunding}
                disabled={savingFunding}
                aria-label="Close"
              >
                <X size={18} />
              </button>

            </div>

            <div className="project-modal-body">

              <div className="project-form-field">

                <label htmlFor="funding-transaction-type">
                  Transaction Type
                </label>

                <select
                  id="funding-transaction-type"
                  value={
                    fundingTransactionType
                  }
                  onChange={(event) =>
                    setFundingTransactionType(
                      event.target
                        .value as ProjectFundingTransactionType
                    )
                  }
                >
                  <option value="ALLOCATION">
                    Allocation
                  </option>

                  <option value="DISBURSEMENT">
                    Disbursement
                  </option>

                  <option value="UTILIZATION">
                    Utilization
                  </option>

                  <option value="REFUND">
                    Refund
                  </option>
                </select>

              </div>

              <div className="project-form-field">

                <label htmlFor="funding-amount">
                  Amount
                </label>

                <div className="project-input-with-icon">
                  <IndianRupee size={16} />

                  <input
                    id="funding-amount"
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={fundingAmount}
                    onChange={(event) =>
                      setFundingAmount(
                        event.target.value
                      )
                    }
                    placeholder="Enter transaction amount"
                  />
                </div>

              </div>

              <div className="project-form-field">

                <label htmlFor="funding-transaction-date">
                  Transaction Date
                </label>

                <input
                  id="funding-transaction-date"
                  type="datetime-local"
                  value={
                    fundingTransactionDate
                  }
                  onChange={(event) =>
                    setFundingTransactionDate(
                      event.target.value
                    )
                  }
                />

              </div>

              <div className="project-form-field">

                <label htmlFor="funding-reference">
                  Reference Number
                </label>

                <input
                  id="funding-reference"
                  type="text"
                  value={fundingReference}
                  onChange={(event) =>
                    setFundingReference(
                      event.target.value
                    )
                  }
                  placeholder="e.g. CSR-2026-001"
                />

              </div>

              <div className="project-form-field">

                <label htmlFor="funding-description">
                  Description
                </label>

                <textarea
                  id="funding-description"
                  rows={4}
                  value={fundingDescription}
                  onChange={(event) =>
                    setFundingDescription(
                      event.target.value
                    )
                  }
                  placeholder="Explain the purpose of this funding transaction..."
                />

              </div>

              {fundingError && (
                <div className="project-form-error">
                  <AlertCircle size={16} />

                  <span>
                    {fundingError}
                  </span>
                </div>
              )}

            </div>

            <div className="project-modal-footer">

              <button
                type="button"
                className="project-secondary-button"
                onClick={closeCreateFunding}
                disabled={savingFunding}
              >
                Cancel
              </button>

              <button
                type="button"
                className="project-primary-button"
                onClick={() =>
                  void saveFundingTransaction()
                }
                disabled={savingFunding}
              >
                {savingFunding ? (
                  <>
                    <Loader2
                      size={16}
                      className="spin"
                    />
                    Creating...
                  </>
                ) : (
                  <>
                    <IndianRupee size={16} />
                    Create Transaction
                  </>
                )}
              </button>

            </div>

          </div>
        </div>
      )}

      {/* ===================================================
          REVIEW DELIVERABLE MODAL
      =================================================== */}

      {reviewingDeliverable && (
        <div
          className="project-modal-overlay"
          onMouseDown={(event) => {
            if (
              event.target ===
              event.currentTarget &&
              !savingDeliverableReview
            ) {
              closeReviewDeliverable();
            }
          }}
        >

          <div
            className="project-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="review-deliverable-title"
          >

            <div className="project-modal-header">

              <div>

                <span className="project-section-eyebrow">
                  DELIVERABLE REVIEW
                </span>

                <h2 id="review-deliverable-title">
                  {
                    reviewingDeliverable.title
                  }
                </h2>

              </div>


              <button
                type="button"
                className="project-modal-close"
                onClick={
                  closeReviewDeliverable
                }
                disabled={
                  savingDeliverableReview
                }
                aria-label="Close"
              >
                ×
              </button>

            </div>


            <div className="project-modal-body">

              {reviewingDeliverable.submission_reference && (
                <div className="project-review-reference">

                  <strong>
                    Submission reference
                  </strong>

                  <span>
                    {
                      reviewingDeliverable.submission_reference
                    }
                  </span>

                </div>
              )}


              <div className="project-form-field">

                <label htmlFor="deliverable-review-decision">
                  Decision
                </label>

                <select
                  id="deliverable-review-decision"
                  value={
                    deliverableReviewDecision
                  }
                  onChange={(event) =>
                    setDeliverableReviewDecision(
                      event.target
                        .value as
                      | "APPROVED"
                      | "REJECTED"
                    )
                  }
                >

                  <option value="APPROVED">
                    Approve
                  </option>

                  <option value="REJECTED">
                    Reject
                  </option>

                </select>

              </div>


              <div className="project-form-field">

                <label htmlFor="deliverable-review-remarks">
                  Review Remarks
                </label>

                <textarea
                  id="deliverable-review-remarks"
                  rows={5}
                  value={
                    deliverableReviewRemarks
                  }
                  onChange={(event) =>
                    setDeliverableReviewRemarks(
                      event.target.value
                    )
                  }
                  placeholder="Add review remarks, observations or corrective actions..."
                />

              </div>


              {deliverableReviewDecision ===
                "REJECTED" && (
                  <div className="project-form-info warning">
                    Rejected deliverables can be
                    resubmitted by the project partner
                    after corrective action.
                  </div>
                )}


              {deliverableReviewError && (
                <div className="project-form-error">

                  <AlertCircle
                    size={16}
                  />

                  <span>
                    {
                      deliverableReviewError
                    }
                  </span>

                </div>
              )}

            </div>


            <div className="project-modal-footer">

              <button
                type="button"
                className="project-secondary-button"
                onClick={
                  closeReviewDeliverable
                }
                disabled={
                  savingDeliverableReview
                }
              >
                Cancel
              </button>


              <button
                type="button"
                className="project-primary-button"
                onClick={() =>
                  void saveDeliverableReview()
                }
                disabled={
                  savingDeliverableReview
                }
              >

                {savingDeliverableReview ? (
                  <>
                    <Loader2
                      size={16}
                      className="spin"
                    />

                    Saving...
                  </>
                ) : deliverableReviewDecision ===
                  "APPROVED" ? (
                  <>
                    <CheckCircle2
                      size={16}
                    />

                    Approve Deliverable
                  </>
                ) : (
                  <>
                    <AlertCircle
                      size={16}
                    />

                    Reject Deliverable
                  </>
                )}

              </button>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}


/* =========================================================
   SUMMARY METRIC
========================================================= */

function SummaryMetric({
  icon,
  label,
  value,
  subtitle,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  subtitle: string;
}) {
  return (
    <div className="project-execution-metric">

      <div className="project-execution-icon">
        {icon}
      </div>

      <div>

        <span>
          {label}
        </span>

        <strong>
          {value}
        </strong>

        <small>
          {subtitle}
        </small>

      </div>

    </div>
  );
}
