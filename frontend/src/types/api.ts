export enum UserRole {
  USER = 'user',
  RESEARCHER = 'researcher',
  ADMIN = 'admin'
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  is_active?: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export interface ResearchRequest {
  query: string;
}

export interface ResearchResponse {
  query: string;
  result_markdown: string;
}

export interface ApiError {
  detail: string;
}

export interface UserListItem {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

// For compliance mapping - assuming some structure
export interface ComplianceItem {
  id: string;
  title: string;
  status: 'compliant' | 'non-compliant' | 'pending';
  category: string;
  last_updated: string;
  details?: string;
}

export interface AgentStatus {
  id: string;
  name: string;
  status: 'idle' | 'running' | 'error';
  progress?: number;
  last_activity: string;
}

export interface DashboardMetrics {
  total_users: number;
  active_research_queries: number;
  compliance_score: number;
  system_health: 'healthy' | 'warning' | 'critical';
}