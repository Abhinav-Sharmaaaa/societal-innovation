import { api } from "./api";

/* =========================================================
   PROJECT TYPES
========================================================= */

export type ProjectStatus =
    | "PLANNING"
    | "ACTIVE"
    | "ON_HOLD"
    | "COMPLETED"
    | "CANCELLED";

export type ProjectHealth =
    | "ON_TRACK"
    | "AT_RISK"
    | "DELAYED"
    | "CRITICAL";

export interface Project {
    id: number;

    collaboration_id: number;
    challenge_id: number;

    university_id: number;
    industry_id: number;

    created_by: number;

    title: string;
    description: string | null;
    objectives: string | null;
    expected_outcomes: string | null;

    total_budget: number | null;

    start_date: string | null;
    target_completion_date: string | null;
    actual_completion_date: string | null;

    status: ProjectStatus;
    health: ProjectHealth;
    progress_percentage: number;

    created_at: string;
    updated_at: string;
}

export interface CreateProjectRequest {
    collaboration_id: number;

    title: string;
    description?: string;
    objectives?: string;
    expected_outcomes?: string;

    total_budget?: number;

    start_date?: string;
    target_completion_date?: string;
}

/* =========================================================
   PROJECT MILESTONES
========================================================= */

export type ProjectMilestoneStatus =
    | "NOT_STARTED"
    | "IN_PROGRESS"
    | "COMPLETED"
    | "DELAYED"
    | "BLOCKED";

export interface ProjectMilestone {
    id: number;
    project_id: number;

    milestone_type: string;
    sequence_number: number;

    title: string;
    description: string | null;
    deliverables: string | null;

    start_date: string | null;
    due_date: string | null;
    completed_at: string | null;

    status: ProjectMilestoneStatus;
    progress_percentage: number;
    is_mandatory: boolean;

    completion_remarks: string | null;

    created_at: string;
    updated_at: string;
}

export interface UpdateProjectMilestoneRequest {
    progress_percentage: number;
    status: ProjectMilestoneStatus;
    completion_remarks?: string;
}

/* =========================================================
   PROJECT DELIVERABLES
========================================================= */

export type ProjectDeliverableStatus =
    | "PENDING"
    | "IN_PROGRESS"
    | "SUBMITTED"
    | "APPROVED"
    | "REJECTED"
    | "OVERDUE";

export interface ProjectDeliverable {
    id: number;
    project_id: number;
    milestone_id: number;

    title: string;
    description: string | null;

    due_date: string | null;
    submitted_at: string | null;
    approved_at: string | null;

    status: ProjectDeliverableStatus;

    submission_reference: string | null;
    review_remarks: string | null;

    is_mandatory: boolean;

    created_at: string;
    updated_at: string;
}

export interface CreateProjectDeliverableRequest {
    milestone_id: number;

    title: string;
    description?: string;

    due_date?: string;

    is_mandatory?: boolean;
}

export interface SubmitProjectDeliverableRequest {
    submission_reference: string;
}

export type ProjectDeliverableReviewDecision =
    | "APPROVED"
    | "REJECTED";

export interface ReviewProjectDeliverableRequest {
    decision: ProjectDeliverableReviewDecision;
    review_remarks?: string;
}

/* =========================================================
   PROJECT FUNDING
========================================================= */

export type ProjectFundingTransactionType =
    | "ALLOCATION"
    | "DISBURSEMENT"
    | "UTILIZATION"
    | "REFUND";

export type ProjectFundingTransactionStatus =
    | "PENDING"
    | "APPROVED"
    | "COMPLETED"
    | "REJECTED";

export interface ProjectFundingTransaction {
    id: number;
    project_id: number;
    transaction_type: ProjectFundingTransactionType;
    status: ProjectFundingTransactionStatus;
    amount: number;
    transaction_date: string | null;
    description: string | null;
    reference_number: string | null;
    created_by: number;
    approved_by: number | null;
    approved_at: string | null;
    created_at: string;
    updated_at: string;
}

export interface ProjectFundingCreatePayload {
    project_id: number;
    transaction_type: ProjectFundingTransactionType;
    amount: number;
    transaction_date?: string | null;
    description?: string | null;
    reference_number?: string | null;
}

export interface ProjectFundingApprovalPayload {
    decision: "APPROVED" | "REJECTED";
    remarks?: string | null;
}



export interface CreateProjectFundingRequest {
    project_id: number;

    transaction_type: ProjectFundingTransactionType;

    amount: number;

    transaction_date?: string;

    description?: string;
    reference_number?: string;
}

export type ProjectFundingApprovalDecision =
    | "APPROVED"
    | "REJECTED";

export interface ApproveProjectFundingRequest {
    decision: ProjectFundingApprovalDecision;
    remarks?: string;
}

export interface ProjectFundingSummary {
    project_id: number;

    allocated: number;
    disbursed: number;
    utilized: number;
    refunded: number;

    remaining: number;
}

/* =========================================================
   PROJECT REPORTS
========================================================= */

export type ProjectReportType =
    | "PROGRESS"
    | "MILESTONE"
    | "FINANCIAL"
    | "PILOT"
    | "FINAL";

export type ProjectReportStatus =
    | "DRAFT"
    | "SUBMITTED"
    | "UNDER_REVIEW"
    | "APPROVED"
    | "REJECTED";

export interface ProjectReport {
    id: number;
    project_id: number;
    milestone_id: number | null;
    submitted_by: number;

    report_type: ProjectReportType;

    title: string;
    summary: string;

    findings: string | null;
    challenges: string | null;
    next_steps: string | null;

    status: ProjectReportStatus;

    submitted_at: string | null;
    reviewed_at: string | null;
    review_remarks: string | null;

    created_at: string;
    updated_at: string;
}

export interface CreateProjectReportRequest {
    project_id: number;
    milestone_id?: number;

    report_type: ProjectReportType;

    title: string;
    summary: string;

    findings?: string;
    challenges?: string;
    next_steps?: string;
}

export type ProjectReportReviewDecision =
    | "APPROVED"
    | "REJECTED";

export interface ReviewProjectReportRequest {
    decision: ProjectReportReviewDecision;
    review_remarks?: string;
}

/* =========================================================
   PROJECT EVIDENCE
========================================================= */

export type ProjectEvidenceType =
    | "DOCUMENT"
    | "IMAGE"
    | "VIDEO"
    | "DATASET"
    | "LINK";

export interface ProjectEvidence {
    id: number;

    project_id: number;
    report_id: number | null;
    uploaded_by: number;

    evidence_type: ProjectEvidenceType;

    title: string;

    file_url: string | null;
    external_url: string | null;

    description: string | null;

    created_at: string;
    updated_at: string;
}

export interface CreateProjectEvidenceRequest {
    project_id: number;
    report_id?: number;

    evidence_type: ProjectEvidenceType;

    title: string;

    file_url?: string;
    external_url?: string;

    description?: string;
}

/* =========================================================
   PROJECT OUTCOMES
========================================================= */

export type ProjectOutcomeMetricType =
    | "COUNT"
    | "PERCENTAGE"
    | "CURRENCY"
    | "SCORE"
    | "TEXT";

export type ProjectOutcomeStatus =
    | "DRAFT"
    | "SUBMITTED"
    | "UNDER_REVIEW"
    | "VERIFIED"
    | "REJECTED";

export interface ProjectOutcome {
    id: number;
    project_id: number;
    submitted_by: number;

    title: string;
    description: string;

    beneficiary_count: number | null;

    metric_name: string | null;
    metric_type: ProjectOutcomeMetricType | null;

    baseline_value: number | null;
    target_value: number | null;
    achieved_value: number | null;

    impact_score: number | null;

    status: ProjectOutcomeStatus;

    submitted_at: string | null;
    verified_at: string | null;
    verification_remarks: string | null;

    created_at: string;
    updated_at: string;
}

export interface CreateProjectOutcomeRequest {
    project_id: number;

    title: string;
    description: string;

    beneficiary_count?: number;

    metric_name?: string;
    metric_type?: ProjectOutcomeMetricType;

    baseline_value?: number;
    target_value?: number;
    achieved_value?: number;

    impact_score?: number;
}

export type ProjectOutcomeVerificationDecision =
    | "VERIFIED"
    | "REJECTED";

export interface VerifyProjectOutcomeRequest {
    decision: ProjectOutcomeVerificationDecision;
    verification_remarks?: string;
}

/* =========================================================
   PROJECT RISKS
========================================================= */

export type ProjectRiskLevel =
    | "LOW"
    | "MEDIUM"
    | "HIGH"
    | "CRITICAL";

export type ProjectRiskStatus =
    | "OPEN"
    | "ACKNOWLEDGED"
    | "MITIGATED"
    | "CLOSED";

export interface ProjectRisk {
    id: number;
    project_id: number;

    risk_level: ProjectRiskLevel;
    risk_score: number;

    title: string;
    description: string;

    detected_factors: string | null;
    recommended_action: string | null;

    status: ProjectRiskStatus;

    detected_at: string;
    acknowledged_at: string | null;
    resolved_at: string | null;
    resolution_remarks: string | null;

    created_at: string;
    updated_at: string;
}

export type ProjectRiskAction =
    | "ACKNOWLEDGED"
    | "MITIGATED"
    | "CLOSED";

export interface ManageProjectRiskRequest {
    action: ProjectRiskAction;
    remarks?: string;
}

/* =========================================================
   PROJECT APIs
========================================================= */

export async function getProjects(): Promise<Project[]> {
    const response = await api.get<Project[]>(
        "/projects"
    );

    return response.data;
}

export async function getProject(
    projectId: number
): Promise<Project> {
    const response = await api.get<Project>(
        `/projects/${projectId}`
    );

    return response.data;
}

export async function createProject(
    payload: CreateProjectRequest
): Promise<Project> {
    const response = await api.post<Project>(
        "/projects",
        payload
    );

    return response.data;
}

/* =========================================================
   MILESTONE APIs
========================================================= */

export async function getProjectMilestones(
    projectId: number
): Promise<ProjectMilestone[]> {
    const response = await api.get<ProjectMilestone[]>(
        `/project-milestones/project/${projectId}`
    );

    return response.data;
}

export async function updateProjectMilestone(
    milestoneId: number,
    payload: UpdateProjectMilestoneRequest
): Promise<ProjectMilestone> {
    const response = await api.put<ProjectMilestone>(
        `/project-milestones/${milestoneId}`,
        payload
    );

    return response.data;
}

/* =========================================================
   DELIVERABLE APIs
========================================================= */

export async function getProjectDeliverables(
    projectId: number
): Promise<ProjectDeliverable[]> {
    const response = await api.get<ProjectDeliverable[]>(
        `/project-deliverables/project/${projectId}`
    );

    return response.data;
}

export async function createProjectDeliverable(
    payload: CreateProjectDeliverableRequest
): Promise<ProjectDeliverable> {
    const response = await api.post<ProjectDeliverable>(
        "/project-deliverables",
        payload
    );

    return response.data;
}

export async function submitProjectDeliverable(
    deliverableId: number,
    payload: SubmitProjectDeliverableRequest
): Promise<ProjectDeliverable> {
    const response = await api.post<ProjectDeliverable>(
        `/project-deliverables/${deliverableId}/submit`,
        payload
    );

    return response.data;
}

export async function reviewProjectDeliverable(
    deliverableId: number,
    payload: ReviewProjectDeliverableRequest
): Promise<ProjectDeliverable> {
    const response = await api.post<ProjectDeliverable>(
        `/project-deliverables/${deliverableId}/review`,
        payload
    );

    return response.data;
}

/* =========================================================
   FUNDING APIs
========================================================= */

export async function getProjectFundingSummary(
    projectId: number
): Promise<ProjectFundingSummary> {
    const response = await api.get<ProjectFundingSummary>(
        `/project-funding/project/${projectId}/summary`
    );

    return response.data;
}

export async function createProjectFunding(
    payload: CreateProjectFundingRequest
): Promise<ProjectFundingTransaction> {
    const response = await api.post<ProjectFundingTransaction>(
        "/project-funding",
        payload
    );

    return response.data;
}

export async function approveProjectFunding(
    transactionId: number,
    payload: ApproveProjectFundingRequest
): Promise<ProjectFundingTransaction> {
    const response = await api.post<ProjectFundingTransaction>(
        `/project-funding/${transactionId}/approve`,
        payload
    );

    return response.data;
}

export async function completeProjectFunding(
    transactionId: number
): Promise<ProjectFundingTransaction> {
    const response = await api.post<ProjectFundingTransaction>(
        `/project-funding/${transactionId}/complete`
    );

    return response.data;
}

export async function getProjectFundingTransactions(
    projectId: number
): Promise<ProjectFundingTransaction[]> {
    const response = await api.get(
        `/project-funding/project/${projectId}/transactions`
    );

    return response.data;
}

/* =========================================================
   REPORT APIs
========================================================= */

export async function getProjectReports(
    projectId: number
): Promise<ProjectReport[]> {
    const response = await api.get<ProjectReport[]>(
        `/project-reports/project/${projectId}`
    );

    return response.data;
}

export async function createProjectReport(
    payload: CreateProjectReportRequest
): Promise<ProjectReport> {
    const response = await api.post<ProjectReport>(
        "/project-reports",
        payload
    );

    return response.data;
}

export async function reviewProjectReport(
    reportId: number,
    payload: ReviewProjectReportRequest
): Promise<ProjectReport> {
    const response = await api.post<ProjectReport>(
        `/project-reports/${reportId}/review`,
        payload
    );

    return response.data;
}

/* =========================================================
   EVIDENCE APIs
========================================================= */

export async function getProjectEvidence(
    projectId: number
): Promise<ProjectEvidence[]> {
    const response = await api.get<ProjectEvidence[]>(
        `/project-reports/project/${projectId}/evidence`
    );

    return response.data;
}

export async function createProjectEvidence(
    payload: CreateProjectEvidenceRequest
): Promise<ProjectEvidence> {
    const response = await api.post<ProjectEvidence>(
        "/project-reports/evidence",
        payload
    );

    return response.data;
}

/* =========================================================
   OUTCOME APIs
========================================================= */

export async function getProjectOutcomes(
    projectId: number
): Promise<ProjectOutcome[]> {
    const response = await api.get<ProjectOutcome[]>(
        `/project-outcomes/project/${projectId}`
    );

    return response.data;
}

export async function createProjectOutcome(
    payload: CreateProjectOutcomeRequest
): Promise<ProjectOutcome> {
    const response = await api.post<ProjectOutcome>(
        "/project-outcomes",
        payload
    );

    return response.data;
}

export async function verifyProjectOutcome(
    outcomeId: number,
    payload: VerifyProjectOutcomeRequest
): Promise<ProjectOutcome> {
    const response = await api.post<ProjectOutcome>(
        `/project-outcomes/${outcomeId}/verify`,
        payload
    );

    return response.data;
}

/* =========================================================
   RISK APIs
========================================================= */

export async function getProjectRisks(
    projectId: number
): Promise<ProjectRisk[]> {
    const response = await api.get<ProjectRisk[]>(
        `/project-risks/project/${projectId}`
    );

    return response.data;
}

export async function assessProjectRisk(
    projectId: number
): Promise<ProjectRisk> {
    const response = await api.post<ProjectRisk>(
        `/project-risks/project/${projectId}/assess`
    );

    return response.data;
}

export async function manageProjectRisk(
    riskId: number,
    payload: ManageProjectRiskRequest
): Promise<ProjectRisk> {
    const response = await api.post<ProjectRisk>(
        `/project-risks/${riskId}/action`,
        payload
    );

    return response.data;
}