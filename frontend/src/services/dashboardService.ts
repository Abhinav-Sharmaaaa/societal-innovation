import { api } from "./api";

export interface GovernmentDashboard {
  challenge_stats: {
    total: number;
    submitted: number;
    under_review: number;
    routed: number;
    in_progress: number;
    resolved: number;
    rejected: number;
    closed: number;
    innovation_required: number;
    high_priority: number;
  };

  project_stats: {
    total: number;
    planning: number;
    active: number;
    on_hold: number;
    completed: number;
    cancelled: number;
  };

  project_health: {
    on_track: number;
    at_risk: number;
    delayed: number;
    critical: number;
  };

  ecosystem: {
    universities: number;
    industries: number;
  };

  funding: {
    allocated: number;
    disbursed: number;
    utilized: number;
    refunded: number;
    remaining: number;
  };

  impact: {
    verified_outcomes: number;
    total_beneficiaries: number;
    average_project_progress: number;
  };

  distribution: {
    challenge_categories: Record<string, number>;
    challenge_districts: {
      district: string;
      challenge_count: number;
    }[];
  };
}

export interface UniversityDashboard {
  organization_id: number;

  invitations: {
    total: number;
    interested: number;
    declined: number;
    proposal_submitted: number;
  };

  proposals: {
    total: number;
    submitted: number;
    under_evaluation: number;
    shortlisted: number;
    rejected: number;
  };

  industry_collaboration: {
    total: number;
    submitted: number;
    accepted: number;
  };

  projects: {
    total: number;
    planning: number;
    active: number;
    on_hold: number;
    completed: number;
  };

  milestones: {
    total: number;
    completed: number;
    delayed: number;
  };

  deliverables: {
    total: number;
    approved: number;
    rejected: number;
  };

  impact: {
    verified_outcomes: number;
    beneficiaries: number;
    average_project_progress: number;
  };

  reputation: {
    total_points: number;
    contribution_count: number;
  };
}

export interface IndustryDashboard {
  organization_id: number;

  collaborations: {
    total: number;
    draft: number;
    submitted: number;
    under_review: number;
    accepted: number;
    rejected: number;
  };

  projects: {
    total: number;
    planning: number;
    active: number;
    on_hold: number;
    completed: number;
  };

  milestones: {
    total: number;
    completed: number;
    delayed: number;
    blocked: number;
  };

  deliverables: {
    total: number;
    approved: number;
    rejected: number;
  };

  funding: {
    allocated: number;
    disbursed: number;
    utilized: number;
    refunded: number;
  };

  impact: {
    verified_outcomes: number;
    beneficiaries: number;
    average_project_progress: number;
  };

  reputation: {
    total_points: number;
    contribution_count: number;
  };
}

export interface CitizenDashboard {
  user_id: number;

  challenge_stats: {
    total: number;
    submitted: number;
    under_review: number;
    routed: number;
    in_progress: number;
    resolved: number;
    rejected: number;
    closed: number;
    innovation_required: number;
  };

  reputation: {
    total_points: number;
    contribution_count: number;
  };

  recent_challenges: {
    id: number;
    title: string;
    status: string;
    category: string;
    urgency: string;
    innovation_required: boolean;
    district: string | null;
    state: string | null;
    current_authority_id: number | null;
    created_at: string;
    updated_at: string;
  }[];
}

export interface ActionCenter {
  summary: {
    total: number;
    unread: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
  };

  notifications: {
    id: number;
    type: string;
    priority: string;
    title: string;
    message: string;
    project_id: number | null;
    is_read: boolean;
    created_at: string;
    read_at: string | null;
  }[];
}

export interface AnalyticsOverview {
  challenges: {
    total: number;
    resolved: number;
    innovation_required: number;
    resolution_rate: number;
  };

  projects: {
    total: number;
    active: number;
    completed: number;
  };

  ecosystem: {
    universities: number;
    industries: number;
  };

  impact: {
    verified_outcomes: number;
    beneficiaries: number;
  };
}

export interface DistrictAnalytics {
  district: string;
  challenge_count: number;
  resolved_count: number;
  innovation_count: number;
}

export interface UniversityLeaderboardItem {
  organization_id: number;
  organization_name: string;
  reputation_points: number;
  projects: number;
  completed_projects: number;
  verified_outcomes: number;
}

export interface IndustryLeaderboardItem {
  organization_id: number;
  organization_name: string;
  reputation_points: number;
  projects: number;
  completed_projects: number;
  funding_contribution: number;
}

export const dashboardService = {
  async getGovernmentDashboard(): Promise<GovernmentDashboard> {
    const response = await api.get(
      "/dashboard/government",
    );

    return response.data;
  },

  async getUniversityDashboard(): Promise<UniversityDashboard> {
    const response = await api.get(
      "/university-dashboard",
    );

    return response.data;
  },

  async getIndustryDashboard(): Promise<IndustryDashboard> {
    const response = await api.get(
      "/industry-dashboard",
    );

    return response.data;
  },

  async getCitizenDashboard(): Promise<CitizenDashboard> {
    const response = await api.get(
      "/citizen-dashboard",
    );

    return response.data;
  },

  async getActionCenter(): Promise<ActionCenter> {
    const response = await api.get(
      "/action-center",
    );

    return response.data;
  },

  async getAnalyticsOverview(): Promise<AnalyticsOverview> {
    const response = await api.get(
      "/analytics/overview",
    );

    return response.data;
  },

  async getDistrictAnalytics(): Promise<
    DistrictAnalytics[]
  > {
    const response = await api.get(
      "/analytics/districts",
    );

    return response.data;
  },

  async getUniversityLeaderboard(): Promise<
    UniversityLeaderboardItem[]
  > {
    const response = await api.get(
      "/analytics/universities",
    );

    return response.data;
  },

  async getIndustryLeaderboard(): Promise<
    IndustryLeaderboardItem[]
  > {
    const response = await api.get(
      "/analytics/industries",
    );

    return response.data;
  },
};