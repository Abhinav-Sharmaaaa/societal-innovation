import { api } from "./api";
import type { Notification } from "../types/notification";


/*
|--------------------------------------------------------------------------
| Get My Notifications
|--------------------------------------------------------------------------
*/

export async function getNotifications(): Promise<Notification[]> {
  const response = await api.get<Notification[]>("/notifications");
  return response.data;
}


/*
|--------------------------------------------------------------------------
| Mark Single Notification as Read
|--------------------------------------------------------------------------
*/

export async function markNotificationRead(
  notificationId: number
): Promise<Notification> {
  const response = await api.post<Notification>(
    `/notifications/${notificationId}/read`
  );
  return response.data;
}


/*
|--------------------------------------------------------------------------
| Mark All Notifications as Read (optimistic batch)
| NOTE: backend doesn't have a mark-all endpoint yet so we fan out
|--------------------------------------------------------------------------
*/

export async function markAllNotificationsRead(
  notifications: Notification[]
): Promise<void> {
  const unread = notifications.filter((n) => !n.is_read);
  await Promise.all(
    unread.map((n) => api.post(`/notifications/${n.id}/read`))
  );
}
