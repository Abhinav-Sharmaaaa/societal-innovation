import { api } from "./api";

export type IndustryCollaborationStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "UNDER_REVIEW"
  | "MODIFICATION_REQUESTED"
  | "ACCEPTED"
  | "REJECTED"
  | "WITHDRAWN";

export interface UniversityProposal {
  id: number;
  rfp_id: number;
  invitation_id: number;
  university_id: number;
  submitted_by: number;

  title: string;
  solution: string;
  technical_approach: string;

  research_methodology: string | null;
  required_resources: string | null;
  estimated_cost: number | null;
  expected_timeline_days: number | null;
  faculty_team: string | null;
  expected_outcomes: string | null;
  technology_requirements: string | null;

  status:
    | "DRAFT"
    | "SUBMITTED"
    | "UNDER_EVALUATION"
    | "SHORTLISTED"
    | "REJECTED"
    | "WITHDRAWN";

  submitted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface IndustryCollaboration {
  id: number;

  university_proposal_id: number;
  industry_id: number;
  submitted_by: number;

  title: string;
  collaboration_description: string;

  funding_amount: number | null;

  technical_mentorship: string | null;
  industry_experts: string | null;
  infrastructure_resources: string | null;
  technology_support: string | null;
  internship_support: string | null;
  pilot_deployment_support: string | null;
  commercialization_support: string | null;

  proposed_duration_days: number | null;
  response_deadline: string | null;
  additional_terms: string | null;

  status: IndustryCollaborationStatus;

  submitted_at: string | null;
  reviewed_at: string | null;

  created_at: string;
  updated_at: string;
}

export interface CreateIndustryCollaborationRequest {
  university_proposal_id: number;

  title: string;
  collaboration_description: string;

  funding_amount?: number;

  technical_mentorship?: string;
  industry_experts?: string;
  infrastructure_resources?: string;
  technology_support?: string;
  internship_support?: string;
  pilot_deployment_support?: string;
  commercialization_support?: string;

  proposed_duration_days?: number;
  response_deadline?: string;

  additional_terms?: string;
}

export interface IndustryCollaborationDecisionRequest {
  decision:
    | "ACCEPTED"
    | "REJECTED"
    | "MODIFICATION_REQUESTED";

  remarks?: string;
}

/* ============================================================
   INDUSTRY: SHORTLISTED PROPOSALS
============================================================ */

export async function getShortlistedProposals(): Promise<
  UniversityProposal[]
> {
  const response = await api.get<UniversityProposal[]>(
    "/university-proposals/shortlisted"
  );

  return response.data;
}

/* ============================================================
   INDUSTRY: SUBMIT COLLABORATION
============================================================ */

export async function createIndustryCollaboration(
  payload: CreateIndustryCollaborationRequest
): Promise<IndustryCollaboration> {
  const response =
    await api.post<IndustryCollaboration>(
      "/industry-collaboration",
      payload
    );

  return response.data;
}

/* ============================================================
   INDUSTRY: MY COLLABORATIONS
============================================================ */

export async function getMyIndustryCollaborations(): Promise<
  IndustryCollaboration[]
> {
  const response =
    await api.get<IndustryCollaboration[]>(
      "/industry-collaboration/my"
    );

  return response.data;
}

/* ============================================================
   UNIVERSITY: RECEIVED COLLABORATIONS
============================================================ */

export async function getUniversityCollaborations(): Promise<
  IndustryCollaboration[]
> {
  const response =
    await api.get<IndustryCollaboration[]>(
      "/industry-collaboration/university"
    );

  return response.data;
}

/* ============================================================
   UNIVERSITY: DECISION
============================================================ */

export async function decideIndustryCollaboration(
  collaborationId: number,
  payload: IndustryCollaborationDecisionRequest
): Promise<IndustryCollaboration> {
  const response =
    await api.post<IndustryCollaboration>(
      `/industry-collaboration/${collaborationId}/decision`,
      payload
    );

  return response.data;
}

export async function getAcceptedGovernmentCollaborations(): Promise<
  IndustryCollaboration[]
> {
  const response =
    await api.get<IndustryCollaboration[]>(
      "/industry-collaboration/government/accepted"
    );

  return response.data;
}