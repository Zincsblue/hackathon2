<!-- Sync Impact Report:
Version change: 1.0.0 → 1.1.0
Modified principles: All principles were filled with project-specific content
Added sections: Core Principles section with 6 specific principles
Removed sections: None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md - updated for consistency
- ✅ .specify/templates/spec-template.md - updated for consistency
- ✅ .specify/templates/tasks-template.md - updated for consistency
Follow-up TODOs: None
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### Spec-driven Development
All implementation must strictly follow approved specifications. No coding is allowed without a corresponding approved specification and plan in place.

### Agentic Workflow Compliance
Enforce the flow spec → plan → tasks → implementation with no skipped steps. Every development activity must follow the agentic workflow pattern with proper planning and task breakdown.

### Security-first Design
Authentication, authorization, and user isolation are mandatory defaults. All API endpoints must validate JWT tokens and enforce strict task ownership per user, with unauthorized requests returning HTTP 401.

### Deterministic Behavior
APIs and UI must behave consistently across users, sessions, and environments. The system must provide predictable responses and maintain consistent state regardless of user or environmental variations.

### Full-stack Coherence
Frontend, backend, and database must integrate without mismatches or assumptions. All layers must communicate through well-defined contracts with proper error handling and data validation.

### No Manual Coding Constraint
All code must be generated via Claude Code and Spec-Kit Plus tools. Direct manual implementation without proper specification and planning is strictly prohibited.

## Technology Stack Requirements

Fixed technology stack constraints:
- Frontend: Next.js 16+ (App Router)
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (JWT-based)

All endpoints require a valid JWT after authentication. Backend authentication must be stateless (JWT only). Multi-user support is mandatory with data persistence across sessions required.

## Development Workflow

All API behavior must be explicitly defined in specs before implementation. Authentication must be implemented using Better Auth with JWT tokens. All database queries must be user-scoped. REST APIs must follow proper HTTP semantics and status codes.

Implementation follows the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding is allowed.

## Success Criteria

- All three specs (Backend, Authentication, Frontend) are fully implemented and integrated.
- Users can sign up, sign in, and manage only their own tasks.
- Unauthorized requests consistently return HTTP 401.
- Task ownership is enforced on every CRUD operation.
- The application works end-to-end as a full-stack system.
- Specs, plans, tasks, and iterations are reviewable and traceable.
- Project passes hackathon evaluation based on process correctness and implementation accuracy.

## Governance

This constitution supersedes all other practices and development guidelines for this project. All implementation must comply with the specified principles and technology stack. Any deviation from these principles requires formal amendment documentation and approval.

Amendments require: (1) Clear justification for change, (2) Impact assessment on existing codebase, (3) Updated dependent templates and documentation, (4) Approval from project stakeholders.

All pull requests and reviews must verify compliance with constitutional principles. Implementation without proper specification and planning is grounds for immediate rejection.

**Version**: 1.1.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-07