const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

interface ApiResponse<T> {
  data: T;
}

interface ApiError {
  detail: string;
}

export class ApiRequestError extends Error {
  status: number;
  detail?: string;

  constructor(status: number, detail?: string) {
    super(detail || 'An error occurred');
    this.name = 'ApiRequestError';
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('token');

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail: string | undefined;
    try {
      const error: ApiError = await response.json();
      if (error && typeof error.detail === 'string') {
        detail = error.detail;
      }
    } catch {
      // Ignore JSON parsing errors for non-JSON responses.
    }
    throw new ApiRequestError(response.status, detail);
  }

  return response.json();
}

export const api = {
  get: <T>(endpoint: string) => request<T>(endpoint),
  post: <T>(endpoint: string, data: unknown) =>
    request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  put: <T>(endpoint: string, data: unknown) =>
    request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: <T>(endpoint: string) =>
    request<T>(endpoint, { method: 'DELETE' }),
};

// Auth specific functions
export interface RegisterData {
  email: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface UserData {
  id: number;
  email: string;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserData;
}

export interface RefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ProjectData {
  id: number;
  name: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectData {
  name: string;
}

export const authApi = {
  register: (data: RegisterData) =>
    api.post<ApiResponse<UserData>>('/auth/register', data),
  login: (data: LoginData) =>
    api.post<ApiResponse<LoginResponse>>('/auth/login', data),
  refresh: (refresh_token: string) =>
    api.post<ApiResponse<RefreshResponse>>('/auth/refresh', { refresh_token }),
  me: () => api.get<ApiResponse<UserData>>('/auth/me'),
  logout: (refresh_token: string) =>
    api.post<null>('/auth/logout', { refresh_token }),
};

export const projectsApi = {
  list: () => api.get<ApiResponse<ProjectData[]>>('/projects'),
  create: (data: CreateProjectData) =>
    api.post<ApiResponse<ProjectData>>('/projects', data),
  get: (id: number) => api.get<ApiResponse<ProjectData>>(`/projects/${id}`),
};
