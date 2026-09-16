import { api } from "./api";

export interface Organization {
  id: number;
  name: string;
  organization_type: OrganizationType;
  description: string | null;
  district: string | null;
  locality: string | null;
  state: string | null;
  email: string | null;
  phone: string | null;
  website: string | null;
  is_active: boolean;
}

export type OrganizationType =
  | "MUNICIPALITY"
  | "GOVERNMENT_DEPARTMENT"
  | "UNIVERSITY"
  | "INDUSTRY";

export interface OfficialUserCreate {
  full_name: string;
  email: string;
  phone?: string;
  password: string;
  role: OfficialRole;
  organization_id: number;
}

export type OfficialRole =
  | "REVIEW_OFFICER"
  | "MUNICIPALITY_OFFICER"
  | "GOVERNMENT_OFFICER"
  | "UNIVERSITY_ADMIN"
  | "FACULTY"
  | "STUDENT"
  | "INDUSTRY_ADMIN"
  | "INDUSTRY_MEMBER";

export interface OrganizationCreate {
  name: string;
  organization_type: OrganizationType;
  description?: string;
  district?: string;
  locality?: string;
  state?: string;
  email?: string;
  phone?: string;
  website?: string;
}

/*
|--------------------------------------------------------------------------
| Organizations
|--------------------------------------------------------------------------
*/

export async function listOrganizations(
  type?: OrganizationType
): Promise<Organization[]> {
  const params = type ? { organization_type: type } : {};
  const res = await api.get<Organization[]>("/organizations", { params });
  return res.data;
}

export async function createOrganization(
  data: OrganizationCreate
): Promise<Organization> {
  const res = await api.post<Organization>("/organizations", data);
  return res.data;
}

/*
|--------------------------------------------------------------------------
| Official Users
|--------------------------------------------------------------------------
*/

export async function createOfficialUser(
  data: OfficialUserCreate
): Promise<{ id: number; full_name: string; email: string; role: string }> {
  const res = await api.post("/admin/users", data);
  return res.data;
}
