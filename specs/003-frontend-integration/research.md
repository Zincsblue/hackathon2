# Research: Frontend & Integration

**Feature**: 003-frontend-integration
**Date**: 2026-02-09
**Status**: Complete

---

## Overview

This document captures research findings and technology decisions for implementing the Next.js frontend that integrates with the existing FastAPI backend. The primary focus is on authentication flow, API client architecture, component structure, and testing strategy.

---

## Research Questions

### RQ-001: Frontend Testing Strategy

**Question**: What testing approach should be used for Next.js App Router with TypeScript?

**Research Focus**: Testing frameworks for React Server Components, Client Components, and E2E flows

**Decision**: Use Jest + React Testing Library for component/unit tests, Playwright for E2E tests

**Rationale**:
- **Jest + React Testing Library**: Industry standard for React component testing
  - Excellent TypeScript support
  - Works with Next.js App Router
  - Can test both Server and Client Components
  - Large ecosystem and community support
  - Built-in mocking capabilities

- **Playwright**: Official recommendation for Next.js E2E testing
  - Supports multiple browsers (Chrome, Firefox, Safari)
  - Handles authentication flows well
  - Can test responsive behavior across viewports
  - Better Next.js integration than Cypress
  - Parallel test execution
  - Built-in screenshot and video recording

**Testing Strategy**:

1. **Component Tests** (Jest + React Testing Library):
   - Test individual components in isolation
   - Mock API calls and auth context
   - Verify rendering, user interactions, form validation
   - Test loading states, error states, empty states
   - Coverage target: 80%+ for components

2. **E2E Tests** (Playwright):
   - Test complete user flows (sign up → login → create task → logout)
   - Verify authentication redirects
   - Test task CRUD operations with real API calls
   - Validate responsive behavior on different viewports (320px, 768px, 1920px)
   - Confirm user data isolation (multiple user accounts)
   - Coverage: Critical user paths (P1 and P2 user stories)

3. **API Client Tests** (Jest):
   - Test JWT token injection
   - Test token refresh logic
   - Test error handling and retry logic
   - Mock fetch responses

**Alternatives Considered**:
- **Vitest**: Faster than Jest but less mature ecosystem for Next.js
- **Cypress**: Popular but Playwright has better Next.js support and is recommended in official docs
- **Testing Library alone**: Need E2E tool for full flow validation

**Implementation Notes**:
- Configure Jest with `next/jest` for Next.js compatibility
- Use `@testing-library/react` for component tests
- Use `@playwright/test` for E2E tests
- Mock `fetch` calls in component tests
- Use test database or mock backend for E2E tests

---

## Technology Decisions

### TD-001: Next.js App Router Architecture

**Decision**: Use Next.js 16+ App Router with route groups for authentication state separation

**Rationale**:
- **Route Groups**: `(auth)` and `(dashboard)` groups allow different layouts and middleware behavior
- **Server Components by default**: Better performance for initial page loads
- **Client Components where needed**: Interactive forms, auth context, real-time updates
- **Middleware for route protection**: Centralized authentication checks before page rendering
- **Layouts for shared UI**: Dashboard layout includes header/navigation, auth layout is minimal

**Structure**:
```
app/
├── (auth)/           # Unauthenticated pages
│   ├── login/
│   └── register/
├── (dashboard)/      # Authenticated pages
│   ├── layout.tsx    # Auth check + shared layout
│   ├── page.tsx      # Task dashboard
│   └── tasks/
└── middleware.ts     # Route protection
```

**Benefits**:
- Clear separation of authenticated vs unauthenticated routes
- Shared layouts reduce code duplication
- Middleware provides early authentication checks
- Server Components improve performance

---

### TD-002: API Client Architecture

**Decision**: Create centralized API client with automatic JWT token injection and refresh handling

**Rationale**:
- **Centralized logic**: All API calls go through single client
- **Automatic token injection**: No manual header management in components
- **Token refresh handling**: Automatically refresh expired tokens
- **Error handling**: Consistent error responses across app
- **Type safety**: TypeScript interfaces for all API responses

**Implementation Pattern**:
```typescript
// lib/api-client.ts
class ApiClient {
  private baseUrl: string;
  private getAccessToken: () => string | null;
  private refreshToken: () => Promise<string>;

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    // 1. Get access token from auth context
    // 2. Attach Authorization header
    // 3. Make request
    // 4. If 401, try refresh token
    // 5. Retry original request
    // 6. Return typed response
  }

  // Convenience methods
  async get<T>(endpoint: string): Promise<T>
  async post<T>(endpoint: string, data: any): Promise<T>
  async patch<T>(endpoint: string, data: any): Promise<T>
  async delete<T>(endpoint: string): Promise<T>
}
```

**Benefits**:
- DRY principle - no repeated auth logic
- Automatic token refresh prevents user disruption
- Type safety catches errors at compile time
- Easy to mock for testing
- Single place to add logging, retry logic, etc.

**Alternatives Considered**:
- **Axios**: Popular but fetch is native and sufficient
- **SWR/React Query**: Good for caching but adds complexity for MVP
- **Manual fetch in components**: Too much duplication

---

### TD-003: Authentication State Management

**Decision**: Use React Context for auth state with memory storage for access tokens

**Rationale**:
- **React Context**: Simple, built-in, no external dependencies
- **Memory storage for access tokens**: More secure than localStorage (XSS protection)
- **httpOnly cookies for refresh tokens**: Backend sets these, frontend can't access (XSS protection)
- **Context provides**: User data, login/logout functions, loading state

**Implementation Pattern**:
```typescript
// contexts/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<string>;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize: check if user is logged in
  useEffect(() => {
    // Try to refresh token on mount
    // If successful, user is logged in
    // If fails, user is logged out
  }, []);

  // Login, register, logout, refresh functions
  // ...

  return (
    <AuthContext.Provider value={{ user, accessToken, isLoading, login, register, logout, refreshAccessToken }}>
      {children}
    </AuthContext.Provider>
  );
}
```

**Benefits**:
- Simple to implement and understand
- No external dependencies
- Access token in memory (not localStorage) is more secure
- Context makes auth state available throughout app
- Easy to test with mock provider

**Alternatives Considered**:
- **Redux**: Overkill for simple auth state
- **Zustand**: Good but adds dependency
- **localStorage for tokens**: Less secure (XSS vulnerability)
- **Better Auth library**: Spec requires custom JWT implementation

---

### TD-004: Route Protection Strategy

**Decision**: Use Next.js middleware for route protection with redirect to login

**Rationale**:
- **Middleware runs before page rendering**: Efficient, no flash of protected content
- **Centralized logic**: Single place to define protected routes
- **Redirect to login**: Unauthenticated users sent to login page
- **Preserve intended destination**: Redirect back after login

**Implementation Pattern**:
```typescript
// middleware.ts
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

**Benefits**:
- Runs before page rendering (no flash of content)
- Simple cookie check (refresh token presence)
- Automatic redirects
- Preserves intended destination
- Prevents authenticated users from seeing login page

**Alternatives Considered**:
- **Layout-level checks**: Would cause flash of content
- **Component-level checks**: Too late, page already rendered
- **Server Component checks**: Good but middleware is more efficient

---

### TD-005: Form Validation Strategy

**Decision**: Client-side validation with HTML5 + custom validation, server-side validation via API

**Rationale**:
- **Client-side validation**: Immediate feedback, better UX
- **HTML5 validation**: Built-in, no dependencies (required, email, minLength)
- **Custom validation**: Additional rules (password strength, email format)
- **Server-side validation**: Security, final authority on data validity
- **Display field-level errors**: Show errors next to fields

**Implementation Pattern**:
```typescript
// components/auth/LoginForm.tsx
export function LoginForm() {
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    // Client-side validation
    const newErrors: Record<string, string> = {};
    if (!email) newErrors.email = 'Email is required';
    if (!password) newErrors.password = 'Password is required';
    if (password.length < 8) newErrors.password = 'Password must be at least 8 characters';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Call API
    try {
      await login(email, password);
    } catch (error) {
      // Display server errors
      if (error.status === 422) {
        setErrors(error.fieldErrors);
      } else {
        setErrors({ general: error.message });
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" required />
      {errors.email && <span>{errors.email}</span>}
      {/* ... */}
    </form>
  );
}
```

**Benefits**:
- Immediate feedback improves UX
- HTML5 validation is free
- Server validation ensures security
- Field-level errors are clear
- Prevents invalid submissions

---

### TD-006: Loading and Error State Handling

**Decision**: Use React state for loading/error with dedicated UI components

**Rationale**:
- **Loading state**: Show spinner during API calls, disable submit buttons
- **Error state**: Display error messages with retry option
- **Empty state**: Show helpful message when no tasks exist
- **Optimistic updates**: Optional for better perceived performance

**Implementation Pattern**:
```typescript
// components/tasks/TaskList.tsx
export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.get<TasksResponse>('/tasks');
      setTasks(data.tasks);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={loadTasks} />;
  if (tasks.length === 0) return <TaskEmpty />;

  return <div>{tasks.map(task => <TaskItem key={task.id} task={task} />)}</div>;
}
```

**Benefits**:
- Clear feedback to users
- Prevents duplicate submissions
- Retry option for errors
- Empty state guides users
- Consistent patterns across app

---

## Best Practices

### BP-001: Component Organization

**Practice**: Separate Server Components and Client Components clearly

**Guidelines**:
- Use `'use client'` directive only when needed (forms, context, interactivity)
- Keep Server Components for data fetching and static content
- Pass data from Server to Client Components via props
- Minimize Client Component bundle size

**Example**:
```typescript
// app/(dashboard)/page.tsx (Server Component)
export default async function DashboardPage() {
  // Could fetch initial data here if needed
  return (
    <div>
      <h1>My Tasks</h1>
      <TaskList /> {/* Client Component */}
    </div>
  );
}

// components/tasks/TaskList.tsx (Client Component)
'use client';
export function TaskList() {
  // Interactive logic, API calls, state
}
```

---

### BP-002: Type Safety

**Practice**: Define TypeScript interfaces for all API responses and component props

**Guidelines**:
- Create `lib/types.ts` with all type definitions
- Use interfaces for API responses
- Use types for component props
- Enable strict TypeScript mode

**Example**:
```typescript
// lib/types.ts
export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface TasksResponse {
  tasks: Task[];
  total: number;
  page: number;
  page_size: number;
}
```

---

### BP-003: Environment Configuration

**Practice**: Use environment variables for backend API URL

**Guidelines**:
- Create `.env.local` for local development (not committed)
- Create `.env.example` as template (committed)
- Use `NEXT_PUBLIC_` prefix for client-side variables
- Validate environment variables on startup

**Example**:
```bash
# .env.example
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001/api/v1
```

---

## Summary

All research questions have been resolved with clear decisions and rationale. The frontend architecture is designed to:

1. **Integrate seamlessly** with existing backend (Spec-1 + Spec-2)
2. **Enforce security** through JWT authentication and route protection
3. **Provide excellent UX** with loading states, error handling, and responsive design
4. **Maintain code quality** through TypeScript, testing, and best practices
5. **Follow Next.js conventions** using App Router, Server/Client Components, and middleware

**Next Steps**: Proceed to Phase 1 (Design & Contracts) to define data models and API contracts.
