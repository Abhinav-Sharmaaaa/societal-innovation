import { api } from "./api";


/* ============================================================
   CHALLENGE EVIDENCE
============================================================ */

export interface ChallengeEvidence {
  id: number;

  evidence_type: string;
  original_filename: string;

  content_type: string | null;
  file_size: number | null;
  file_url: string | null;

  uploaded_by: number;

  created_at: string;
}


/* ============================================================
   CHALLENGE
   Mirrors backend/app/schemas/challenge.py
============================================================ */

export interface Challenge {
  /* ----------------------------------------------------------
     Basic Information
  ---------------------------------------------------------- */

  id: number;

  title: string;
  description: string;

  submitted_by: number;


  /* ----------------------------------------------------------
     Location Resolution
  ---------------------------------------------------------- */

  location_source: string;

  location_verified: boolean;

  location_accuracy_meters: number | null;

  locality: string | null;

  location_resolution_reason: string | null;

  location_resolved_at: string | null;


  /* ----------------------------------------------------------
     Classification
  ---------------------------------------------------------- */

  category: string;

  severity: string;

  urgency: string;


  /* ----------------------------------------------------------
     Impact / Location
  ---------------------------------------------------------- */

  affected_population: number | null;

  estimated_economic_loss: number | null;

  address: string | null;

  district: string | null;

  state: string | null;

  latitude: number | null;

  longitude: number | null;


  /* ----------------------------------------------------------
     Innovation
  ---------------------------------------------------------- */

  innovation_required: boolean;


  /* ----------------------------------------------------------
     General AI Information
  ---------------------------------------------------------- */

  ai_confidence_score: number | null;

  ai_model_version: string | null;


  /* ----------------------------------------------------------
     Category Model
  ---------------------------------------------------------- */

  ai_category_confidence: number | null;

  ai_second_category: string | null;

  ai_second_category_confidence: number | null;

  ai_category_margin: number | null;

  ai_category_decision: string | null;

  ai_requires_human_review: boolean | null;

  ai_category_top_3:
    Array<Record<string, unknown>> | null;


  /* ----------------------------------------------------------
     Innovation-required Model
  ---------------------------------------------------------- */

  ai_innovation_confidence: number | null;

  ai_innovation_decision: string | null;

  ai_innovation_requires_human_review:
    boolean | null;


  /* ----------------------------------------------------------
     Innovation-type Model
  ---------------------------------------------------------- */

  ai_innovation_type: string | null;

  ai_innovation_type_confidence: number | null;

  ai_innovation_type_second: string | null;

  ai_innovation_type_second_confidence:
    number | null;

  ai_innovation_type_margin: number | null;

  ai_innovation_type_decision: string | null;

  ai_innovation_type_requires_human_review:
    boolean | null;

  ai_innovation_type_top_3:
    Array<Record<string, unknown>> | null;


  /* ----------------------------------------------------------
     AI Analysis Timestamp
  ---------------------------------------------------------- */

  ai_analysis_at: string | null;


  /* ----------------------------------------------------------
     Routing
  ---------------------------------------------------------- */

  routing_type: string;

  routing_reason: string | null;


  /* ----------------------------------------------------------
     Current Authority Assignment
  ---------------------------------------------------------- */

  current_authority_id: number | null;

  assigned_at: string | null;

  assigned_by: number | null;


  /* ----------------------------------------------------------
     Challenge Lifecycle
  ---------------------------------------------------------- */

  status: string;


  /* ----------------------------------------------------------
     Duplicate / Master Challenge
  ---------------------------------------------------------- */

  is_master_challenge: boolean;

  master_challenge_id: number | null;

  duplicate_similarity_score: number | null;


  /* ----------------------------------------------------------
     Evidence
  ---------------------------------------------------------- */

  evidence: ChallengeEvidence[];


  /* ----------------------------------------------------------
     Timestamps
  ---------------------------------------------------------- */

  created_at: string;

  updated_at: string;
}


/* ============================================================
   AUTHORITY ROUTING
   Mirrors backend/app/schemas/routing.py
============================================================ */

export interface AuthorityCandidate {
  organization_id: number;

  organization_name: string;

  organization_type: string;

  score: number;

  reason: string;
}


export interface RoutingRecommendation {
  recommended_authority_id: number | null;

  recommended_authority_name:
    string | null;

  score: number;

  reason: string;

  candidates: AuthorityCandidate[];
}


/* ============================================================
   ASSIGNMENT HISTORY
   Mirrors backend/app/schemas/assignment.py
============================================================ */

export interface AssignmentHistoryItem {
  id: number;

  challenge_id: number;

  from_authority_id: number | null;

  to_authority_id: number;

  performed_by: number | null;

  action: string;

  status: string;

  reason: string | null;

  remarks: string | null;

  created_at: string;

  completed_at: string | null;
}


/* ============================================================
   REVIEW HISTORY
   Mirrors backend/app/schemas/review.py
============================================================ */

export interface ReviewHistoryItem {
  id: number;

  challenge_id: number;

  reviewer_id: number;

  decision: string;

  recommended_authority_id: number | null;

  selected_authority_id: number;

  reason: string | null;

  created_at: string;
}


/* ============================================================
   REQUEST TYPES
============================================================ */

export interface ChallengeAssignmentRequest {
  authority_id: number;

  remarks?: string;
}


export interface ChallengeReassignRequest {
  authority_id: number;

  reason: string;

  remarks?: string;
}


export interface ChallengeEscalateRequest {
  authority_id: number;

  reason: string;

  remarks?: string;
}


export interface ReviewOverrideRequest {
  authority_id: number;

  reason: string;
}


/* ============================================================
   CHALLENGE SERVICE
============================================================ */

export const challengeService = {

  /* ----------------------------------------------------------
     GET CHALLENGES
  ---------------------------------------------------------- */

  async getChallenges(
    skip = 0,
    limit = 100,
  ): Promise<Challenge[]> {
    const response =
      await api.get<Challenge[]>(
        "/challenges",
        {
          params: {
            skip,
            limit,
          },
        },
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     GET SINGLE CHALLENGE
  ---------------------------------------------------------- */

  async getChallenge(
    challengeId: number,
  ): Promise<Challenge> {
    const response =
      await api.get<Challenge>(
        `/challenges/${challengeId}`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     GET MY CHALLENGES
     Useful for citizen-side screens
  ---------------------------------------------------------- */

  async getMyChallenges(): Promise<Challenge[]> {
    const response =
      await api.get<Challenge[]>(
        "/challenges/my",
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     REVIEW QUEUE
  ---------------------------------------------------------- */

  async getReviewQueue(): Promise<Challenge[]> {
    const response =
      await api.get<Challenge[]>(
        "/reviews/queue",
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     ROUTING RECOMMENDATION
  ---------------------------------------------------------- */

  async getRoutingRecommendation(
    challengeId: number,
  ): Promise<RoutingRecommendation> {
    const response =
      await api.get<RoutingRecommendation>(
        `/routing/challenges/${challengeId}/recommendation`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     ASSIGN CHALLENGE
  ---------------------------------------------------------- */

  async assignChallenge(
    challengeId: number,
    payload: ChallengeAssignmentRequest,
  ): Promise<Challenge> {
    const response =
      await api.post<Challenge>(
        `/challenges/${challengeId}/assign`,
        payload,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     AUTO ROUTE
  ---------------------------------------------------------- */

  async autoRouteChallenge(
    challengeId: number,
  ): Promise<Challenge> {
    const response =
      await api.post<Challenge>(
        `/challenges/${challengeId}/auto-route`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     REASSIGN CHALLENGE
  ---------------------------------------------------------- */

  async reassignChallenge(
    challengeId: number,
    payload: ChallengeReassignRequest,
  ): Promise<Challenge> {
    const response =
      await api.post<Challenge>(
        `/challenges/${challengeId}/reassign`,
        payload,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     ESCALATE CHALLENGE
  ---------------------------------------------------------- */

  async escalateChallenge(
    challengeId: number,
    payload: ChallengeEscalateRequest,
  ): Promise<Challenge> {
    const response =
      await api.post<Challenge>(
        `/challenges/${challengeId}/escalate`,
        payload,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     ACCEPT AI RECOMMENDATION
  ---------------------------------------------------------- */

  async acceptRecommendation(
    challengeId: number,
  ): Promise<Challenge> {
    const response =
      await api.post<Challenge>(
        `/reviews/${challengeId}/accept`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     OVERRIDE AI RECOMMENDATION
  ---------------------------------------------------------- */

  async overrideRecommendation(
    challengeId: number,
    payload: ReviewOverrideRequest,
  ): Promise<Challenge> {
    const response =
      await api.post<Challenge>(
        `/reviews/${challengeId}/override`,
        payload,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     ASSIGNMENT HISTORY
  ---------------------------------------------------------- */

  async getAssignmentHistory(
    challengeId: number,
  ): Promise<AssignmentHistoryItem[]> {
    const response =
      await api.get<AssignmentHistoryItem[]>(
        `/challenges/${challengeId}/assignment-history`,
      );

    return response.data;
  },


  /* ----------------------------------------------------------
     REVIEW HISTORY
  ---------------------------------------------------------- */

  async getReviewHistory(
    challengeId: number,
  ): Promise<ReviewHistoryItem[]> {
    const response =
      await api.get<ReviewHistoryItem[]>(
        `/reviews/${challengeId}/history`,
      );

    return response.data;
  },
};