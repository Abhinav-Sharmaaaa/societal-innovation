import { api } from "./api";


/* ============================================================
   INNOVATION OPPORTUNITY
============================================================ */

export interface InnovationOpportunity {
  id: number;
  challenge_id: number;
  sponsoring_organization_id: number;

  created_by: number;
  approved_by: number | null;

  title: string;
  problem_statement: string;

  objectives: string | null;
  technical_requirements: string | null;
  expected_outcomes: string | null;

  estimated_budget: number | null;
  expected_duration_days: number | null;
  proposal_deadline: string | null;

  status: string;
  is_active: boolean;

  approved_at: string | null;
  created_at: string;
  updated_at: string;
}


export interface InnovationOpportunityCreate {
  challenge_id: number;
  sponsoring_organization_id: number;

  title: string;
  problem_statement: string;

  objectives?: string;
  technical_requirements?: string;
  expected_outcomes?: string;

  estimated_budget?: number;
  expected_duration_days?: number;
  proposal_deadline?: string;
}


/* ============================================================
   RFP
============================================================ */

export interface RFP {
  id: number;
  innovation_opportunity_id: number;
  created_by: number;

  title: string;
  description: string;

  objectives: string | null;
  technical_requirements: string | null;
  expected_outcomes: string | null;

  estimated_budget: number | null;
  expected_duration_days: number | null;
  proposal_deadline: string | null;

  status: string;
  is_active: boolean;

  published_at: string | null;
  closed_at: string | null;

  created_at: string;
  updated_at: string;
}


export interface RFPCreate {
  innovation_opportunity_id: number;

  title: string;
  description: string;

  objectives?: string;
  technical_requirements?: string;
  expected_outcomes?: string;

  estimated_budget?: number;
  expected_duration_days?: number;
  proposal_deadline?: string;
}


/* ============================================================
   SERVICE
============================================================ */

export const innovationService = {

  /* ----------------------------------------------------------
     CREATE INNOVATION OPPORTUNITY
  ---------------------------------------------------------- */

  async createOpportunity(
    payload: InnovationOpportunityCreate,
  ): Promise<InnovationOpportunity> {
    const response =
      await api.post<InnovationOpportunity>(
        "/innovation-opportunities",
        payload,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     GET INNOVATION OPPORTUNITY
  ---------------------------------------------------------- */

  async getOpportunity(
    opportunityId: number,
  ): Promise<InnovationOpportunity> {
    const response =
      await api.get<InnovationOpportunity>(
        `/innovation-opportunities/${opportunityId}`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     APPROVE
  ---------------------------------------------------------- */

  async approveOpportunity(
    opportunityId: number,
  ): Promise<InnovationOpportunity> {
    const response =
      await api.post<InnovationOpportunity>(
        `/innovation-opportunities/${opportunityId}/approve`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     CREATE RFP
  ---------------------------------------------------------- */

  async createRFP(
    payload: RFPCreate,
  ): Promise<RFP> {
    const response =
      await api.post<RFP>(
        "/rfps",
        payload,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     GET RFP
  ---------------------------------------------------------- */

  async getRFP(
    rfpId: number,
  ): Promise<RFP> {
    const response =
      await api.get<RFP>(
        `/rfps/${rfpId}`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     PUBLISH RFP
  ---------------------------------------------------------- */

  async publishRFP(
    rfpId: number,
  ): Promise<RFP> {
    const response =
      await api.post<RFP>(
        `/rfps/${rfpId}/publish`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     CLOSE RFP
  ---------------------------------------------------------- */

  async closeRFP(
    rfpId: number,
  ): Promise<RFP> {
    const response =
      await api.post<RFP>(
        `/rfps/${rfpId}/close`,
      );

    return response.data;
  },
};