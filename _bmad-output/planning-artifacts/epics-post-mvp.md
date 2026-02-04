---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - "_bmad-output/planning-artifacts/prd.md"
  - "_bmad-output/planning-artifacts/architecture.md"
  - "_bmad-output/planning-artifacts/epics.md"
status: 'complete'
completedAt: '2026-01-24'
mvpCompletedAt: '2026-01-24'
---

# TaskForge - Post-MVP Epic Breakdown

## Overview

This document provides the epic and story breakdown for TaskForge post-MVP enhancements. The MVP (Epics 1-3) was completed on 2026-01-24, delivering all 14 core functional requirements.

**Development Strategy (Updated 2026-02-04):** This project is now following a **local-development-first approach**. Stories requiring cloud infrastructure or production deployment have been moved to a separate "Production Track" and are on hold. The focus is on completing all local development and testing capabilities first.

## MVP Completion Summary

| Epic | Status | Stories | FRs Covered |
|------|--------|---------|-------------|
| Epic 1: User Authentication | Done | 4/4 | FR1-FR4 |
| Epic 2: Project Management | Done | 4/4 | FR5-FR9 |
| Epic 3: Task Management | Done | 4/4 | FR10-FR14 |

**Total:** 12 stories, 14 functional requirements - **100% Complete**

## Post-MVP Progress Summary

### Local Development Track (Active)

| Epic | Status | Stories Completed | FRs Covered |
|------|--------|------------------|-------------|
| Epic 4: CI/CD & DevOps | ✅ Done | 3/3 | FR15, FR16 |
| Epic 5: Database Migrations | ✅ Done | 1/1 | FR18 |
| Epic 6: OAuth Integration | 📋 Ready | 0/3 | FR21, FR22, FR23 |
| Epic 7: Enhanced Testing | 🔄 In Progress | 0/3 | FR24 |

**Progress:** 4/10 stories complete (40%)
**Note:** OAuth can be developed locally using localhost callback URLs

### Production/Cloud Track (On Hold)

| Epic | Status | Stories | FRs Covered |
|------|--------|---------|-------------|
| Epic 5: Production Infrastructure | 📦 On Hold | 0/3 | FR17, FR19, FR20 |

**Status:** 3 stories on hold until cloud deployment is prioritized

---

## Post-MVP Requirements Inventory

### New Functional Requirements

- FR15: Automated CI/CD pipeline validates all code changes
- FR16: Test coverage is tracked and reported
- FR17: Application is deployed to production environment
- FR18: Database schema changes are managed via migrations
- FR19: Application uses HTTPS in production
- FR20: Application health and errors are monitored
- FR21: User can authenticate via GitHub OAuth
- FR22: User can authenticate via Google OAuth
- FR23: OAuth accounts can be linked to existing email accounts
- FR24: Comprehensive E2E tests validate user flows

### New Non-Functional Requirements

- NFR10: CI pipeline runs in < 5 minutes
- NFR11: Test coverage > 80% for backend, > 70% for frontend
- NFR12: Zero-downtime deployments
- NFR13: < 1 minute to rollback deployment
- NFR14: OAuth login completes in < 3 seconds

### FR Coverage Map (Post-MVP)

| FR | Epic | Description |
|----|------|-------------|
| FR15 | Epic 4 | Automated CI/CD pipeline validates all code changes |
| FR16 | Epic 4 | Test coverage is tracked and reported |
| FR17 | Epic 5 | Application is deployed to production environment |
| FR18 | Epic 5 | Database schema changes are managed via migrations |
| FR19 | Epic 5 | Application uses HTTPS in production |
| FR20 | Epic 5 | Application health and errors are monitored |
| FR21 | Epic 6 | User can authenticate via GitHub OAuth |
| FR22 | Epic 6 | User can authenticate via Google OAuth |
| FR23 | Epic 6 | OAuth accounts can be linked to existing email accounts |
| FR24 | Epic 7 | Comprehensive E2E tests validate user flows |

---

## Post-MVP Epic List

### Local Development Track (Active)

#### Epic 4: CI/CD & DevOps ✅ COMPLETED
Automated continuous integration and delivery pipeline ensures code quality and enables confident deployments.
**FRs covered:** FR15, FR16
**Status:** Complete (3/3 stories done)
**Completed:** 2026-01-24

#### Epic 5: Database Migrations ✅ COMPLETED
Database schema changes managed via Alembic migrations for versioning and reversibility.
**FRs covered:** FR18
**Status:** Complete (Story 5.2 done)
**Completed:** 2026-02-04
**Note:** Extracted from Production Deployment epic as it's essential for local development

#### Epic 6: OAuth Integration 📋 READY
Users can authenticate using third-party OAuth providers (GitHub, Google) in addition to email/password.
**FRs covered:** FR21, FR22, FR23
**Status:** Ready for implementation (0/3 stories)
**Depends on:** None - can use localhost callback URLs for development
**Priority:** MEDIUM - Can be done alongside or after Epic 7
**Note:** OAuth providers (GitHub, Google) support localhost callbacks for local development

#### Epic 7: Enhanced Testing 🔄 NEXT PRIORITY
Comprehensive test coverage with pytest, expanded frontend tests, and E2E testing with Playwright.
**FRs covered:** FR24
**Status:** In Progress (0/3 stories)
**Depends on:** Epic 4 (CI integration) ✅
**Priority:** HIGH - Next epic to implement

### Production/Cloud Track (On Hold)

#### Epic 5: Production Infrastructure 📦 ON HOLD
Application deployed to Oracle Cloud Infrastructure with proper security and monitoring.
**FRs covered:** FR17, FR19, FR20
**Stories:** 5.1 (Oracle Cloud Setup), 5.3 (SSL/HTTPS), 5.4 (Monitoring)
**Status:** On hold - requires cloud deployment decision
**Decision:** Changed from AWS Lightsail to Oracle Cloud on 2026-01-27 (see [ADR](../implementation-artifacts/adr-2026-01-27-oracle-cloud.md))
**Note:** Story 5.2 (Database Migrations) was moved to Local Development Track and completed

---

## Epic 4: CI/CD & DevOps

Automated continuous integration and delivery pipeline ensures code quality and enables confident deployments.

### Story 4.1: GitHub Actions CI

As a **developer**,
I want **automated tests to run on every pull request**,
So that **code quality is validated before merging**.

**Acceptance Criteria:**

**Given** I push code or open a pull request
**When** GitHub Actions workflow triggers
**Then** backend tests run and report results
**And** frontend tests run and report results
**And** linting checks pass
**And** type checking passes
**And** the workflow completes in < 5 minutes
**And** failed checks block PR merge

*Includes: .github/workflows/ci.yml, cross-platform test scripts*

### Story 4.2: Test Coverage Reporting

As a **developer**,
I want **test coverage to be tracked and visible**,
So that **I can identify untested code**.

**Acceptance Criteria:**

**Given** CI pipeline runs tests
**When** tests complete
**Then** coverage report is generated for backend (pytest-cov)
**And** coverage report is generated for frontend (vitest coverage)
**And** coverage percentage is displayed in PR comments
**And** coverage thresholds are enforced (backend > 80%, frontend > 70%)

*Includes: pytest.ini, vitest.config.ts updates, coverage badges*

### Story 4.3: Production Docker Configuration

As a **developer**,
I want **optimized Docker images for production**,
So that **deployments are fast and secure**.

**Acceptance Criteria:**

**Given** I build Docker images for production
**When** the build completes
**Then** images use multi-stage builds for smaller size
**And** images run as non-root user
**And** health checks are configured
**And** .dockerignore excludes unnecessary files
**And** docker-compose.prod.yml is available for production

---

## Epic 5: Production Deployment & Database Management

> **Reorganization Note (2026-02-04):** This epic has been split into two tracks:
> - **Local Development:** Story 5.2 (Database Migrations) - ✅ COMPLETED
> - **Production/Cloud:** Stories 5.1, 5.3, 5.4 - 📦 ON HOLD
>
> **Architecture Decision (2026-01-27):** Changed from AWS Lightsail to Oracle Cloud.
> See [ADR-2026-01-27-Oracle-Cloud](../implementation-artifacts/adr-2026-01-27-oracle-cloud.md) for rationale.

This epic originally covered production deployment to Oracle Cloud Infrastructure (OCI) Always Free Tier with proper infrastructure, security, and monitoring. Story 5.2 (Database Migrations) was prioritized for local development and has been completed. The remaining production infrastructure stories (5.1, 5.3, 5.4) are on hold pending cloud deployment decision.

### Story 5.1: Oracle Cloud Setup 📦 ON HOLD

**Track:** Production/Cloud
**Status:** On hold - requires cloud deployment decision
**See:** [5-1-oracle-cloud-setup.md](../implementation-artifacts/5-1-oracle-cloud-setup.md) (moved to backlog)

As a **developer**,
I want **the application deployed to Oracle Cloud Infrastructure**,
So that **users can access it on the internet for free**.

**Acceptance Criteria:**

**Given** I have Oracle Cloud account configured
**When** I run the deployment process
**Then** ARM-based VM instance is provisioned (Always Free tier)
**And** Docker and Docker Compose are installed
**And** PostgreSQL runs in container with persistent volume
**And** Frontend and backend containers are deployed
**And** Public IP is accessible
**And** Environment variables are securely configured
**And** Firewall rules allow HTTP/HTTPS traffic

*Includes: OCI setup guide, deployment scripts, ARM Docker images*

### Story 5.2: Database Migrations (Alembic) ✅ COMPLETED

**Track:** Local Development
**Status:** Complete - merged to develop on 2026-02-04
**See:** [5-2-database-migrations.md](../implementation-artifacts/5-2-database-migrations.md)
**PR:** [#26](https://github.com/YutingLi2001/TaskForge/pull/26)

As a **developer**,
I want **database schema changes managed via Alembic migrations**,
So that **schema updates are versioned and reversible**.

**Acceptance Criteria:**

**Given** I modify a SQLAlchemy model
**When** I generate and run a migration
**Then** the database schema is updated
**And** migration history is tracked
**And** migrations can be rolled back
**And** migrations run automatically on deployment

*Includes: alembic.ini, migrations folder, CI integration*

### Story 5.3: SSL/HTTPS Configuration 📦 ON HOLD

**Track:** Production/Cloud
**Status:** On hold - requires production domain and cloud deployment
**Depends on:** Story 5.1 (Oracle Cloud Setup)

As a **user**,
I want **the application served over HTTPS**,
So that **my data is transmitted securely**.

**Acceptance Criteria:**

**Given** I access the application URL
**When** the page loads
**Then** connection uses HTTPS
**And** HTTP requests redirect to HTTPS
**And** SSL certificate is valid and auto-renewed
**And** security headers are properly configured

### Story 5.4: Monitoring & Logging 📦 ON HOLD

**Track:** Production/Cloud
**Status:** On hold - requires production environment
**Depends on:** Story 5.1 (Oracle Cloud Setup)

As a **developer**,
I want **application health and errors monitored**,
So that **I can detect and diagnose issues quickly**.

**Acceptance Criteria:**

**Given** the application is running in production
**When** errors occur or health degrades
**Then** errors are logged with context
**And** health check endpoint returns status
**And** alerts are triggered for critical issues
**And** logs are accessible for debugging

---

## Epic 6: OAuth Integration 📋 READY

**Track:** Local Development
**Status:** Ready for implementation - can use localhost callbacks
**Depends on:** None (independent epic)
**Rationale:** Both GitHub and Google OAuth support localhost callback URLs (e.g., `http://localhost:3000/auth/github/callback`), allowing full local development and testing

Users can authenticate using third-party OAuth providers in addition to email/password.

### Story 6.1: GitHub OAuth 📋 READY

**Track:** Local Development
**Status:** Ready - can use localhost callback (`http://localhost:3000/auth/github/callback`)
**Depends on:** None
**Note:** GitHub OAuth app can be configured with localhost URLs for development

As a **user**,
I want **to log in using my GitHub account**,
So that **I can access the app without creating a new password**.

**Acceptance Criteria:**

**Given** I am on the login page
**When** I click "Login with GitHub"
**Then** I am redirected to GitHub authorization
**And** after authorizing, I am logged in
**And** my GitHub email is used for my account
**And** I receive JWT tokens like email/password login
**And** new users are created automatically
**And** existing users with matching email are logged in

*Includes: GitHub OAuth app setup, /api/auth/github/callback endpoint*

### Story 6.2: Google OAuth 📋 READY

**Track:** Local Development
**Status:** Ready - can use localhost callback (`http://localhost:3000/auth/google/callback`)
**Depends on:** None
**Note:** Google OAuth app can be configured with localhost URLs for development

As a **user**,
I want **to log in using my Google account**,
So that **I can access the app with my existing Google credentials**.

**Acceptance Criteria:**

**Given** I am on the login page
**When** I click "Login with Google"
**Then** I am redirected to Google authorization
**And** after authorizing, I am logged in
**And** my Google email is used for my account
**And** I receive JWT tokens like email/password login
**And** new users are created automatically
**And** existing users with matching email are logged in

*Includes: Google OAuth app setup, /api/auth/google/callback endpoint*

### Story 6.3: Account Linking 📋 READY

**Track:** Local Development
**Status:** Ready - depends on OAuth providers being implemented
**Depends on:** Story 6.1 (GitHub OAuth), Story 6.2 (Google OAuth)
**Note:** Can be fully implemented and tested locally

As a **user**,
I want **my OAuth login linked to my existing account**,
So that **I can access the same projects regardless of login method**.

**Acceptance Criteria:**

**Given** I have an existing email/password account
**When** I log in via OAuth with the same email
**Then** I access my existing account and projects
**And** I can now log in via either method
**And** account linking is shown in user settings
**And** I can unlink OAuth providers from settings

---

## Epic 7: Enhanced Testing

Comprehensive test coverage with modern testing tools and E2E validation.

### Story 7.1: Pytest Migration

As a **developer**,
I want **backend tests using pytest instead of unittest**,
So that **I have better test tooling and fixtures**.

**Acceptance Criteria:**

**Given** I run backend tests
**When** tests execute
**Then** pytest is used as the test runner
**And** pytest-asyncio handles async tests
**And** pytest-cov generates coverage reports
**And** fixtures replace repetitive test setup
**And** all existing tests pass

*Includes: pytest.ini, conftest.py, requirements-dev.txt*

### Story 7.2: Frontend Test Expansion

As a **developer**,
I want **comprehensive frontend test coverage**,
So that **UI components are validated**.

**Acceptance Criteria:**

**Given** I run frontend tests
**When** tests execute
**Then** all pages have test coverage
**And** all components have test coverage
**And** coverage is > 70%
**And** tests validate user interactions
**And** tests mock API calls appropriately

### Story 7.3: E2E Tests with Playwright

As a **developer**,
I want **end-to-end tests validating full user flows**,
So that **I can catch integration issues**.

**Acceptance Criteria:**

**Given** I run E2E tests
**When** tests execute against running application
**Then** user registration flow is tested
**And** user login flow is tested
**And** project CRUD flow is tested
**And** task CRUD flow is tested
**And** tests run in CI pipeline
**And** tests use isolated test database

*Includes: playwright.config.ts, e2e/ test folder*

---

## Recommended Implementation Order

### Local Development Track (Current Focus)

#### Phase 1: Foundation ✅ COMPLETED
1. ✅ **Story 4.1: GitHub Actions CI** - Critical foundation
2. ✅ **Story 4.2: Test Coverage Reporting** - Visibility
3. ✅ **Story 4.3: Production Docker** - Container optimization
4. ✅ **Story 5.2: Database Migrations** - Schema management

#### Phase 2: Enhanced Testing 🔄 CURRENT PHASE
5. **Story 7.1: Pytest Migration** - Better backend testing tooling
6. **Story 7.2: Frontend Test Expansion** - Comprehensive UI coverage
7. **Story 7.3: E2E Playwright** - Full user flow validation

#### Phase 3: OAuth Integration 📋 NEXT UP
8. **Story 6.1: GitHub OAuth** - Developer-friendly auth (localhost callbacks)
9. **Story 6.2: Google OAuth** - Broad reach (localhost callbacks)
10. **Story 6.3: Account Linking** - UX polish

**Rationale:** Complete all local development capabilities before moving to production deployment. OAuth can be fully developed and tested locally using localhost callback URLs. This allows for thorough testing and iteration without cloud costs.

### Production/Cloud Track (On Hold - Future Phases)

#### Phase 4: Production Infrastructure (When Ready to Deploy)
11. **Story 5.1: Oracle Cloud Setup** - Production environment
12. **Story 5.3: SSL/HTTPS** - Security certificates
13. **Story 5.4: Monitoring & Logging** - Observability

**Note:** Phase 4 requires cloud deployment and production domain. On hold until production deployment is prioritized. When moving to production, OAuth callback URLs will need to be updated to production domain.

---

## Dependencies Graph

```
MVP Complete (Epics 1-3)
    │
    ├──────────────────────────────────────────────────────────┐
    │                                                          │
    │ LOCAL DEVELOPMENT TRACK (ACTIVE)                         │ PRODUCTION/CLOUD TRACK (ON HOLD)
    │                                                          │
    ├── Epic 4: CI/CD & DevOps ✅                             │
    │       │                                                  │
    │       ├── 4.1 GitHub Actions CI ✅                       │
    │       ├── 4.2 Test Coverage ✅                           │
    │       └── 4.3 Production Docker ✅                       │
    │                │                                         │
    │                ├─────────────────────┐                   │
    │                │                     │                   │
    │                ▼                     ▼                   ▼
    │                                                          │
    │       Epic 5: Database Migrations ✅         Epic 5: Production Infrastructure 📦
    │               │                                          │
    │               └── 5.2 Alembic ✅                         ├── 5.1 Oracle Cloud Setup 📦
    │                                                          ├── 5.3 SSL/HTTPS 📦
    │       Epic 7: Enhanced Testing 🔄                        └── 5.4 Monitoring 📦
    │               │
    │               ├── 7.1 Pytest Migration
    │               ├── 7.2 Frontend Test Expansion
    │               └── 7.3 E2E Playwright
    │
    │       Epic 6: OAuth Integration 📋
    │               │
    │               ├── 6.1 GitHub OAuth (localhost callbacks)
    │               ├── 6.2 Google OAuth (localhost callbacks)
    │               └── 6.3 Account Linking
    │
    └──────────────────────────────────────────────────────────┘

Legend:
✅ = Completed
🔄 = In Progress / Next Priority
📋 = Ready for Development
📦 = On Hold (requires production deployment)
```

---

## Success Metrics

| Metric | Target | Measured By |
|--------|--------|-------------|
| CI Pipeline Time | < 5 min | GitHub Actions logs |
| Backend Test Coverage | > 80% | pytest-cov report |
| Frontend Test Coverage | > 70% | vitest coverage |
| Deployment Time | < 10 min | Deployment logs |
| Rollback Time | < 1 min | Deployment logs |
| OAuth Login Time | < 3 sec | E2E tests |
| Production Uptime | > 99.5% | Monitoring dashboard |
