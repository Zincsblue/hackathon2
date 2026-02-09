// User types
export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

// Task types
export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

// API response types
export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface TasksResponse {
  tasks: Task[];
  total: number;
  page: number;
  page_size: number;
}

export interface ErrorResponse {
  detail: string | ErrorDetail[];
}

export interface ErrorDetail {
  loc: string[];
  msg: string;
  type: string;
}

// Form types
export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  name: string;
}

export interface TaskFormData {
  title: string;
  description?: string;
  completed?: boolean;
}
