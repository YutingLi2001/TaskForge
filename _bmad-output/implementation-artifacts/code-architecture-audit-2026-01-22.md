# Code & Architecture Audit Report

**Date:** 2026-01-22
**Auditor:** Claude Opus 4.5
**Branch:** chore/test-coverage-audit

---

## Executive Summary

Comprehensive audit of the TaskForge codebase identified **17 issues** across security, architecture, and code quality domains. The codebase demonstrates good separation of concerns and solid test coverage, but has several areas requiring attention.

| Severity | Count |
|----------|-------|
| HIGH | 3 |
| MEDIUM | 9 |
| LOW | 5 |

---

## HIGH SEVERITY ISSUES

### 1. JWT Tokens Stored in localStorage (XSS Vulnerability)
**Location:** `frontend/src/api/client.ts:28`, `frontend/src/pages/Login.tsx`, etc.

**Issue:** Access and refresh tokens stored in localStorage are accessible to any JavaScript running on the page, including malicious scripts from XSS attacks.

**Impact:** Token theft allows complete account takeover.

**Recommended Fix:**
- Migrate to httpOnly cookies for token storage
- Backend should set `Set-Cookie` with `httpOnly`, `Secure`, `SameSite=Strict` flags
- Frontend removes all `localStorage.getItem('token')` calls

---

### 2. Refresh Token Validation Insufficient
**Location:** `backend/app/routers/auth.py:125-143`

**Issue:** Refresh token validation only compares hashes in database - no validation that the token itself is well-formed or hasn't been rotated.

**Impact:** Potential for token replay or fabrication attacks.

**Recommended Fix:**
- Add token metadata (issued_at, rotation_count)
- Validate token structure before hash comparison
- Implement proper token rotation with revocation

---

### 3. No HTTPS Enforcement
**Location:** Missing from configuration

**Issue:** No HTTPS redirect middleware or HSTS headers configured.

**Impact:** Credentials and tokens can be intercepted on insecure connections.

**Recommended Fix:**
- Add `TrustedHostMiddleware` in production
- Configure reverse proxy for HTTPS redirect
- Add HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`

---

## MEDIUM SEVERITY ISSUES

### 4. In-Memory Rate Limiting
**Location:** `backend/app/routers/auth.py:32`

**Issue:** Login rate limiting uses module-level dictionary that doesn't persist across restarts, isn't thread-safe, and won't work in multi-process deployments.

**Fix:** Use Redis-based rate limiting or a dedicated library (slowapi).

---

### 5. CORS Configuration Overly Permissive
**Location:** `backend/app/main.py:22-28`

**Issue:** `allow_methods=["*"]` and `allow_headers=["*"]` allow more than necessary.

**Fix:** Whitelist specific methods `["GET", "POST", "PUT", "DELETE"]` and headers `["Content-Type", "Authorization"]`.

---

### 6. Password Complexity Not Enforced
**Location:** `backend/app/schemas/user.py:7`

**Issue:** Only min/max length validated, no complexity requirements (uppercase, digits, special chars).

**Fix:** Add `@field_validator` for password complexity.

---

### 7. Duplicate Token Validation Logic
**Location:** `frontend/src/components/ProtectedRoute.tsx:12-29`, `frontend/src/components/PublicRoute.tsx:11-28`

**Issue:** Nearly identical JWT parsing/validation code in two files.

**Fix:** Extract to `frontend/src/utils/tokenUtils.ts`.

---

### 8. Silent Auth Errors Grant Access
**Location:** `frontend/src/components/ProtectedRoute.tsx:46-55`

**Issue:** Non-auth errors (500, network) result in `setStatus('allowed')` - granting access when server is unavailable.

**Fix:** Stay in `'checking'` state on server errors; add retry logic.

---

### 9. No State Management - Prop Drilling
**Location:** `frontend/src/pages/Dashboard.tsx`, `Projects.tsx`, `ProjectDetail.tsx`

**Issue:** User email fetched from localStorage in multiple components independently.

**Fix:** Create React Context for user state, wrap app with provider.

---

### 10. No Transaction Management
**Location:** `backend/app/routers/auth.py:89-114`

**Issue:** Multiple database operations in login flow without explicit transaction handling.

**Fix:** Wrap critical operations in explicit transactions.

---

### 11. API Response Inconsistency
**Location:** Multiple backend files

**Issue:** Different response structures for success vs error, inconsistent use of status constants.

**Fix:** Standardize all responses with consistent wrapper structure.

---

### 12. No Request/Response Logging
**Location:** Backend - missing

**Issue:** No logging middleware for debugging, monitoring, or security audit trail.

**Fix:** Add structured logging middleware for all API requests.

---

## LOW SEVERITY ISSUES

### 13. Database Session Missing Rollback
**Location:** `backend/app/database.py:13-19`

**Issue:** `get_db()` doesn't rollback on exception before close.

---

### 14. Missing Input Validation (Project Name Max Length)
**Location:** `backend/app/schemas/project.py`, `backend/app/models/project.py`

**Issue:** No max length constraint on project name.

---

### 15. Foreign Key Missing Cascade Delete
**Location:** `backend/app/models/project.py:14`

**Issue:** `ForeignKey("users.id")` doesn't specify `ondelete="CASCADE"`.

---

### 16. No Pagination for Project List
**Location:** `backend/app/routers/projects.py:24`

**Issue:** Loads all projects into memory without limit.

---

### 17. Health Check Doesn't Verify Database
**Location:** `backend/app/main.py:48-50`

**Issue:** `/api/health` returns healthy without checking database connectivity.

---

## Prioritized Action Items

### Immediate (Security Critical)
- [ ] Migrate token storage from localStorage to httpOnly cookies
- [ ] Add HTTPS enforcement and HSTS headers
- [ ] Strengthen refresh token validation

### Short-Term (Architecture)
- [ ] Implement Redis-based rate limiting
- [ ] Add password complexity validation
- [ ] Extract duplicate token validation to utility
- [ ] Fix silent auth error handling
- [ ] Add React Context for user state

### Medium-Term (Quality)
- [ ] Tighten CORS configuration
- [ ] Standardize API response format
- [ ] Add request/response logging
- [ ] Add pagination for lists
- [ ] Improve health check endpoint

---

## Notes

The codebase is well-structured for its current scope. Issues identified are typical of MVP/early-stage applications. The architecture supports incremental improvement without major refactoring.

**SQL Injection:** Not a concern - all queries use SQLAlchemy ORM (parameterized).
**XSS in output:** React handles escaping by default - no raw HTML rendering observed.
