# Story 1.4: Protected Routes

Status: done

## Story

As a **user**,
I want **protected routes to require authentication**,
So that **unauthorized users cannot access my data**.

## Acceptance Criteria

1. **Given** I am not authenticated **When** I try to access `/dashboard` **Then** I am redirected to the login page
2. **Given** I have an expired or invalid token **When** I try to access a protected route **Then** I am redirected to the login page
3. **Given** I make an API request without a token **Then** the API returns 401 Unauthorized
4. **Given** I make an API request with an invalid/expired token **Then** the API returns 401 Unauthorized
5. **Given** I am authenticated with a valid token **Then** I can access protected routes and API endpoints normally
6. **Given** I am on the login or register page **When** I am already authenticated **Then** I am redirected to the dashboard

## Tasks / Subtasks

- [x] **Task 1: Backend Auth Dependency** (AC: 3, 4, 5)
  - [x] Create `get_current_user` dependency in `backend/app/utils/auth.py`
  - [x] Add `OAuth2PasswordBearer` scheme pointing to `/api/auth/login`
  - [x] Decode JWT token from Authorization header
  - [x] Validate token signature, expiration, and type
  - [x] Return user object or raise HTTPException 401
  - [x] Add `decode_access_token` helper function

- [x] **Task 2: Backend Protected Endpoint Test** (AC: 3, 4, 5)
  - [x] Create test endpoint `GET /api/auth/me` that requires authentication
  - [x] Returns current user data (id, email, created_at)
  - [x] Add tests: valid token returns 200 + user data
  - [x] Add tests: missing token returns 401
  - [x] Add tests: invalid token returns 401
  - [x] Add tests: expired token returns 401

- [x] **Task 3: Frontend ProtectedRoute Component** (AC: 1, 2, 5)
  - [x] Create `frontend/src/components/ProtectedRoute.tsx`
  - [x] Check for token in localStorage
  - [x] Redirect to `/login` if no token present
  - [x] Render children if authenticated
  - [x] Store intended destination for redirect after login (optional)

- [x] **Task 4: Frontend Public Route Redirect** (AC: 6)
  - [x] Create `frontend/src/components/PublicRoute.tsx` (or add logic to Login/Register)
  - [x] Redirect authenticated users away from login/register to dashboard
  - [x] Check token presence on mount

- [x] **Task 5: Update App Routing** (AC: 1, 2, 5, 6)
  - [x] Wrap `/dashboard` route with ProtectedRoute
  - [x] Wrap `/login` and `/register` with PublicRoute logic
  - [x] Test navigation flows work correctly

- [x] **Task 6: Frontend Testing** (AC: 1, 2, 5, 6)
  - [x] Add test: ProtectedRoute redirects when no token
  - [x] Add test: ProtectedRoute renders children when token exists
  - [x] Add test: PublicRoute redirects authenticated users to dashboard
  - [x] Add test: Login page redirects if already authenticated

- [x] **Task 7: Integration Testing** (AC: all)
  - [x] Test full flow: unauthenticated user → protected route → login → dashboard
  - [x] Test: logout → try protected route → redirect to login
  - [x] Verify API calls with token succeed, without token fail

## Dev Notes

### Prior Work Notice

> **Partial Implementation Exists**
>
> Dashboard.tsx already has a basic token check in useEffect (Story 1.3), but this is not a proper protected route pattern.
> This story implements the proper ProtectedRoute wrapper component and backend auth dependency.

### Architecture Compliance

**Backend Structure:**
- Add `get_current_user` and `decode_access_token` to `backend/app/utils/auth.py`
- Add `/api/auth/me` endpoint to `backend/app/routers/auth.py`
- Use FastAPI's `Depends()` for dependency injection

**Frontend Structure:**
- Create `frontend/src/components/ProtectedRoute.tsx`
- Create `frontend/src/components/PublicRoute.tsx`
- Update `frontend/src/App.tsx` routing

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| JWT Validation | `python-jose` decode with SECRET_KEY |
| Auth Scheme | `OAuth2PasswordBearer(tokenUrl="/api/auth/login")` |
| Token Header | `Authorization: Bearer <token>` |
| 401 Response | `HTTPException(status_code=401, detail="...")` |
| Route Protection | React component wrapper pattern |

### Component Specifications

**get_current_user dependency:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
```

**ProtectedRoute.tsx:**
```tsx
import { Navigate, useLocation } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const location = useLocation();
  const token = localStorage.getItem('token');

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
```

**PublicRoute.tsx:**
```tsx
import { Navigate } from 'react-router-dom';

interface PublicRouteProps {
  children: React.ReactNode;
}

export default function PublicRoute({ children }: PublicRouteProps) {
  const token = localStorage.getItem('token');

  if (token) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
```

### API Endpoint Spec

**GET /api/auth/me** (Protected)

Request Headers:
```
Authorization: Bearer <access_token>
```

Success Response (200):
```json
{
  "data": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-01-19T00:00:00Z"
  }
}
```

Error Response (401 - no token):
```json
{
  "detail": "Not authenticated"
}
```

Error Response (401 - invalid token):
```json
{
  "detail": "Could not validate credentials"
}
```

### References

**Planning Documents:**
- [PRD: FR4 - Protected Routes](../planning-artifacts/prd.md)
- [Architecture: Authentication & Security](../planning-artifacts/architecture.md)
- [Epics: Story 1.4](../planning-artifacts/epics.md#Story-1.4-Protected-Routes)
- [Project Context: Python/FastAPI Rules](../project-context.md#Python/FastAPI-Rules)

**Source: Previous Stories**
- [Story 1-2](1-2-user-login.md) - JWT token creation, login flow
- [Story 1-3](1-3-user-logout.md) - Token storage keys, logout flow, Header component

**Source: Existing Codebase**
- [backend/app/utils/auth.py](../../backend/app/utils/auth.py) - Add get_current_user here
- [backend/app/routers/auth.py](../../backend/app/routers/auth.py) - Add /me endpoint here
- [frontend/src/App.tsx](../../frontend/src/App.tsx) - Update routing here
- [frontend/src/pages/Dashboard.tsx](../../frontend/src/pages/Dashboard.tsx) - Has basic token check (to be replaced)

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Implementation Plan

- Add backend auth dependency and /me endpoint with tests.
- Implement ProtectedRoute/PublicRoute with token validation.
- Update routing to enforce protected/public access.
- Add frontend/integration tests and run scripts.

### Completion Notes List

- Added backend auth helpers (`decode_access_token`, `get_current_user`) and `/api/auth/me`.
- Implemented ProtectedRoute/PublicRoute with JWT expiry/format checks and server validation via `/api/auth/me`.
- Wrapped login/register/dashboard routes with public/protected guards.
- Adjusted `/api/auth/me` response to limit fields and return 403 for inactive users.
- Tests: `scripts/windows/run-frontend-tests.ps1` (pass)
- Tests: `scripts/windows/run-backend-tests.ps1` (pass; warnings in log: FastAPI on_event deprecation, sqlite connection not closed)

### File List

- backend/app/routers/auth.py
- backend/app/schemas/user.py
- backend/app/utils/auth.py
- backend/tests/api/test_auth_me_api.py
- backend/tests/unit/test_auth_dependency.py
- frontend/src/App.tsx
- frontend/src/AppRouting.test.tsx
- frontend/src/api/client.ts
- frontend/src/components/ProtectedRoute.tsx
- frontend/src/components/ProtectedRoute.test.tsx
- frontend/src/components/PublicRoute.tsx
- frontend/src/components/PublicRoute.test.tsx

### Change Log

- 2026-01-21: Added auth dependency, /me endpoint, protected/public routing, and tests.
- 2026-01-21: Code review fixes: validate tokens via `/api/auth/me`, limit /me response, inactive users return 403.
