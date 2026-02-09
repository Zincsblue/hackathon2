---
id: 002
title: Frontend Integration Planning Complete
stage: plan
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: 003-frontend-integration
branch: 003-frontend-integration
user: PMLS
command: /sp.plan
labels: ["planning", "architecture", "frontend", "nextjs", "design", "contracts"]
links:
  spec: specs/003-frontend-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-frontend-integration/plan.md
  - specs/003-frontend-integration/research.md
  - specs/003-frontend-integration/data-model.md
  - specs/003-frontend-integration/contracts/frontend-api-client.md
  - specs/003-frontend-integration/quickstart.md
  - CLAUDE.md (updated with new technology stack)
tests:
  - Constitution Check: All principles PASS (6/6)
  - Technology Stack Compliance: All requirements PASS (5/5)
  - Post-Design Constitution Check: All principles PASS (6/6)
---

## Prompt

User ran `/sp.plan` command with architectural requirements:

**Requirements**: "Create Frontend architecture using Next.js App Router. Auth-aware routing and protected pages. API client layer with automatic JWT header injection. Task management UI components. Decisions needing documentation: Page and component structure for task workflows. Strategy for handling loading, error, and empty states. Auth redirect behavior for unauthenticated users. Testing & validation: Verify full CRUD task flow for authenticated users. Confirm user isolation across multiple accounts. Validate responsive behavior on different screen sizes."

**Context**: Following completion of Spec-3 (Frontend & Integration), user requested architectural planning to design the Next.js frontend implementation that integrates with existing backend (Spec-1 and Spec-2).

## Response snapshot

Successfully completed comprehensive architectural planning for Frontend & Integration feature with all phases complete.

**Phase 0: Research & Technology Decisions**

Resolved all technology questions and documented decisions:

1. **Testing Strategy (RT-001)**: Jest + React Testing Library for components, Playwright for E2E
   - Rationale: Industry standard, excellent Next.js support, comprehensive coverage
   - Strategy: Component tests for isolation, E2E tests for user flows, API client tests for token management

**Phase 1: Design & Contracts**

Generated complete design artifacts:

1. **data-model.md** (68KB):
   - Frontend data models: User, Task, TokenResponse, TasksResponse, ErrorResponse
   - Form data models: LoginFormData, RegisterFormData, TaskFormData
   - UI state models: AuthState, TaskListState
   - Data flow diagrams: Authentication flow (9 steps), Task CRUD flow (6 operations), Token refresh flow (10 steps)
   - State transitions documented for all models

2. **contracts/frontend-api-client.md** (71KB):
   - ApiClient class interface with automatic JWT injection
   - 11 API endpoint specifications:
     - 5 authentication endpoints: register, login, refresh, logout, me
     - 6 task endpoints: create, list, get, update, delete
   - Token refresh flow (10-step automatic retry)
   - Error handling contract with ApiError class
   - Rate limiting documentation
   - CORS configuration

3. **quickstart.md** (75KB):
   - 8-step setup guide from project creation to production deployment
   - Environment configuration
   - Core infrastructure code examples (types, API client, auth context, middleware)
   - Development workflow
   - Validation checklist (4 user stories, 22 checkpoints)
   - Common issues and solutions (4 issues documented)
   - Production deployment guide

**Key Architectural Decisions**:

1. **DD-001: Next.js App Router with Route Groups**
   - `(auth)` group for unauthenticated pages (login, register)
   - `(dashboard)` group for authenticated pages (tasks)
   - Middleware for route protection at Next.js level

2. **DD-002: Centralized API Client**
   - Single ApiClient class for all backend communication
   - Automatic JWT token injection via Authorization header
   - Automatic token refresh on 401 response
   - Consistent error handling with ApiError class

3. **DD-003: React Context for Auth State**
   - Access tokens stored in memory (React Context) - XSS protection
   - Refresh tokens in httpOnly cookies (backend-managed)
   - AuthProvider wraps entire app
   - useAuth hook for accessing auth state

4. **DD-004: Next.js Middleware for Route Protection**
   - Checks refresh token cookie presence
   - Redirects unauthenticated users to login
   - Redirects authenticated users away from auth pages
   - Runs before page rendering (no flash of content)

5. **DD-005: Jest + Playwright Testing Strategy**
   - Component tests: Jest + React Testing Library
   - E2E tests: Playwright
   - API client tests: Jest with mocked fetch

**Project Structure**:
```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Unauthenticated routes
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/       # Authenticated routes
│   │   ├── layout.tsx     # Auth check + header
│   │   ├── page.tsx       # Task dashboard
│   │   └── tasks/
│   ├── layout.tsx         # Root layout with AuthProvider
│   └── page.tsx           # Landing/redirect
├── components/            # Reusable components
│   ├── auth/             # LoginForm, RegisterForm
│   ├── tasks/            # TaskList, TaskItem, TaskForm
│   ├── ui/               # Button, Input, LoadingSpinner, ErrorMessage
│   └── layout/           # Header, Navigation
├── lib/                  # Utilities
│   ├── api-client.ts     # API client with JWT injection
│   ├── auth.ts           # Auth utilities
│   └── types.ts          # TypeScript definitions
├── contexts/             # React contexts
│   └── AuthContext.tsx   # Auth state provider
└── middleware.ts         # Route protection
```

**Constitution Check Results**:
- Pre-design: 6/6 principles PASS, 5/5 technology requirements PASS
- Post-design: 6/6 principles PASS - design approved for task generation

**ADR Recommendations**:
Three significant architectural decisions identified for documentation:
1. ADR-001: Next.js App Router Architecture for Authentication
2. ADR-002: JWT Token Management and Storage Strategy
3. ADR-003: Centralized API Client with Automatic Token Management

**Agent Context Update**:
Updated CLAUDE.md with new technology stack:
- Language: TypeScript 5.x with Next.js 16+ (App Router), React 18+
- Framework: Next.js 16+, React 18+, TypeScript, custom API client (fetch-based)
- Database: N/A (frontend only - backend handles persistence)

## Outcome

- ✅ Impact: Complete architectural plan for Next.js frontend with 5 design artifacts. All technology decisions resolved. Clear implementation path defined with 5 major design decisions. Ready for task generation.
- 🧪 Tests: Constitution Check PASS (6/6 principles pre-design, 6/6 post-design). Technology Stack Compliance PASS (5/5 requirements). All NEEDS CLARIFICATION items resolved.
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, contracts/frontend-api-client.md, quickstart.md), 1 file updated (CLAUDE.md)
- 🔁 Next prompts: Run /sp.tasks to generate implementation tasks, optionally run /sp.adr to document 3 significant architectural decisions
- 🧠 Reflection: Planning phase complete with comprehensive design artifacts. All 11 API endpoints documented with clear contracts. Testing strategy defined (Jest + Playwright). Project structure designed with route groups for auth state separation. API client handles automatic token refresh. Ready for task breakdown.

## Evaluation notes (flywheel)

- Failure modes observed: None - all phases completed successfully
- Graders run and results (PASS/FAIL): Constitution Check (pre-design) PASS 6/6, Technology Stack Compliance PASS 5/5, Constitution Check (post-design) PASS 6/6
- Prompt variant (if applicable): User provided detailed architectural requirements via /sp.plan command
- Next experiment (smallest change to try): Proceed to /sp.tasks to generate implementation tasks organized by user story priority (P1-P4)
