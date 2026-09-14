import { api } from "./api";

/* ============================================================
   ENUMS / TYPES
   ============================================================ */

export type UniversityProposalStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "UNDER_EVALUATION"
  | "SHORTLISTED"
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

  status: UniversityProposalStatus;

  submitted_at: string | null;
  created_at: string;
  updated_at: string;
}

/* ============================================================
   CREATE PROPOSAL REQUEST
   ============================================================ */

export interface CreateUniversityProposalRequest {
  invitation_id: number;
  title: string;
  solution: string;
  technical_approach: string;
  research_methodology?: string;
  required_resources?: string;
  estimated_cost?: number;
  expected_timeline_days?: number;
  faculty_team?: string;
  expected_outcomes?: string;
  technology_requirements?: string;
}

/* ============================================================
   API METHODS
   ============================================================ */

/**
 * Submit a university proposal.
 */
export async function createUniversityProposal(
  payload: CreateUniversityProposalRequest
): Promise<UniversityProposal> {
  const response = await api.post<UniversityProposal>(
    "/university-proposals",
    payload
  );

  return response.data;
}

/**
 * Get a single university proposal.
 */
export async function getUniversityProposal(
  proposalId: number
): Promise<UniversityProposal> {
  const response = await api.get<UniversityProposal>(
    `/university-proposals/${proposalId}`
  );

  return response.data;
}

/**
 * Get all proposals submitted against an RFP.
 */
export async function getRFPProposals(
  rfpId: number
): Promise<UniversityProposal[]> {
  const response = await api.get<UniversityProposal[]>(
    `/university-proposals/rfp/${rfpId}`
  );

  return response.data;
}