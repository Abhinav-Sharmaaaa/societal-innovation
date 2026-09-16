import { api } from "./api";

export interface CategoryPrediction {
  rank: number;
  category: string;
  confidence: number;
}

export interface TriageResult {
  category: string;
  category_confidence: number;
  second_category: string;
  second_category_confidence: number;
  category_margin: number;
  category_top_3: CategoryPrediction[];
  category_decision: string;
  requires_human_review: boolean;

  severity: string;
  urgency: string;

  innovation_required: boolean;
  innovation_score: number;

  routing_type: string;
  routing_confidence: number;

  severity_score: number;
  urgency_score: number;

  routing_reason: string;
  severity_reason: string;
  urgency_reason: string;
  innovation_reason: string;

  model_version: string;
}

export interface TriageRequestPayload {
  challenge_id?: number;

  title: string;
  description: string;
  category?: string | null;
  affected_population?: number | null;
  estimated_economic_loss?: number | null;
  address?: string | null;
  district?: string | null;
  state?: string | null;
}

export async function runChallengeTriage(
  payload: TriageRequestPayload
): Promise<TriageResult> {
  const response = await api.post<TriageResult>(
    "/ai/triage",
    {
      challenge_id: payload.challenge_id ?? null,

      title: payload.title,
      description: payload.description,
      category: payload.category ?? null,
      affected_population: payload.affected_population ?? null,
      estimated_economic_loss:
        payload.estimated_economic_loss ?? null,
      address: payload.address ?? null,
      district: payload.district ?? null,
      state: payload.state ?? null,
    }
  );

  return response.data;
}


// ============================================================
// Duplicate Check
// ============================================================

export interface DuplicateMatch {
  id: number;
  title: string;
  description: string;
  category: string | null;
  status: string;
  district: string | null;
  state: string | null;
  similarity_score: number;
}

export interface DuplicateCheckResponse {
  has_duplicates: boolean;
  matches: DuplicateMatch[];
}

export interface DuplicateCheckPayload {
  title: string;
  description: string;
  category?: string | null;
  district?: string | null;
  state?: string | null;
}

export async function checkDuplicates(
  payload: DuplicateCheckPayload
): Promise<DuplicateCheckResponse> {
  const response = await api.post<DuplicateCheckResponse>(
    "/ai/duplicate-check",
    {
      title:       payload.title,
      description: payload.description,
      category:    payload.category    ?? null,
      district:    payload.district    ?? null,
      state:       payload.state       ?? null,
    }
  );

  return response.data;
}