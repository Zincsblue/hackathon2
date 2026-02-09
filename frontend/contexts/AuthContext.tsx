'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, TokenResponse } from '@/lib/types';
import { ApiClient } from '@/lib/api-client';

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<string>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Create API client
  const apiClient = new ApiClient({
    baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL!,
    getAccessToken: () => accessToken,
    setAccessToken: (token) => setAccessToken(token),
    onUnauthorized: () => {
      setUser(null);
      setAccessToken(null);
    },
  });

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Try to refresh token to check if user is logged in
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          credentials: 'include',
        });

        if (response.ok) {
          const data: TokenResponse = await response.json();
          setAccessToken(data.access_token);

          // Fetch user profile
          const userResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${data.access_token}` },
          });

          if (userResponse.ok) {
            const userData: User = await userResponse.json();
            setUser(userData);
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const data = await apiClient.post<TokenResponse>('/auth/login', { email, password }, true);
    setAccessToken(data.access_token);

    // Fetch user profile
    const userData = await apiClient.get<User>('/auth/me');
    setUser(userData);
  };

  const register = async (email: string, password: string, name: string) => {
    const data = await apiClient.post<TokenResponse>('/auth/register', { email, password, name }, true);
    setAccessToken(data.access_token);

    // Fetch user profile
    const userData = await apiClient.get<User>('/auth/me');
    setUser(userData);
  };

  const logout = async () => {
    await apiClient.post('/auth/logout');
    setUser(null);
    setAccessToken(null);
  };

  const refreshAccessToken = async (): Promise<string> => {
    const data = await apiClient.post<TokenResponse>('/auth/refresh', null, true);
    setAccessToken(data.access_token);
    return data.access_token;
  };

  return (
    <AuthContext.Provider value={{ user, accessToken, isLoading, login, register, logout, refreshAccessToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
