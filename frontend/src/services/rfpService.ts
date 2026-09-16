import { api } from "./api";


// ============================================================
// Types
// ============================================================

export type RFPStatus = "DRAFT" | "PUBLISHED" | "CLOSED";

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
  status: RFPStatus;
  is_active: boolean;
  published_at: string | null;
  closed_at: string | null;
  created_at: string;
  updated_at: string;
}


/*
|--------------------------------------------------------------------------
| List all RFPs (with optional status filter)
|--------------------------------------------------------------------------
*/

export async function listRfps(status?: RFPStatus): Promise<RFP[]> {
  const params = status ? { status } : {};
  const res = await api.get<RFP[]>("/rfps", { params });
  return res.data;
}


/*
|--------------------------------------------------------------------------
| Get single RFP
|--------------------------------------------------------------------------
*/

export async function getRfp(rfpId: number): Promise<RFP> {
  const res = await api.get<RFP>(`/rfps/${rfpId}`);
  return res.data;
}


/*
|--------------------------------------------------------------------------
| Publish an RFP
|--------------------------------------------------------------------------
*/

export async function publishRfp(rfpId: number): Promise<RFP> {
  const res = await api.post<RFP>(`/rfps/${rfpId}/publish`);
  return res.data;
}


/*
|--------------------------------------------------------------------------
| Close an RFP
|--------------------------------------------------------------------------
*/

export async function closeRfp(rfpId: number): Promise<RFP> {
  const res = await api.post<RFP>(`/rfps/${rfpId}/close`);
  return res.data;
}
