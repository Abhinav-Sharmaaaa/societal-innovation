import type { UserRole } from "../types/auth";

export function getDashboardPath(
  role: UserRole,
): string {
  switch (role) {
    case "CITIZEN":
      return "/citizen/dashboard";

    case "SUPER_ADMIN":
    case "REVIEW_OFFICER":
    case "GOVERNMENT_OFFICER":
    case "MUNICIPALITY_OFFICER":
      return "/government/dashboard";

    case "UNIVERSITY_ADMIN":
    case "FACULTY":
    case "STUDENT":
      return "/university/dashboard";

    case "INDUSTRY_ADMIN":
    case "INDUSTRY_MEMBER":
      return "/industry/dashboard";

    default:
      return "/";
  }
}