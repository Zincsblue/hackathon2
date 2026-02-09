# Tasks: Frontend & Integration

**Input**: Design documents from `/specs/003-frontend-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/frontend-api-client.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/` at repository root
- **Backend**: `backend/` (existing, no changes)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Next.js project and configure development environment

- [X] T001 Create Next.js 16+ project with TypeScript and App Router in frontend/ directory
- [X] T002 Install dependencies: Next.js 16+, React 18+, TypeScript 5.x
- [X] T003 [P] Create .env.example with NEXT_PUBLIC_API_BASE_URL template in frontend/.env.example
- [X] T004 [P] Create .env.local with backend API URL (http://localhost:8001/api/v1) in frontend/.env.local
- [X] T005 [P] Configure TypeScript with strict mode in frontend/tsconfig.json
- [X] T006 [P] Configure Next.js for API base URL in frontend/next.config.js
- [X] T007 [P] Add .env.local to .gitignore in frontend/.gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 [P] Create TypeScript type definitions in frontend/lib/types.ts (User, Task, TokenResponse, TasksResponse, ErrorResponse, LoginFormData, RegisterFormData, TaskFormData)
- [X] T009 Create API client class with automatic JWT injection and token refresh in frontend/lib/api-client.ts
- [X] T010 Create AuthContext provider with user state and auth methods in frontend/contexts/AuthContext.tsx
- [X] T011 Create Next.js middleware for route protection in frontend/middleware.ts
- [X] T012 Create root layout with AuthProvider wrapper in frontend/app/layout.tsx
- [X] T013 [P] Create global styles with responsive base styles in frontend/app/globals.css

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication Flow (Priority: P1) 🎯 MVP

**Goal**: Users can sign up, log in, and log out through web interface with JWT authentication

**Independent Test**: Complete sign-up → login → logout flow through web interface. Verify tokens obtained, stored, and cleared correctly. Verify unauthenticated users redirected to login.

### Implementation for User Story 1

- [X] T014 [P] [US1] Create auth route group directory structure in frontend/app/(auth)/
- [X] T015 [P] [US1] Create LoginForm component with email/password fields and validation in frontend/components/auth/LoginForm.tsx
- [X] T016 [P] [US1] Create RegisterForm component with email/password/name fields and validation in frontend/components/auth/RegisterForm.tsx
- [X] T017 [US1] Create login page using LoginForm component in frontend/app/(auth)/login/page.tsx
- [X] T018 [US1] Create register page using RegisterForm component in frontend/app/(auth)/register/page.tsx
- [X] T019 [US1] Create root landing page with redirect logic (authenticated → dashboard, unauthenticated → login) in frontend/app/page.tsx
- [X] T020 [US1] Implement login method in AuthContext calling POST /auth/login in frontend/contexts/AuthContext.tsx
- [X] T021 [US1] Implement register method in AuthContext calling POST /auth/register in frontend/contexts/AuthContext.tsx
- [X] T022 [US1] Implement logout method in AuthContext calling POST /auth/logout in frontend/contexts/AuthContext.tsx
- [X] T023 [US1] Add error handling and display in LoginForm for invalid credentials in frontend/components/auth/LoginForm.tsx
- [X] T024 [US1] Add error handling and display in RegisterForm for duplicate email in frontend/components/auth/RegisterForm.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, login, and logout

---

## Phase 4: User Story 2 - Task Management Interface (Priority: P2)

**Goal**: Authenticated users can view, create, update, delete, and complete tasks through web interface

**Independent Test**: Login → view task list → create task → edit task → toggle completion → delete task. Verify all CRUD operations work and only user's tasks are displayed.

### Implementation for User Story 2

- [X] T025 [P] [US2] Create dashboard route group directory structure in frontend/app/(dashboard)/
- [X] T026 [P] [US2] Create TaskList component to display array of tasks in frontend/components/tasks/TaskList.tsx
- [X] T027 [P] [US2] Create TaskItem component for individual task display with edit/delete/toggle buttons in frontend/components/tasks/TaskItem.tsx
- [X] T028 [P] [US2] Create TaskForm component for create/edit with title and description fields in frontend/components/tasks/TaskForm.tsx
- [X] T029 [P] [US2] Create TaskEmpty component for empty state with "create first task" message in frontend/components/tasks/TaskEmpty.tsx
- [X] T030 [US2] Create dashboard layout with Header component in frontend/app/(dashboard)/layout.tsx
- [X] T031 [US2] Create dashboard page that fetches and displays task list using TaskList component in frontend/app/(dashboard)/page.tsx
- [X] T032 [US2] Create new task page with TaskForm for creating tasks in frontend/app/(dashboard)/tasks/new/page.tsx
- [X] T033 [US2] Create task detail/edit page with TaskForm for editing tasks in frontend/app/(dashboard)/tasks/[id]/page.tsx
- [X] T034 [US2] Implement task list fetching (GET /tasks) in dashboard page in frontend/app/(dashboard)/page.tsx
- [X] T035 [US2] Implement task creation (POST /tasks) in TaskForm component in frontend/components/tasks/TaskForm.tsx
- [X] T036 [US2] Implement task update (PATCH /tasks/{id}) in TaskForm component in frontend/components/tasks/TaskForm.tsx
- [X] T037 [US2] Implement task deletion (DELETE /tasks/{id}) in TaskItem component in frontend/components/tasks/TaskItem.tsx
- [X] T038 [US2] Implement task completion toggle (PATCH /tasks/{id}) in TaskItem component in frontend/components/tasks/TaskItem.tsx
- [X] T039 [US2] Add optimistic UI updates for task operations in TaskList component in frontend/components/tasks/TaskList.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full authentication and task management

---

## Phase 5: User Story 3 - Responsive User Experience (Priority: P3)

**Goal**: Application provides consistent, usable experience across desktop (1920px), tablet (768px), and mobile (320px) devices

**Independent Test**: Access application on different viewport sizes (320px, 768px, 1920px). Verify layout adapts appropriately, touch targets are sized correctly, and no horizontal scrolling occurs.

### Implementation for User Story 3

- [X] T040 [P] [US3] Add responsive breakpoints and mobile-first styles to globals.css in frontend/app/globals.css
- [X] T041 [P] [US3] Make LoginForm responsive with mobile-friendly input sizing in frontend/components/auth/LoginForm.tsx
- [X] T042 [P] [US3] Make RegisterForm responsive with mobile-friendly input sizing in frontend/components/auth/RegisterForm.tsx
- [X] T043 [US3] Make TaskList responsive with stacked layout on mobile in frontend/components/tasks/TaskList.tsx
- [X] T044 [US3] Make TaskItem responsive with touch-friendly buttons (44x44px minimum) in frontend/components/tasks/TaskItem.tsx
- [X] T045 [US3] Make TaskForm responsive with full-width inputs on mobile in frontend/components/tasks/TaskForm.tsx
- [X] T046 [US3] Make dashboard layout responsive with collapsible navigation on mobile in frontend/app/(dashboard)/layout.tsx
- [X] T047 [US3] Add viewport meta tag for mobile rendering in root layout in frontend/app/layout.tsx

**Checkpoint**: All user stories should now work across all viewport sizes - desktop, tablet, and mobile

---

## Phase 6: User Story 4 - Error and Loading State Handling (Priority: P4)

**Goal**: Application provides clear feedback during loading operations and when errors occur

**Independent Test**: Trigger loading states (slow network), error states (invalid input, network failure), and empty states (no tasks). Verify appropriate feedback is shown and users can recover from failures.

### Implementation for User Story 4

- [X] T048 [P] [US4] Create LoadingSpinner component with animation in frontend/components/ui/LoadingSpinner.tsx
- [X] T049 [P] [US4] Create ErrorMessage component with retry button in frontend/components/ui/ErrorMessage.tsx
- [X] T050 [US4] Add loading state to LoginForm during authentication in frontend/components/auth/LoginForm.tsx
- [X] T051 [US4] Add loading state to RegisterForm during registration in frontend/components/auth/RegisterForm.tsx
- [X] T052 [US4] Add loading state to TaskList during fetch in frontend/components/tasks/TaskList.tsx
- [X] T053 [US4] Add loading state to TaskForm during create/update in frontend/components/tasks/TaskForm.tsx
- [X] T054 [US4] Add error handling with ErrorMessage in TaskList for fetch failures in frontend/components/tasks/TaskList.tsx
- [X] T055 [US4] Add error handling with ErrorMessage in TaskForm for create/update failures in frontend/components/tasks/TaskForm.tsx
- [X] T056 [US4] Add field-level validation errors in LoginForm in frontend/components/auth/LoginForm.tsx
- [X] T057 [US4] Add field-level validation errors in RegisterForm in frontend/components/auth/RegisterForm.tsx
- [X] T058 [US4] Add field-level validation errors in TaskForm in frontend/components/tasks/TaskForm.tsx
- [X] T059 [US4] Display TaskEmpty component when task list is empty in frontend/components/tasks/TaskList.tsx
- [X] T060 [US4] Add session expiration handling with redirect to login in API client in frontend/lib/api-client.ts
- [X] T061 [US4] Disable submit buttons during loading to prevent duplicate requests in all forms

**Checkpoint**: All error and loading states are handled gracefully across the application

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Reusable UI components and final improvements that affect multiple user stories

- [X] T062 [P] Create reusable Button component with variants (primary, secondary, danger) in frontend/components/ui/Button.tsx
- [X] T063 [P] Create reusable Input component with label and error display in frontend/components/ui/Input.tsx
- [X] T064 [P] Create Header component with user name and logout button in frontend/components/layout/Header.tsx
- [X] T065 [P] Create Navigation component with dashboard links in frontend/components/layout/Navigation.tsx
- [X] T066 Refactor all forms to use reusable Button and Input components
- [X] T067 Add Header component to dashboard layout in frontend/app/(dashboard)/layout.tsx
- [X] T068 [P] Add consistent spacing and typography to global styles in frontend/app/globals.css
- [X] T069 [P] Add focus styles for keyboard navigation accessibility in frontend/app/globals.css
- [X] T070 Verify all functional requirements (FR-001 through FR-022) are implemented
- [X] T071 Run quickstart.md validation: complete sign-up → login → create task → edit task → delete task → logout flow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - No dependencies on other stories (independent)
  - User Story 3 (P3): Can start after Foundational - Enhances US1 and US2 but doesn't block them
  - User Story 4 (P4): Can start after Foundational - Enhances all stories but doesn't block them
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 but typically done after
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US1 and US2 layouts
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Enhances all stories with better UX

### Within Each User Story

- Components before pages (pages use components)
- API integration after component structure
- Error handling after core functionality
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T007)
- All Foundational tasks marked [P] can run in parallel (T008, T013)
- Within User Story 1: T014-T016 can run in parallel (different files)
- Within User Story 2: T025-T029 can run in parallel (different component files)
- Within User Story 3: T040-T042 can run in parallel (different files)
- Within User Story 4: T048-T049 can run in parallel (different component files)
- All Polish tasks marked [P] can run in parallel (T062-T065, T068-T069)
- Once Foundational phase completes, User Story 1 and User Story 2 can start in parallel (if team capacity allows)

---

## Parallel Example: Foundational Phase

```bash
# After Setup (Phase 1), launch foundational tasks together:
Task: "Create TypeScript type definitions in frontend/lib/types.ts"
Task: "Create global styles with responsive base styles in frontend/app/globals.css"
```

---

## Parallel Example: User Story 1

```bash
# Launch component creation tasks together:
Task: "Create auth route group directory structure in frontend/app/(auth)/"
Task: "Create LoginForm component in frontend/components/auth/LoginForm.tsx"
Task: "Create RegisterForm component in frontend/components/auth/RegisterForm.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch all component creation tasks together:
Task: "Create dashboard route group directory structure in frontend/app/(dashboard)/"
Task: "Create TaskList component in frontend/components/tasks/TaskList.tsx"
Task: "Create TaskItem component in frontend/components/tasks/TaskItem.tsx"
Task: "Create TaskForm component in frontend/components/tasks/TaskForm.tsx"
Task: "Create TaskEmpty component in frontend/components/tasks/TaskEmpty.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T013) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T014-T024)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - users can now register and login!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - authentication works!)
3. Add User Story 2 → Test independently → Deploy/Demo (task management works!)
4. Add User Story 3 → Test independently → Deploy/Demo (responsive on all devices!)
5. Add User Story 4 → Test independently → Deploy/Demo (polished UX with error handling!)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (Task Management) - can work in parallel with US1
3. After US1 and US2 complete:
   - Developer A: User Story 3 (Responsive UX)
   - Developer B: User Story 4 (Error Handling)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No test tasks included (not requested in specification)
- Backend is complete and running - no backend changes needed
- All API endpoints are documented in contracts/frontend-api-client.md

---

## Task Summary

- **Total Tasks**: 71
- **Setup Phase**: 7 tasks
- **Foundational Phase**: 6 tasks (BLOCKING)
- **User Story 1 (Authentication)**: 11 tasks
- **User Story 2 (Task Management)**: 15 tasks
- **User Story 3 (Responsive UX)**: 8 tasks
- **User Story 4 (Error Handling)**: 14 tasks
- **Polish Phase**: 10 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-3 (24 tasks) delivers user authentication with JWT

**Independent Test Criteria**:
- US1: Register new user → verify account created → login → verify tokens → logout → verify redirect
- US2: Login → create task → verify appears in list → edit task → verify changes → delete task → verify removed
- US3: Access on mobile (320px) → verify layout adapts → access on desktop (1920px) → verify layout adapts
- US4: Trigger loading state → verify spinner shows → trigger error → verify error message → verify retry works
