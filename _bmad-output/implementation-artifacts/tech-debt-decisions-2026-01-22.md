# Technical Debt Decisions

**Date:** 2026-01-22
**Branch:** chore/security-and-quality-fixes

---

## Context

Following a comprehensive code/architecture audit that identified 17 issues (3 HIGH, 9 MEDIUM, 5 LOW), we evaluated which fixes to prioritize given the planned technology stack:

- **Auth0** for authentication (replacing current JWT implementation)
- **Google/GitHub Sign-In** for social login
- **Oracle Cloud** for deployment (changed from AWS Lightsail on 2026-01-27; see [ADR](./adr-2026-01-27-oracle-cloud.md))

---

## Decision: Skip Auth-Related Fixes

The following issues will **NOT** be fixed now because Auth0 will replace the current authentication system:

| Issue | Severity | Reason to Skip |
|-------|----------|----------------|
| JWT tokens in localStorage | HIGH | Auth0 SDK manages token storage securely |
| Refresh token validation | HIGH | Auth0 handles token lifecycle |
| In-memory rate limiting | MEDIUM | Auth0 has built-in rate limiting |
| Password complexity | MEDIUM | Auth0 password policies |
| Duplicate token utils | MEDIUM | Code will be replaced entirely |
| Silent auth errors | MEDIUM | Auth0 SDK handles auth state |

**Rationale:** Investing effort in httpOnly cookie migration or token validation improvements would be wasted work since the entire auth implementation will be replaced by Auth0 integration.

---

## Decision: Defer AWS/Infrastructure Fixes

| Issue | Severity | Reason to Defer |
|-------|----------|-----------------|
| HTTPS/HSTS enforcement | HIGH | Requires AWS Lightsail configuration; not deploying yet |
| CORS tightening | MEDIUM | Will configure properly when adding Auth0 domains |

**Rationale:** Infrastructure security will be configured during deployment phase when AWS Lightsail is set up.

---

## Decision: Defer Low-Priority Fixes

| Issue | Severity | Reason to Defer |
|-------|----------|-----------------|
| React Context for user state | MEDIUM | Design around Auth0 user object when integrating |
| API response consistency | MEDIUM | Current approach works; nice-to-have |
| Pagination for project list | LOW | No users yet; won't hit limits |
| Transaction management | MEDIUM | Current code works; optimize later |
| FK cascade delete | LOW | Requires migration; batch with other DB changes |

**Rationale:** These improvements can wait until there's more context (Auth0 integration, user scale, etc.).

---

## Decision: Fix Now (High Value, Low Effort)

Three fixes provide immediate value with minimal effort:

### 1. Project Name Max Length Constraint
- **Issue:** No max length on project name allows unbounded input
- **Effort:** ~10 minutes
- **Why Now:** Prevents data issues before more projects are created
- **Implementation:** Add `max_length=100` to schema and model

### 2. Health Check with Database Ping
- **Issue:** `/api/health` returns healthy without verifying DB connectivity
- **Effort:** ~15 minutes
- **Why Now:** Helps debugging during development; catches DB connection issues early
- **Implementation:** Add DB query to health endpoint

### 3. Request/Response Logging Middleware
- **Issue:** No logging for API requests makes debugging difficult
- **Effort:** ~30 minutes
- **Why Now:** Invaluable for debugging as more features are built
- **Implementation:** Add structured logging middleware

---

## Implementation Plan

Using TDD approach:
1. Write failing test
2. Implement fix
3. Verify test passes
4. Commit

**Total Estimated Effort:** ~1 hour

---

## Implementation Status

### Implemented
- Project name max length constraint (`max_length=100` in schema; `String(100)` in model)
- Health check with database ping (DB query in `/api/health`, returns 503 if DB unavailable)
- Request/response logging middleware (JSON payload per request)

### Test Results (2026-01-22)
- Backend tests: passed via `scripts/windows/run-backend-tests.ps1` (log: `logs/backend-tests-20260122-194112.log`)
- Frontend tests: passed via `scripts/windows/run-frontend-tests.ps1` (log: `logs/frontend-tests-20260122-194126.log`)

---

## Audit Reports Reference

- [Test Coverage Audit](./test-coverage-audit-2026-01-22.md)
- [Code/Architecture Audit](./code-architecture-audit-2026-01-22.md)
