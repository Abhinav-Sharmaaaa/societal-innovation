export type UserRole =
  | "SUPER_ADMIN"
  | "CITIZEN"
  | "MUNICIPALITY_OFFICER"
  | "GOVERNMENT_OFFICER"
  | "UNIVERSITY_ADMIN"
  | "FACULTY"
  | "STUDENT"
  | "INDUSTRY_ADMIN"
  | "INDUSTRY_MEMBER";


export interface User {
  id: number;
  full_name: string;
  email: string;
  phone: string | null;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
}


export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}


export interface LoginResponse {
  user: User;
  tokens: TokenResponse;
}


export interface RegisterRequest {
  full_name: string;
  email: string;
  phone?: string;
  password: string;
  role: "CITIZEN";
}


export interface LoginRequest {
  email: string;
  password: string;
}