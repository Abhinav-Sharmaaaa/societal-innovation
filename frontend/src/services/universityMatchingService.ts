import { api } from "./api";


/* ============================================================
   UNIVERSITY MATCHING
============================================================ */

export interface UniversityMatchRecommendation {
  rank: number;

  organization_id: number;
  organization_name: string;

  score: number;

  competency_match_score: number;
  capability_match_score: number;
  text_relevance_score: number;
  location_score: number;

  matched_competencies: string[];
  matched_capabilities: string[];

  explanation: string;
}


export interface UniversityMatchingResponse {
  rfp_id: number;
  challenge_id: number;

  recommendations:
    UniversityMatchRecommendation[];

  total_candidates_evaluated: number;
}


/* ============================================================
   RFP INVITATIONS
============================================================ */

export interface RFPInvitationCreate {
  rfp_id: number;
  university_id: number;
}


export interface RFPInvitation {
  id: number;

  rfp_id: number;
  university_id: number;

  invited_by: number;

  recommendation_rank: number | null;
  match_score: number | null;

  status: string;

  response_reason: string | null;

  invited_at: string;
  viewed_at: string | null;
  responded_at: string | null;

  created_at: string;
  updated_at: string;
}


/* ============================================================
   SERVICE
============================================================ */

export const universityMatchingService = {

  /* ----------------------------------------------------------
     MATCH UNIVERSITIES FOR RFP
  ---------------------------------------------------------- */

  async matchUniversities(
    rfpId: number,
  ): Promise<UniversityMatchingResponse> {
    const response =
      await api.post<UniversityMatchingResponse>(
        `/rfps/${rfpId}/match-universities`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     SEND INVITATION
  ---------------------------------------------------------- */

  async sendInvitation(
    payload: RFPInvitationCreate,
  ): Promise<RFPInvitation> {
    const response =
      await api.post<RFPInvitation>(
        "/rfp-invitations",
        payload,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     GET RFP INVITATIONS
  ---------------------------------------------------------- */

  async getRFPInvitations(
    rfpId: number,
  ): Promise<RFPInvitation[]> {
    const response =
      await api.get<RFPInvitation[]>(
        `/rfp-invitations/rfp/${rfpId}`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     UNIVERSITY INTEREST
  ---------------------------------------------------------- */

  async expressInterest(
    invitationId: number,
  ): Promise<RFPInvitation> {
    const response =
      await api.post<RFPInvitation>(
        `/rfp-invitations/${invitationId}/interest`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     UNIVERSITY DECLINE
  ---------------------------------------------------------- */

  async declineInvitation(
    invitationId: number,
    reason?: string,
  ): Promise<RFPInvitation> {
    const response =
      await api.post<RFPInvitation>(
        `/rfp-invitations/${invitationId}/decline`,
        {
          reason: reason || null,
        },
      );

    return response.data;
  },
};


/* ============================================================
   UNIVERSITIES LIST (for manual search/invite)
============================================================ */

export interface UniversityOrganization {
  id: number;
  name: string;
  short_name: string | null;
  city: string | null;
  district: string | null;
  state: string | null;
  email: string | null;
}

export async function listAllUniversities(): Promise<
  UniversityOrganization[]
> {
  const response = await api.get<UniversityOrganization[]>(
    "/organizations",
    {
      params: { organization_type: "UNIVERSITY" },
    }
  );

  return response.data;
}