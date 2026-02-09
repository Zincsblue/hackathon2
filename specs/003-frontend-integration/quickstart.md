# Quickstart Guide: Frontend & Integration

**Feature**: 003-frontend-integration
**Date**: 2026-02-09
**Audience**: Developers implementing the frontend

---

## Overview

This guide provides step-by-step instructions for setting up, developing, and testing the Next.js frontend that integrates with the existing FastAPI backend. Follow these steps to get the application running locally.

---

## Prerequisites

Before starting, ensure you have:

1. **Backend Running**: FastAPI backend from Spec-1 and Spec-2 must be running
   - Backend URL: `http://localhost:8001`
   - Health check: `http://localhost:8001/health`
   - API docs: `http://localhost:8001/docs`

2. **Node.js**: Version 18.x or higher
   - Check: `node --version`
   - Install: https://nodejs.org/

3. **npm or yarn**: Package manager
   - Check: `npm --version` or `yarn --version`

4. **Git**: For version control
   - Check: `git --version`

---

## Step 1: Project Setup

### 1.1 Create Next.js Project

```bash
# Navigate to project root
cd C:\Users\PMLS\OneDrive\Desktop\hackathon2phase2\phase

# Create Next.js app with TypeScript
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"

# Navigate to frontend directory
cd frontend
```

**Options explained**:
- `--typescript`: Enable TypeScript
- `--tailwind`: Include Tailwind CSS for styling
- `--app`: Use App Router (not Pages Router)
- `--no-src-dir`: Don't use src/ directory
- `--import-alias "@/*"`: Enable @ imports

### 1.2 Install Additional Dependencies

```bash
# Install development dependencies
npm install --save-dev @types/node @types/react @types/react-dom

# No additional runtime dependencies needed for MVP
# (fetch is built-in, no need for axios or other HTTP clients)
```

---

## Step 2: Environment Configuration

### 2.1 Create Environment Files

```bash
# Create .env.local (not committed to git)
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8001/api/v1" > .env.local

# Create .env.example (committed to git as template)
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8001/api/v1" > .env.example
```

### 2.2 Update .gitignore

Ensure `.env.local` is in `.gitignore`:

```bash
# Add to .gitignore if not already present
echo ".env.local" >> .gitignore
```

---

## Step 3: Create Core Infrastructure

### 3.1 Create Type Definitions

Create `lib/types.ts`:

```typescript
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
```

### 3.2 Create API Client

Create `lib/api-client.ts`:

```typescript
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
```

### 3.3 Create Auth Context

Create `contexts/AuthContext.tsx`:

```typescript
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
```

### 3.4 Create Middleware for Route Protection

Create `middleware.ts`:

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const refreshToken = request.cookies.get('refresh_token');
  const { pathname } = request.nextUrl;

  // Protected routes
  const protectedRoutes = ['/dashboard', '/tasks'];
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));

  // If protected route and no refresh token, redirect to login
  if (isProtectedRoute && !refreshToken) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If auth route and has refresh token, redirect to dashboard
  const authRoutes = ['/login', '/register'];
  const isAuthRoute = authRoutes.includes(pathname);
  if (isAuthRoute && refreshToken) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

---

## Step 4: Run Development Server

### 4.1 Start Backend (if not already running)

```bash
# In backend directory
cd C:\Users\PMLS\OneDrive\Desktop\hackathon2phase2\phase\backend
python -m uvicorn src.main:app --reload --port 8001
```

### 4.2 Start Frontend

```bash
# In frontend directory
cd C:\Users\PMLS\OneDrive\Desktop\hackathon2phase2\phase\frontend
npm run dev
```

**Expected output**:
```
> frontend@0.1.0 dev
> next dev

  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

### 4.3 Verify Setup

1. **Frontend**: Open http://localhost:3000
2. **Backend**: Open http://localhost:8001/docs
3. **Health Check**: http://localhost:8001/health

---

## Step 5: Development Workflow

### 5.1 Create Pages

Follow this order for implementation:

1. **Root Layout** (`app/layout.tsx`): Wrap with AuthProvider
2. **Landing Page** (`app/page.tsx`): Redirect to dashboard or login
3. **Login Page** (`app/(auth)/login/page.tsx`): Login form
4. **Register Page** (`app/(auth)/register/page.tsx`): Registration form
5. **Dashboard Layout** (`app/(dashboard)/layout.tsx`): Auth check + header
6. **Dashboard Page** (`app/(dashboard)/page.tsx`): Task list
7. **Task Pages**: Create, edit, detail pages

### 5.2 Create Components

1. **Auth Components**: LoginForm, RegisterForm
2. **Task Components**: TaskList, TaskItem, TaskForm
3. **UI Components**: Button, Input, LoadingSpinner, ErrorMessage
4. **Layout Components**: Header, Navigation

### 5.3 Testing Strategy

**Component Tests** (Jest + React Testing Library):
```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom jest-environment-jsdom
npm run test
```

**E2E Tests** (Playwright):
```bash
npm install --save-dev @playwright/test
npx playwright install
npx playwright test
```

---

## Step 6: Validation Checklist

Before considering the feature complete, verify:

### User Story 1: Authentication Flow
- [ ] User can register with email/password
- [ ] User receives JWT token on registration
- [ ] User can login with credentials
- [ ] User is redirected to dashboard after login
- [ ] Unauthenticated users are redirected to login
- [ ] User can logout successfully

### User Story 2: Task Management
- [ ] User can view their task list
- [ ] User can create a new task
- [ ] User can edit an existing task
- [ ] User can toggle task completion
- [ ] User can delete a task
- [ ] User only sees their own tasks

### User Story 3: Responsive UX
- [ ] Layout works on desktop (1920px)
- [ ] Layout works on tablet (768px)
- [ ] Layout works on mobile (320px)
- [ ] Touch targets are appropriately sized

### User Story 4: Error Handling
- [ ] Loading indicators show during API calls
- [ ] Error messages display on failures
- [ ] Empty state shows when no tasks exist
- [ ] Token refresh works automatically
- [ ] Session expiration redirects to login

---

## Step 7: Common Issues & Solutions

### Issue: CORS Error

**Symptom**: Browser console shows CORS error when calling API

**Solution**: Ensure backend CORS is configured for frontend origin:
```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Cookies Not Set

**Symptom**: Refresh token cookie not appearing in browser

**Solution**: Ensure `credentials: 'include'` in fetch calls and backend sets `httponly=True`

### Issue: Token Refresh Loop

**Symptom**: Infinite loop of refresh requests

**Solution**: Check that refresh endpoint uses `skipAuth: true` to avoid circular refresh

### Issue: Middleware Redirect Loop

**Symptom**: Page keeps redirecting

**Solution**: Verify middleware matcher excludes static files and API routes

---

## Step 8: Production Deployment

### 8.1 Build Frontend

```bash
npm run build
```

### 8.2 Update Environment Variables

```bash
# .env.production
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com/api/v1
```

### 8.3 Deploy

Options:
- **Vercel**: `vercel deploy` (recommended for Next.js)
- **Netlify**: Connect GitHub repo
- **Docker**: Create Dockerfile and deploy to cloud

---

## Summary

This quickstart guide covers:

1. ✅ Project setup with Next.js 16+ and TypeScript
2. ✅ Environment configuration
3. ✅ Core infrastructure (types, API client, auth context, middleware)
4. ✅ Development workflow
5. ✅ Validation checklist
6. ✅ Common issues and solutions
7. ✅ Production deployment

**Next Steps**: Follow the tasks.md file (generated by `/sp.tasks`) for detailed implementation steps.
