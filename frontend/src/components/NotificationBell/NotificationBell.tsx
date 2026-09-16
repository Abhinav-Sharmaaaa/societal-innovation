import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bell, Check, CheckCheck, Clock, X } from "lucide-react";
import {
  getNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from "../../services/notificationService";
import type { Notification } from "../../types/notification";
import "./NotificationBell.css";


// ============================================================
// Helpers
// ============================================================

function timeAgo(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function getPriorityColor(priority: string): string {
  switch (priority) {
    case "URGENT": return "var(--notif-urgent)";
    case "HIGH":   return "var(--notif-high)";
    case "MEDIUM": return "var(--notif-medium)";
    default:       return "var(--notif-low)";
  }
}

/**
 * Map notification_type to a clickable route.
 * Returns null if no specific route applies.
 */
function getNotificationLink(n: Notification): string | null {
  const type = n.notification_type?.toLowerCase() ?? "";

  if (n.notification_type === "CHALLENGE_RESOLVED") {
    return "/citizen/dashboard";
  }
  if (n.project_id) {
    return `/government/projects/${n.project_id}`;
  }
  if (type.includes("challenge")) return "/government/challenges";
  if (type.includes("proposal")) return "/government/rfps";
  if (type.includes("collaboration")) return "/government/collaborations";
  return null;
}


// ============================================================
// Component
// ============================================================

export default function NotificationBell() {
  const navigate = useNavigate();
  const panelRef = useRef<HTMLDivElement>(null);

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const unreadCount = notifications.filter((n) => !n.is_read).length;


  // ----------------------------------------------------------
  // Fetch notifications
  // ----------------------------------------------------------

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getNotifications();
      setNotifications(data);
    } catch {
      // Silently fail — don't break the navbar
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load + poll every 60 seconds
  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60_000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);


  // ----------------------------------------------------------
  // Close panel on outside click
  // ----------------------------------------------------------

  useEffect(() => {
    function handleOutsideClick(e: MouseEvent) {
      if (
        panelRef.current &&
        !panelRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    }

    if (open) {
      document.addEventListener("mousedown", handleOutsideClick);
    }

    return () =>
      document.removeEventListener("mousedown", handleOutsideClick);
  }, [open]);


  // ----------------------------------------------------------
  // Handlers
  // ----------------------------------------------------------

  async function handleMarkRead(n: Notification) {
    if (n.is_read) return;
    try {
      await markNotificationRead(n.id);
      setNotifications((prev) =>
        prev.map((x) => (x.id === n.id ? { ...x, is_read: true } : x))
      );
    } catch {/* ignore */}
  }

  async function handleMarkAllRead() {
    try {
      await markAllNotificationsRead(notifications);
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch {/* ignore */}
  }

  function handleClickNotification(n: Notification) {
    handleMarkRead(n);
    const link = getNotificationLink(n);
    if (link) {
      navigate(link);
      setOpen(false);
    }
  }


  // ----------------------------------------------------------
  // Render
  // ----------------------------------------------------------

  return (
    <div className="notif-bell-wrapper" ref={panelRef}>

      {/* ---- Bell Icon Button ---- */}
      <button
        id="notification-bell-btn"
        className="notif-bell-btn"
        onClick={() => setOpen((o) => !o)}
        aria-label={`Notifications${unreadCount > 0 ? `, ${unreadCount} unread` : ""}`}
        title="Notifications"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="notif-badge" aria-hidden="true">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>


      {/* ---- Dropdown Panel ---- */}
      {open && (
        <div className="notif-panel" role="dialog" aria-label="Notifications">

          {/* Panel Header */}
          <div className="notif-panel-header">
            <span className="notif-panel-title">
              Notifications
              {unreadCount > 0 && (
                <span className="notif-unread-pill">{unreadCount} new</span>
              )}
            </span>
            <div className="notif-panel-actions">
              {unreadCount > 0 && (
                <button
                  className="notif-mark-all-btn"
                  onClick={handleMarkAllRead}
                  title="Mark all as read"
                >
                  <CheckCheck size={14} />
                  Mark all read
                </button>
              )}
              <button
                className="notif-close-btn"
                onClick={() => setOpen(false)}
                aria-label="Close notifications"
              >
                <X size={16} />
              </button>
            </div>
          </div>


          {/* Panel Body */}
          <div className="notif-panel-body">
            {loading && notifications.length === 0 ? (
              <div className="notif-empty">
                <div className="notif-spinner" />
                <p>Loading notifications…</p>
              </div>
            ) : notifications.length === 0 ? (
              <div className="notif-empty">
                <Bell size={32} strokeWidth={1.5} />
                <p>You're all caught up!</p>
                <span>No notifications yet.</span>
              </div>
            ) : (
              <ul className="notif-list" role="list">
                {notifications.map((n) => (
                  <li
                    key={n.id}
                    className={`notif-item ${n.is_read ? "notif-item--read" : "notif-item--unread"}`}
                    onClick={() => handleClickNotification(n)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleClickNotification(n);
                    }}
                  >
                    {/* Priority bar */}
                    <span
                      className="notif-priority-bar"
                      style={{ background: getPriorityColor(n.priority) }}
                    />

                    <div className="notif-item-content">
                      <div className="notif-item-header">
                        <strong className="notif-item-title">
                          {n.title}
                        </strong>
                        {!n.is_read && (
                          <button
                            className="notif-read-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMarkRead(n);
                            }}
                            title="Mark as read"
                          >
                            <Check size={13} />
                          </button>
                        )}
                      </div>
                      <p className="notif-item-msg">{n.message}</p>
                      <div className="notif-item-meta">
                        <Clock size={11} />
                        <time dateTime={n.created_at}>
                          {timeAgo(n.created_at)}
                        </time>
                        <span className="notif-type-pill">
                          {n.notification_type.replace(/_/g, " ")}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

        </div>
      )}
    </div>
  );
}
