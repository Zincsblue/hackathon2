# Implementation Plan: Frontend & Integration

**Branch**: `003-frontend-integration` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-frontend-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Next.js 16+ App Router frontend that provides authenticated user access to the todo application. Users can sign up, sign in, and manage their personal tasks through a responsive web interface. The frontend communicates with the existing FastAPI backend (Spec-1 and Spec-2) using JWT authentication, attaching access tokens to all API requests and handling token refresh automatically. The system enforces user data isolation, ensuring users only see and manage their own tasks.

**Technical Approach**: Implement using Next.js App Router with React Server Components for initial page loads and Client Components for interactive features. Create an API client layer that automatically injects JWT tokens into request headers and handles token refresh when access tokens expire. Use middleware for route protection to redirect unauthenticated users to login. Store access tokens in React context (memory) and rely on httpOnly cookies for refresh tokens.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+ (App Router), React 18+
**Primary Dependencies**: Next.js 16+, React 18+, TypeScript, custom API client (fetch-based)
**Storage**: N/A (frontend only - backend handles data persistence via Neon PostgreSQL)
**Testing**: Jest + React Testing Library for component/unit tests, Playwright for E2E tests
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge) - desktop and mobile viewports (320px-1920px)
**Project Type**: Web (frontend)
**Performance Goals**: Login under 10 seconds, task operations under 2 seconds, page loads under 500ms, loading indicators for operations >500ms
**Constraints**: Must use Next.js App Router (not Pages Router), must integrate with existing backend without modifications, custom JWT implementation (not Better Auth library), no manual coding (all via Claude Code), responsive design required (320px-1920px)
**Scale/Scope**: Multi-user todo application with ~10 pages/components (login, register, dashboard, task list, task forms), 11 API endpoints integration, 4 user stories (authentication, task management, responsive UX, error handling)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| **Spec-driven Development** | ✅ PASS | Spec-3 fully defined with 22 functional requirements before implementation |
| **Agentic Workflow Compliance** | ✅ PASS | Following spec → plan → tasks → implementation workflow |
| **Security-first Design** | ✅ PASS | JWT authentication mandatory, token validation on all API calls, user data isolation enforced |
| **Deterministic Behavior** | ✅ PASS | Consistent API responses, predictable state management, standardized error handling |
| **Full-stack Coherence** | ✅ PASS | Frontend integrates with existing backend (Spec-1 + Spec-2) via defined API contracts |
| **No Manual Coding Constraint** | ✅ PASS | All code generated via Claude Code and Spec-Kit Plus |

### Technology Stack Compliance

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Frontend: Next.js 16+ (App Router) | ✅ PASS | Using Next.js 16+ with App Router as specified |
| Backend: Python FastAPI | ✅ PASS | Integrating with existing FastAPI backend (no changes) |
| ORM: SQLModel | ✅ PASS | Backend already uses SQLModel (no frontend changes needed) |
| Database: Neon Serverless PostgreSQL | ✅ PASS | Backend already connected to Neon (no frontend changes needed) |
| Authentication: JWT-based | ✅ PASS | Custom JWT implementation (access + refresh tokens) |

### Gate Result: ✅ **APPROVED TO PROCEED**

No constitutional violations detected. All principles and technology stack requirements are satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/003-frontend-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── frontend-api-client.md
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/                          # Next.js App Router directory
│   ├── (auth)/                   # Auth route group (unauthenticated)
│   │   ├── login/
│   │   │   └── page.tsx          # Login page
│   │   └── register/
│   │       └── page.tsx          # Registration page
│   ├── (dashboard)/              # Dashboard route group (authenticated)
│   │   ├── layout.tsx            # Dashboard layout with auth check
│   │   ├── page.tsx              # Task dashboard (main page)
│   │   └── tasks/
│   │       ├── [id]/
│   │       │   └── page.tsx      # Task detail/edit page
│   │       └── new/
│   │           └── page.tsx      # New task page
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Landing/redirect page
│   └── globals.css               # Global styles
├── components/                   # Reusable UI components
│   ├── auth/
│   │   ├── LoginForm.tsx         # Login form (Client Component)
│   │   └── RegisterForm.tsx      # Registration form (Client Component)
│   ├── tasks/
│   │   ├── TaskList.tsx          # Task list display
│   │   ├── TaskItem.tsx          # Individual task item
│   │   ├── TaskForm.tsx          # Task create/edit form (Client Component)
│   │   └── TaskEmpty.tsx         # Empty state component
│   ├── ui/
│   │   ├── Button.tsx            # Reusable button component
│   │   ├── Input.tsx             # Reusable input component
│   │   ├── LoadingSpinner.tsx    # Loading indicator
│   │   └── ErrorMessage.tsx      # Error display component
│   └── layout/
│       ├── Header.tsx            # App header with logout
│       └── Navigation.tsx        # Navigation component
├── lib/                          # Utility libraries
│   ├── api-client.ts             # API client with JWT injection
│   ├── auth.ts                   # Auth utilities (token management)
│   └── types.ts                  # TypeScript type definitions
├── contexts/                     # React contexts
│   └── AuthContext.tsx           # Auth context provider (Client Component)
├── middleware.ts                 # Next.js middleware for route protection
├── .env.local                    # Environment variables (not committed)
├── .env.example                  # Environment variables template
├── next.config.js                # Next.js configuration
├── tsconfig.json                 # TypeScript configuration
└── package.json                  # Dependencies

backend/                          # Existing backend (no changes)
├── src/
│   ├── models/                   # SQLModel models (User, Task, RefreshToken)
│   ├── services/                 # Business logic (auth, tasks, tokens)
│   ├── api/                      # FastAPI routes
│   └── middleware/               # Rate limiting, security headers
└── tests/                        # Backend tests (already complete)
```

**Structure Decision**: Using Next.js 16+ App Router structure with route groups for authentication state separation. The `(auth)` group contains unauthenticated pages (login, register), while `(dashboard)` group contains authenticated pages with layout-level auth checks. Components are organized by feature (auth, tasks, ui, layout). The API client layer (`lib/api-client.ts`) centralizes all backend communication with automatic JWT token injection. Auth state is managed via React Context (`contexts/AuthContext.tsx`) to provide authentication status and user data throughout the app. Middleware (`middleware.ts`) handles route protection at the Next.js level, redirecting unauthenticated users before page rendering.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations detected. This section is not applicable.

---

## Phase 0: Research & Technology Decisions

### Research Tasks

**RT-001: Frontend Testing Strategy**
- **Question**: What testing approach should be used for Next.js App Router with TypeScript?
- **Research Focus**: Testing frameworks for React Server Components, Client Components, and E2E flows
- **Decision Required**: Testing tools and strategy

### Research Findings

#### RT-001: Frontend Testing Strategy

**Decision**: Use Jest + React Testing Library for component/unit tests, Playwright for E2E tests

**Rationale**:
- **Jest + React Testing Library**: Industry standard for React component testing, excellent TypeScript support, works with Next.js App Router, can test both Server and Client Components
- **Playwright**: Official recommendation for Next.js E2E testing, supports multiple browsers, handles authentication flows well, can test responsive behavior across viewports
- **No Cypress**: While popular, Playwright has better Next.js integration and is recommended in Next.js docs

**Testing Strategy**:
1. **Component Tests** (Jest + React Testing Library):
   - Test individual components in isolation
   - Mock API calls and auth context
   - Verify rendering, user interactions, form validation
   - Test loading states, error states, empty states

2. **E2E Tests** (Playwright):
   - Test complete user flows (sign up → login → create task → logout)
   - Verify authentication redirects
   - Test task CRUD operations with real API calls
   - Validate responsive behavior on different viewports
   - Confirm user data isolation (multiple user accounts)

3. **API Client Tests** (Jest):
   - Test JWT token injection
   - Test token refresh logic
   - Test error handling and retry logic

**Alternatives Considered**:
- **Vitest**: Faster than Jest but less mature ecosystem for Next.js
- **Cypress**: Popular but Playwright has better Next.js support
- **Testing Library alone**: Need E2E tool for full flow validation

**Implementation Notes**:
- Configure Jest with `next/jest` for Next.js compatibility
- Use `@testing-library/react` for component tests
- Use `@playwright/test` for E2E tests
- Mock `fetch` calls in component tests
- Use test database or mock backend for E2E tests (or run against local backend)

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

### Artifacts Generated

1. **data-model.md**: Complete data model definitions
   - Frontend data models: User, Task, TokenResponse, TasksResponse, ErrorResponse
   - Form data models: LoginFormData, RegisterFormData, TaskFormData
   - UI state models: AuthState, TaskListState
   - Data flow diagrams for authentication, task CRUD, and token refresh

2. **contracts/frontend-api-client.md**: API client contract
   - ApiClient class interface with automatic JWT injection
   - 11 API endpoint specifications (5 auth + 6 task endpoints)
   - Token refresh flow documentation
   - Error handling contract
   - Rate limiting and CORS configuration

3. **quickstart.md**: Developer quickstart guide
   - Step-by-step setup instructions
   - Environment configuration
   - Core infrastructure code examples
   - Development workflow
   - Validation checklist
   - Common issues and solutions
   - Production deployment guide

### Key Design Decisions

**DD-001: Next.js App Router with Route Groups**
- Decision: Use `(auth)` and `(dashboard)` route groups for authentication state separation
- Rationale: Clear separation of authenticated vs unauthenticated routes, different layouts per group
- Impact: Simplified route protection, better code organization

**DD-002: Centralized API Client with Automatic Token Management**
- Decision: Single ApiClient class handles all backend communication with automatic JWT injection and refresh
- Rationale: DRY principle, consistent error handling, automatic token refresh prevents user disruption
- Impact: Reduced code duplication, improved maintainability, better UX

**DD-003: React Context for Auth State**
- Decision: Use React Context for auth state with memory storage for access tokens
- Rationale: Simple, no external dependencies, more secure than localStorage
- Impact: Auth state available throughout app, XSS protection

**DD-004: Next.js Middleware for Route Protection**
- Decision: Use middleware to check refresh token cookie and redirect before page rendering
- Rationale: Efficient (runs before rendering), no flash of protected content, centralized logic
- Impact: Better security, improved UX, single source of truth for route protection

**DD-005: Jest + Playwright Testing Strategy**
- Decision: Jest + React Testing Library for components, Playwright for E2E
- Rationale: Industry standard, excellent Next.js support, comprehensive coverage
- Impact: High confidence in code quality, automated validation of user flows

### Constitution Check (Post-Design)

*Re-evaluation after Phase 1 design completion*

| Principle | Status | Notes |
|-----------|--------|-------|
| **Spec-driven Development** | ✅ PASS | All design artifacts align with Spec-3 requirements |
| **Agentic Workflow Compliance** | ✅ PASS | Completed spec → plan → research → design workflow |
| **Security-first Design** | ✅ PASS | JWT in memory (not localStorage), httpOnly cookies, middleware protection, automatic token refresh |
| **Deterministic Behavior** | ✅ PASS | Consistent API client behavior, standardized error handling, predictable state transitions |
| **Full-stack Coherence** | ✅ PASS | All 11 API endpoints documented, data models match backend schemas, no backend modifications required |
| **No Manual Coding Constraint** | ✅ PASS | All implementation will be via Claude Code following tasks.md |

**Gate Result**: ✅ **APPROVED - READY FOR TASK GENERATION**

No constitutional violations detected. Design is complete and ready for `/sp.tasks` command.

---

## Phase 2: Task Generation

**Status**: ⏳ Pending

**Next Step**: Run `/sp.tasks` to generate implementation tasks based on this plan.

The tasks will be organized by user story priority:
- **P1**: User Authentication Flow (login, register, logout pages)
- **P2**: Task Management Interface (dashboard, task CRUD)
- **P3**: Responsive User Experience (mobile/desktop layouts)
- **P4**: Error and Loading State Handling (loading spinners, error messages, empty states)

---

## Architectural Decisions Requiring ADR

The following significant architectural decisions were made during planning and should be documented in ADRs:

### ADR-001: Next.js App Router Architecture
**Decision**: Use Next.js 16+ App Router with route groups and middleware for authentication
**Significance**: Affects entire application structure, routing, and authentication flow
**Alternatives**: Pages Router, client-side routing only, layout-based auth checks
**Recommendation**: Document with `/sp.adr "Next.js App Router Architecture for Authentication"`

### ADR-002: JWT Token Management Strategy
**Decision**: Store access tokens in memory (React Context), refresh tokens in httpOnly cookies
**Significance**: Critical security decision affecting XSS vulnerability and session management
**Alternatives**: localStorage for tokens, session-based auth, Better Auth library
**Recommendation**: Document with `/sp.adr "JWT Token Management and Storage Strategy"`

### ADR-003: API Client Architecture
**Decision**: Centralized API client with automatic token injection and refresh handling
**Significance**: Affects all backend communication, error handling, and token refresh flow
**Alternatives**: Direct fetch calls in components, axios library, SWR/React Query
**Recommendation**: Document with `/sp.adr "Centralized API Client with Automatic Token Management"`

---

## Summary

The implementation plan for Frontend & Integration is complete with:

✅ **Phase 0 (Research)**: All technology decisions resolved
✅ **Phase 1 (Design)**: Data models, API contracts, and quickstart guide created
⏳ **Phase 2 (Tasks)**: Ready for task generation via `/sp.tasks`

**Key Deliverables**:
- 5 planning artifacts (plan.md, research.md, data-model.md, contracts/, quickstart.md)
- 5 major architectural decisions documented
- 3 ADR recommendations for significant decisions
- Complete alignment with Spec-3 requirements and constitutional principles

**Ready for**: Task generation (`/sp.tasks`) followed by implementation (`/sp.implement`)
