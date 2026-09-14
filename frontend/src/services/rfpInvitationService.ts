import { api } from "./api";

export type RFPInvitationStatus =
  | "INVITED"
  | "VIEWED"
  | "INTERESTED"
  | "DECLINED"
  | "PROPOSAL_SUBMITTED"
  | "EXPIRED";

export interface RFPInvitation {
  id: number;
  rfp_id: number;
  university_id: number;
  invited_by: number;

  recommendation_rank: number | null;
  match_score: number | null;

  status: RFPInvitationStatus;
  response_reason: string | null;

  invited_at: string;
  viewed_at: string | null;
  responded_at: string | null;

  created_at: string;
  updated_at: string;
}

export interface RFPInvitationDecision {
  reason?: string;
}

/* ============================================================
   GET MY INVITATIONS
   ============================================================ */

export async function getMyRFPInvitations(): Promise<
  RFPInvitation[]
> {
  const response = await api.get<RFPInvitation[]>(
    "/rfp-invitations/my"
  );

  return response.data;
}

/* ============================================================
   EXPRESS INTEREST
   ============================================================ */

export async function expressInterest(
  invitationId: number
): Promise<RFPInvitation> {
  const response = await api.post<RFPInvitation>(
    `/rfp-invitations/${invitationId}/interest`
  );

  return response.data;
}

/* ============================================================
   DECLINE INVITATION
   ============================================================ */

export async function declineInvitation(
  invitationId: number,
  reason?: string
): Promise<RFPInvitation> {
  const response = await api.post<RFPInvitation>(
    `/rfp-invitations/${invitationId}/decline`,
    {
      reason,
    }
  );

  return response.data;
}