import { api } from "./api";

/* ============================================================
   TYPES
============================================================ */

export type ProposalEvaluationDecision =
  | "UNDER_REVIEW"
  | "SHORTLISTED"
  | "REJECTED";

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


export interface ProposalEvaluation {
  id: number;
  proposal_id: number;
  evaluated_by: number;

  technical_feasibility_score: number;
  innovation_score: number;
  cost_effectiveness_score: number;
  impact_score: number;
  timeline_score: number;
  scalability_score: number;
  research_capability_score: number;

  overall_score: number;

  remarks: string | null;
  decision: ProposalEvaluationDecision;

  evaluated_at: string;
  created_at: string;
  updated_at: string;
}


export interface CreateProposalEvaluationRequest {
  proposal_id: number;

  technical_feasibility_score: number;
  innovation_score: number;
  cost_effectiveness_score: number;
  impact_score: number;
  timeline_score: number;
  scalability_score: number;
  research_capability_score: number;

  remarks?: string;
}


export interface ProposalEvaluationDecisionRequest {
  decision: "SHORTLISTED" | "REJECTED";
  remarks?: string;
}


/* ============================================================
   GET PROPOSALS FOR RFP
============================================================ */

export async function getRFPProposals(
  rfpId: number
): Promise<UniversityProposal[]> {
  const response = await api.get<UniversityProposal[]>(
    `/university-proposals/rfp/${rfpId}`
  );

  return response.data;
}


/* ============================================================
   GET SINGLE PROPOSAL
============================================================ */

export async function getUniversityProposal(
  proposalId: number
): Promise<UniversityProposal> {
  const response = await api.get<UniversityProposal>(
    `/university-proposals/${proposalId}`
  );

  return response.data;
}


/* ============================================================
   CREATE EVALUATION
============================================================ */

export async function createProposalEvaluation(
  payload: CreateProposalEvaluationRequest
): Promise<ProposalEvaluation> {
  const response = await api.post<ProposalEvaluation>(
    "/proposal-evaluations",
    payload
  );

  return response.data;
}


/* ============================================================
   DECIDE PROPOSAL
============================================================ */

export async function decideProposalEvaluation(
  evaluationId: number,
  payload: ProposalEvaluationDecisionRequest
): Promise<ProposalEvaluation> {
  const response = await api.post<ProposalEvaluation>(
    `/proposal-evaluations/${evaluationId}/decision`,
    payload
  );

  return response.data;
}