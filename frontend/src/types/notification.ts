// ============================================================
// Notification Types
// ============================================================

export interface Notification {
  id: number;
  user_id: number;
  project_id: number | null;
  challenge_id?: number | null;
  notification_type: string;
  priority: "LOW" | "MEDIUM" | "HIGH" | "URGENT";
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  read_at: string | null;
}
