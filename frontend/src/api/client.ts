const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

interface ApiResponse<T> {
  data: T;
}

interface ApiError {
  detail: string;
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
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'An error occurred');
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
