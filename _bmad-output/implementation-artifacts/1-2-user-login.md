# Story 1.2: User Login

Status: review

## Story

As a **registered user**,
I want to **log in with my email and password**,
So that **I can access my account and use the application**.

## Acceptance Criteria

1. **Given** I am on the login page **When** I submit valid credentials **Then** I am authenticated and redirected to the dashboard
2. **Given** I submit login credentials **Then** I receive a JWT access token that is stored in localStorage
3. **Given** I try to login with invalid credentials **Then** I receive an error message and login is rejected
4. **Given** I submit empty/invalid email or password **Then** I receive validation error messages
5. **Given** I successfully log in **Then** subsequent API requests include the JWT token in the Authorization header

## Tasks / Subtasks

- [x] **Task 1: JWT Token Generation** (AC: 2, 5)
  - [x] Ensure `SECRET_KEY` is configured (already in `backend/app/config.py` and `.env.example`)
  - [x] Ensure `ACCESS_TOKEN_EXPIRE_MINUTES` is documented in `.env.example`
  - [x] Implement `create_access_token(data: dict, expires_delta: timedelta | None)` in `backend/app/utils/auth.py`
  - [x] Implement refresh token creation + hashing
  - [x] Support remember-me refresh expiry

- [x] **Task 2: Login API Endpoint** (AC: 1, 2, 3, 4)
  - [x] Add `LoginRequest`, `LoginResponse`, `LoginDataResponse` schemas in `backend/app/schemas/user.py`
  - [x] Implement `POST /api/auth/login` in `backend/app/routers/auth.py`
  - [x] Validate credentials with `verify_password()` from `utils/auth.py`
  - [x] Normalize email (trim + lowercase)
  - [x] Return 401 for invalid credentials
  - [x] Enforce account lockout + rate limit
  - [x] Add refresh token rotation endpoint
  - [x] Add logout endpoint to revoke refresh token
  - [x] Return 200 with token + user data on success

- [x] **Task 3: Login Frontend Page** (AC: 1, 3, 4, 5)
  - [x] Create `frontend/src/pages/Login.tsx`
  - [x] Form with email and password fields (similar to Register)
  - [x] Call `/auth/login` endpoint on submit
  - [x] Store `access_token` in localStorage on success
  - [x] Store `refresh_token` in localStorage on success
  - [x] Add remember-me toggle
  - [x] Display error messages for failures
  - [x] Redirect to dashboard/home after successful login
  - [x] Link to registration page

- [x] **Task 4: Update API Client** (AC: 2, 5)
  - [x] Add `login()` function to `authApi` in `frontend/src/api/client.ts`
  - [x] Verify token is automatically included in subsequent requests (already implemented)
  - [x] Add `refresh()` and `logout()` functions

- [x] **Task 5: Testing** (AC: all)
  - [x] Test login success returns 200 + tokens
  - [x] Test invalid credentials return 401
  - [x] Test invalid email returns 422
  - [x] Test disabled/locked account behavior
  - [x] Test rate limiting behavior
  - [x] Test refresh token rotation and logout
  - [x] Test remember-me extends refresh expiry
  - [x] Test Authorization header includes stored token
  - [x] Test login UI shows error on failure

## Dev Notes

### Architecture Compliance

**Backend Structure:**
- Add login endpoint to existing `backend/app/routers/auth.py`
- Extend `backend/app/utils/auth.py` with JWT token creation
- Add new schemas to `backend/app/schemas/user.py`

**Frontend Structure:**
- Create new page at `frontend/src/pages/Login.tsx`
- Extend `frontend/src/api/client.ts` authApi object
- Follow same pattern as Register page (Tailwind styling, error/success handling)

**Database:** No new tables needed - use existing `users` table from story 1-1

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| JWT Token Generation | `python-jose` (already in requirements.txt) |
| Password Verification | `verify_password()` from `utils/auth.py` |
| Token Storage | localStorage |
| Token Header | `Authorization: Bearer <token>` (client.ts already injects) |
| Token Expiration | 15 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`) |
| Refresh Tokens | Rotating refresh tokens + logout revocation |
| Remember Me | Longer refresh token expiry |
| Rate Limit | IP + email throttling |
| Account Lockout | Lock after repeated failures |

### API Endpoint Spec

**POST /api/auth/login**

Request:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Success Response (200):
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "r1eF...longtoken...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "created_at": "2026-01-19T00:00:00Z"
    }
  }
}
```

Error Response (401 - invalid credentials):
```json
{
  "detail": "Invalid email or password"
}
```

**POST /api/auth/refresh**

Request:
```json
{
  "refresh_token": "r1eF...longtoken..."
}
```

Success Response (200):
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "r1eF...newtoken...",
    "token_type": "bearer"
  }
}
```

**POST /api/auth/logout**

Request:
```json
{
  "refresh_token": "r1eF...longtoken..."
}
```

Success Response (204):
```
No Content
```

### References

**Planning Documents:**
- [PRD: FR1 - User Registration](../planning-artifacts/prd.md#User-Management)
- [Architecture: Authentication & Security](../planning-artifacts/architecture.md#Core-Architectural-Decisions)
- [Epics: Story 1.2](../planning-artifacts/epics.md#Story-1.2-User-Login)
- [Project Context: Python/FastAPI Rules](../project-context.md#Python/FastAPI-Rules)

**Source: Story 1-1 (1-1-user-registration.md)**
- Backend structure and patterns
- Frontend component structure
- API response format
- Error handling approach

**Source: Existing Codebase**
- [backend/app/utils/auth.py](../../backend/app/utils/auth.py) - verify_password() already implemented
- [backend/app/routers/auth.py](../../backend/app/routers/auth.py) - Add login endpoint here
- [backend/app/models/user.py](../../backend/app/models/user.py) - User model with email/password
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - Token injection already implemented
- [frontend/src/pages/Register.tsx](../../frontend/src/pages/Register.tsx) - Template for Login page

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Completion Notes List

- Added JWT access + refresh token creation with rotation and remember-me support
- Implemented login, refresh, and logout endpoints with rate limiting and lockout
- Normalized emails and enforced password length bounds
- Built Login UI with remember-me and token storage
- Added backend and frontend edge-case tests
- Organized backend tests into unit and api folders

### File List

**Created:**
- backend/tests/unit/test_auth_login.py
- backend/tests/api/test_auth_login_api.py
- frontend/src/pages/Login.tsx
- frontend/src/api/client.test.ts
- frontend/src/pages/Login.test.tsx
- frontend/src/setupTests.ts
- backend/tests/__init__.py
- backend/tests/unit/__init__.py
- backend/tests/api/__init__.py

**Modified:**
- backend/app/utils/auth.py
- backend/app/schemas/user.py
- backend/app/routers/auth.py
- backend/app/config.py
- backend/app/models/user.py
- backend/tests/unit/test_auth_registration.py
- backend/tests/api/test_auth_registration_api.py
- frontend/src/api/client.ts
- frontend/src/App.tsx
- frontend/src/pages/Register.tsx
- frontend/package.json
- frontend/vite.config.ts
- .env.example
