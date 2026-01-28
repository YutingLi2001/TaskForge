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

## MVP Completion Summary

| Epic | Status | Stories | FRs Covered |
|------|--------|---------|-------------|
| Epic 1: User Authentication | Done | 4/4 | FR1-FR4 |
| Epic 2: Project Management | Done | 4/4 | FR5-FR9 |
| Epic 3: Task Management | Done | 4/4 | FR10-FR14 |

**Total:** 12 stories, 14 functional requirements - **100% Complete**

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

### Epic 4: CI/CD & DevOps
Automated continuous integration and delivery pipeline ensures code quality and enables confident deployments.
**FRs covered:** FR15, FR16
**Depends on:** MVP Complete
**Priority:** Critical (Foundation for all future work)

### Epic 5: Production Deployment
Application is deployed to Oracle Cloud Infrastructure (OCI) Always Free Tier with proper infrastructure, security, and monitoring.
**FRs covered:** FR17, FR18, FR19, FR20
**Depends on:** Epic 4 (CI/CD)
**Priority:** High (Required to go live)
**Decision:** Changed from AWS Lightsail to Oracle Cloud on 2026-01-27 (see [ADR](../implementation-artifacts/adr-2026-01-27-oracle-cloud.md))

### Epic 6: OAuth Integration
Users can authenticate using third-party OAuth providers (GitHub, Google) in addition to email/password.
**FRs covered:** FR21, FR22, FR23
**Depends on:** Epic 5 (Production deployment for OAuth callbacks)
**Priority:** Medium (User experience enhancement)

### Epic 7: Enhanced Testing
Comprehensive test coverage with pytest, expanded frontend tests, and E2E testing with Playwright.
**FRs covered:** FR24
**Depends on:** Epic 4 (CI integration)
**Priority:** Medium (Quality assurance)

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

## Epic 5: Production Deployment

Application is deployed to Oracle Cloud Infrastructure (OCI) Always Free Tier with proper infrastructure, security, and monitoring.

> **Architecture Decision (2026-01-27):** Changed from AWS Lightsail to Oracle Cloud.
> See [ADR-2026-01-27-Oracle-Cloud](../implementation-artifacts/adr-2026-01-27-oracle-cloud.md) for rationale.

### Story 5.1: Oracle Cloud Setup

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

### Story 5.2: Database Migrations (Alembic)

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

### Story 5.3: SSL/HTTPS Configuration

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

### Story 5.4: Monitoring & Logging

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

## Epic 6: OAuth Integration

Users can authenticate using third-party OAuth providers in addition to email/password.

### Story 6.1: GitHub OAuth

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

### Story 6.2: Google OAuth

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

### Story 6.3: Account Linking

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

### Phase 1: Foundation (Week 1)
1. **Story 4.1: GitHub Actions CI** - Critical foundation
2. **Story 4.2: Test Coverage Reporting** - Visibility

### Phase 2: Production Ready (Week 2-3)
3. **Story 4.3: Production Docker** - Deployment prep
4. **Story 5.1: Oracle Cloud Setup** - Go live (free tier)
5. **Story 5.2: Database Migrations** - Schema management
6. **Story 5.3: SSL/HTTPS** - Security

### Phase 3: Quality & Monitoring (Week 3-4)
7. **Story 5.4: Monitoring & Logging** - Observability
8. **Story 7.1: Pytest Migration** - Better tooling
9. **Story 7.2: Frontend Test Expansion** - Coverage

### Phase 4: OAuth & E2E (Week 5-6)
10. **Story 6.1: GitHub OAuth** - Developer-friendly auth
11. **Story 6.2: Google OAuth** - Broad reach
12. **Story 6.3: Account Linking** - UX polish
13. **Story 7.3: E2E Playwright** - Integration validation

---

## Dependencies Graph

```
MVP Complete (Epics 1-3)
    │
    ├── Epic 4: CI/CD & DevOps
    │       │
    │       ├── 4.1 GitHub Actions CI ─────┐
    │       │                              │
    │       ├── 4.2 Test Coverage ─────────┤
    │       │                              │
    │       └── 4.3 Production Docker ─────┼── Epic 5: Production Deployment
    │                                      │       │
    │                                      │       ├── 5.1 Oracle Cloud Setup
    │                                      │       ├── 5.2 Database Migrations
    │                                      │       ├── 5.3 SSL/HTTPS
    │                                      │       └── 5.4 Monitoring
    │                                      │              │
    │                                      │              └── Epic 6: OAuth
    │                                      │                      │
    │                                      │                      ├── 6.1 GitHub OAuth
    │                                      │                      ├── 6.2 Google OAuth
    │                                      │                      └── 6.3 Account Linking
    │                                      │
    └── Epic 7: Enhanced Testing ──────────┘
            │
            ├── 7.1 Pytest Migration
            ├── 7.2 Frontend Test Expansion
            └── 7.3 E2E Playwright
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
