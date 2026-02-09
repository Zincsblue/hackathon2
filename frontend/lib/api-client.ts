export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body: any
  ) {
    super(`API Error ${status}: ${statusText}`);
  }
}

export interface ApiClientConfig {
  baseUrl: string;
  getAccessToken: () => string | null;
  setAccessToken: (token: string) => void;
  onUnauthorized: () => void;
}

export class ApiClient {
  constructor(private config: ApiClientConfig) {}

  async request<T>(endpoint: string, options?: RequestInit & { skipAuth?: boolean }): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    };

    // Add Authorization header unless skipAuth is true
    if (!options?.skipAuth) {
      const token = this.config.getAccessToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    let response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include', // Include cookies for refresh token
    });

    // Handle 401 - try to refresh token
    if (response.status === 401 && !options?.skipAuth) {
      try {
        // Attempt token refresh
        const refreshResponse = await fetch(`${this.config.baseUrl}/auth/refresh`, {
          method: 'POST',
          credentials: 'include',
        });

        if (refreshResponse.ok) {
          const data = await refreshResponse.json();
          this.config.setAccessToken(data.access_token);

          // Retry original request with new token
          headers['Authorization'] = `Bearer ${data.access_token}`;
          response = await fetch(url, { ...options, headers, credentials: 'include' });
        } else {
          // Refresh failed - user needs to login again
          this.config.onUnauthorized();
          throw new ApiError(401, 'Unauthorized', { detail: 'Session expired' });
        }
      } catch (error) {
        this.config.onUnauthorized();
        throw error;
      }
    }

    // Handle non-2xx responses
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new ApiError(response.status, response.statusText, body);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any, skipAuth = false): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      skipAuth,
    });
  }

  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}
