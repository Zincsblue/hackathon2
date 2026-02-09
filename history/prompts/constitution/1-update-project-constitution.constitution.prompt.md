---
id: 1
title: Update-project-constitution
stage: constitution
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-fullstack-webapp
branch: master
user: Claude Code
command: sp.constitution
labels: [constitution, spec-driven, todo-app]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

Project: Todo Full-Stack Web Application (Hackathon Phase-2)

Core Principles
- Spec-driven development: All implementation must strictly follow approved specifications.
- Agentic workflow compliance: Enforce the flow spec → plan → tasks → implementation with no skipped steps.
- Security-first design: Authentication, authorization, and user isolation are mandatory defaults.
- Deterministic behavior: APIs and UI must behave consistently across users, sessions, and environments.
- Full-stack coherence: Frontend, backend, and database must integrate without mismatches or assumptions.

Key Standards
- No implementation is allowed without an approved specification and plan.
- All API behavior must be explicitly defined in specs before implementation.
- Authentication must be implemented using Better Auth with JWT tokens.
- All backend routes must validate JWTs and enforce task ownership.
- All database queries must be user-scoped.
- REST APIs must follow proper HTTP semantics and status codes.
- Errors must Constraints
- No manual coding: All code must be generated via Claude Code.
- Fixed technology stack:
  - Frontend: Next.js 16+ (App Router)
  - Backend: Python FastAPI
  - ORM: SQLModel
  - Database: Neon Serverless PostgreSQL
  - Authentication: Better Auth (JWT-based)
- All endpoints require a valid JWT after authentication.
- Backend authentication must be stateless (JWT only).
- Multi-user support is mandatory.
- Data persistence across sessions is required.Success Criteria
- All three specs (Backend, Authentication, Frontend) are fully implemented and integrated.
- Users can sign up, sign in, and manage only their own tasks.
- Unauthorized requests consistently return HTTP 401.
- Task ownership is enforced on every CRUD operation.
- The application works end-to-end as a full-stack system.
- Specs, plans, tasks, and iterations are reviewable and traceable.
- Project passes hackathon evaluation based on process correctness and implementation accuracy.

Assigned Agents
- Auth Agent (auth-integration.md):
  Owns Better Auth configuration, signup/signin flows, JWT issuance, and authentication requirements.

- Backend Agent (fastapi-backend.md):
  Owns FastAPI application structure, REST API endpoints, middleware, and request/response behavior.

- Frontend Agent (frontend-nextjs-app-router.md):
  Owns the Next.js 16+ App Router frontend, authentication UI, API client logic, and responsive design.

- DB Agent (neon-db-ops.md):
  Owns Neon Serverless PostgreSQL setup,

## Response snapshot

Created an updated constitution file for the Todo Full-Stack Web Application project based on the requirements. The new constitution includes six core principles:
1. Spec-driven Development
2. Agentic Workflow Compliance
3. Security-first Design
4. Deterministic Behavior
5. Full-stack Coherence
6. No Manual Coding Constraint

Also included sections for technology stack requirements, development workflow, success criteria, and governance. The constitution supersedes all other practices for the project and requires adherence to the specified principles.

## Outcome

- ✅ Impact: Created project constitution that defines development principles and constraints
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: Continue with spec, plan, and task creation following the constitution
- 🧠 Reflection: The constitution establishes a strong foundation for spec-driven development with clear constraints

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): Standard constitution creation
- Next experiment (smallest change to try): Proceed with spec creation following the constitution