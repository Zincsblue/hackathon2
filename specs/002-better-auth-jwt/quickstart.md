# Quickstart Guide: Authentication & Security

**Feature**: Authentication & Security (002-better-auth-jwt)
**Date**: 2026-02-08
**Audience**: Developers implementing the authentication system

## Overview

This guide provides step-by-step instructions for implementing JWT-based authentication in the Todo Full-Stack Web Application. It covers backend setup (FastAPI), frontend integration (Next.js + Better Auth), and end-to-end testing.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Completed Spec-1 (Backend Core & Data Layer) implementation
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ Neon PostgreSQL database configured
- ✅ Redis server running (for rate limiting)
- ✅ Email service configured (for password reset)

---

## Part 1: Backend Setup (FastAPI)

### Step 1: Install Dependencies

Add authentication dependencies to `requirements.txt`:

```bash
# Authentication & Security
python-jose[cryptography]==3.3.0
argon2-cffi==23.1.0
slowapi==0.1.9
redis==5.0.1
python-multipart==0.0.6
pydantic[email]==2.5.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Update `.env` file with authentication settings:

```bash
# Existing settings
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
LOG_LEVEL=info

# Authentication Settings (NEW)
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting (NEW)
REDIS_URL=redis://localhost:6379

# Email Service (NEW - for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com
```

**Generate SECRET_KEY**:
```bash
openssl rand -hex 32
```

### Step 3: Run Database Migration

Create and apply the authentication migration:

```bash
# Generate migration
alembic revision --autogenerate -m "Add authentication tables"

# Review the generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

Expected tables created:
- `users` (extended with auth fields)
- `refresh_tokens`
- `password_reset_tokens`

### Step 4: Start Backend Server

```bash
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

Verify server is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Task Management API",
  "version": "1.0.0"
}
```

---

## Part 2: Test Authentication Endpoints

### Test 1: User Registration

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

Expected response (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "is_active": true,
    "is_verified": false,
    "created_at": "2026-02-08T10:30:00Z"
  }
}
```

**Note**: Save the `access_token` for subsequent requests.

### Test 2: User Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

Expected response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "is_active": true,
    "is_verified": false,
    "last_login_at": "2026-02-08T10:35:00Z"
  }
}
```

### Test 3: Access Protected Endpoint

Test that task endpoints now require authentication:

```bash
# Without token (should fail with 401)
curl http://localhost:8000/api/v1/users/test-user/tasks

# With token (should succeed)
curl http://localhost:8000/api/v1/users/test-user/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Test 4: Get Current User

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

Expected response (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "is_active": true,
  "is_verified": false,
  "last_login_at": "2026-02-08T10:35:00Z",
  "created_at": "2026-02-08T10:30:00Z"
}
```

### Test 5: Token Refresh

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Cookie: refresh_token=YOUR_REFRESH_TOKEN_HERE"
```

Expected response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Test 6: Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Cookie: refresh_token=YOUR_REFRESH_TOKEN_HERE"
```

Expected response (204 No Content):
- Empty body
- Cookie cleared

---

## Part 3: Frontend Setup (Next.js + Better Auth)

### Step 1: Install Dependencies

```bash
cd frontend
npm install better-auth
```

### Step 2: Configure Better Auth

Create `lib/auth.ts`:

```typescript
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  database: {
    // Use same Neon database as backend
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  secret: process.env.BETTER_AUTH_SECRET!, // Same as backend SECRET_KEY
})
```

### Step 3: Create Auth API Route

Create `app/api/auth/[...all]/route.ts`:

```typescript
import { auth } from "@/lib/auth"

export const { GET, POST } = auth.handler
```

### Step 4: Create Auth Context

Create `contexts/AuthContext.tsx`:

```typescript
"use client"

import { createContext, useContext, useState, useEffect } from "react"

interface User {
  id: string
  email: string
  is_active: boolean
}

interface AuthContextType {
  user: User | null
  accessToken: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Initialize: Check for existing session
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Try to refresh token on app load
        const response = await fetch("http://localhost:8000/api/v1/auth/refresh", {
          method: "POST",
          credentials: "include", // Include cookies
        })

        if (response.ok) {
          const data = await response.json()
          setAccessToken(data.access_token)

          // Fetch user profile
          const userResponse = await fetch("http://localhost:8000/api/v1/auth/me", {
            headers: {
              Authorization: `Bearer ${data.access_token}`,
            },
          })

          if (userResponse.ok) {
            const userData = await userResponse.json()
            setUser(userData)
          }
        }
      } catch (error) {
        console.error("Auth initialization failed:", error)
      } finally {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [])

  const register = async (email: string, password: string) => {
    const response = await fetch("http://localhost:8000/api/v1/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      credentials: "include",
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail)
    }

    const data = await response.json()
    setAccessToken(data.access_token)
    setUser(data.user)
  }

  const login = async (email: string, password: string) => {
    const response = await fetch("http://localhost:8000/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      credentials: "include",
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail)
    }

    const data = await response.json()
    setAccessToken(data.access_token)
    setUser(data.user)
  }

  const logout = async () => {
    await fetch("http://localhost:8000/api/v1/auth/logout", {
      method: "POST",
      credentials: "include",
    })

    setAccessToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, accessToken, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return context
}
```

### Step 5: Create Login Page

Create `app/login/page.tsx`:

```typescript
"use client"

import { useState } from "react"
import { useAuth } from "@/contexts/AuthContext"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    try {
      await login(email, password)
      router.push("/dashboard")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-4">
        <h1 className="text-2xl font-bold">Login</h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          required
        />

        <button
          type="submit"
          className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
        >
          Login
        </button>

        <p className="text-center">
          Don't have an account?{" "}
          <a href="/register" className="text-blue-500 hover:underline">
            Register
          </a>
        </p>
      </form>
    </div>
  )
}
```

### Step 6: Create API Client with Auth

Create `lib/api.ts`:

```typescript
import { useAuth } from "@/contexts/AuthContext"

export function useApiClient() {
  const { accessToken } = useAuth()

  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    const response = await fetch(`http://localhost:8000${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`)
    }

    return response.json()
  }

  return { apiCall }
}
```

### Step 7: Protect Routes

Create `middleware.ts`:

```typescript
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  // Check if user has refresh token cookie
  const refreshToken = request.cookies.get("refresh_token")

  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith("/dashboard")) {
    if (!refreshToken) {
      return NextResponse.redirect(new URL("/login", request.url))
    }
  }

  // Redirect to dashboard if already logged in
  if (request.nextUrl.pathname === "/login" || request.nextUrl.pathname === "/register") {
    if (refreshToken) {
      return NextResponse.redirect(new URL("/dashboard", request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/register"],
}
```

---

## Part 4: End-to-End Testing

### Test Flow 1: Registration → Login → Access Tasks

1. **Register new user**:
   - Navigate to `http://localhost:3000/register`
   - Enter email and password
   - Submit form
   - Verify redirect to dashboard

2. **Access tasks**:
   - On dashboard, fetch tasks using authenticated API call
   - Verify only user's tasks are returned

3. **Logout**:
   - Click logout button
   - Verify redirect to login page
   - Verify cannot access dashboard without login

### Test Flow 2: Token Expiration Handling

1. **Login and wait 15 minutes**:
   - Access token expires
   - Make API call
   - Verify automatic token refresh
   - Verify API call succeeds with new token

2. **Close browser and reopen**:
   - Navigate to `http://localhost:3000/dashboard`
   - Verify automatic login (refresh token in cookie)
   - Verify access to protected resources

### Test Flow 3: Security Testing

1. **Test rate limiting**:
   - Attempt 6 login requests in 1 minute
   - Verify 6th request returns 429 Too Many Requests

2. **Test account lockout**:
   - Attempt 10 failed logins
   - Verify account locked for 15 minutes
   - Verify error message indicates lockout

3. **Test XSS protection**:
   - Try to access refresh token via JavaScript
   - Verify httpOnly cookie cannot be accessed

4. **Test unauthorized access**:
   - Remove access token
   - Attempt to access protected endpoint
   - Verify 401 Unauthorized response

---

## Part 5: Verification Checklist

### Backend Verification

- [ ] All authentication endpoints respond correctly
- [ ] Passwords are hashed with Argon2id
- [ ] JWT tokens are signed with HS256
- [ ] Access tokens expire in 15 minutes
- [ ] Refresh tokens expire in 7 days
- [ ] Rate limiting is enforced
- [ ] Account lockout works after 10 failures
- [ ] All task endpoints require authentication
- [ ] User can only access their own tasks

### Frontend Verification

- [ ] Registration form works
- [ ] Login form works
- [ ] Logout clears session
- [ ] Protected routes redirect to login
- [ ] Token refresh happens automatically
- [ ] Session persists across browser restarts
- [ ] API calls include Authorization header
- [ ] Error messages are user-friendly

### Security Verification

- [ ] HTTPS enforced in production
- [ ] Refresh tokens in httpOnly cookies
- [ ] Access tokens not persisted
- [ ] CORS configured correctly
- [ ] Rate limiting prevents brute force
- [ ] SQL injection prevented
- [ ] XSS protection enabled
- [ ] CSRF protection via sameSite cookies

---

## Troubleshooting

### Issue: "Could not validate credentials"

**Cause**: Invalid or expired access token

**Solution**:
1. Check token expiration (15 minutes)
2. Verify SECRET_KEY matches between frontend and backend
3. Check Authorization header format: `Bearer {token}`

### Issue: "Rate limit exceeded"

**Cause**: Too many requests in short time

**Solution**:
1. Wait for rate limit window to reset
2. Check Redis is running: `redis-cli ping`
3. Verify REDIS_URL in .env

### Issue: "Account locked"

**Cause**: 10 failed login attempts

**Solution**:
1. Wait 15 minutes for automatic unlock
2. Or manually reset in database:
   ```sql
   UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE email = 'user@example.com';
   ```

### Issue: Session not persisting

**Cause**: Refresh token cookie not set

**Solution**:
1. Verify `credentials: "include"` in fetch calls
2. Check cookie domain matches frontend domain
3. Verify CORS allows credentials
4. Check browser allows third-party cookies

---

## Next Steps

After completing this quickstart:

1. **Implement password reset flow** (email integration required)
2. **Add email verification** (optional enhancement)
3. **Set up monitoring** (log authentication events)
4. **Configure production environment** (HTTPS, secure cookies)
5. **Proceed to Spec-3** (Frontend UI implementation)

---

**Document Status**: Quickstart Complete
**Last Updated**: 2026-02-08
**Estimated Time**: 2-3 hours for full implementation
