# Story 1.3: User Logout

Status: ready-for-dev

## Story

As a **logged-in user**,
I want to **log out of my account**,
So that **I can secure my session and prevent unauthorized access**.

## Acceptance Criteria

1. **Given** I am logged in **When** I click the logout button **Then** my session is terminated and I am redirected to the login page
2. **Given** I click logout **Then** my refresh token is revoked on the server (cannot be reused)
3. **Given** I click logout **Then** both access_token and refresh_token are cleared from localStorage
4. **Given** I have logged out **When** I try to access a protected route **Then** I am redirected to the login page
5. **Given** I am on any authenticated page **Then** I can see a logout button/option

## Tasks / Subtasks

- [ ] **Task 1: Dashboard Layout with Logout Button** (AC: 1, 5)
  - [ ] Create `frontend/src/components/Header.tsx` with app header containing logout button
  - [ ] Add user email display in header (read from localStorage or API)
  - [ ] Style header with Tailwind CSS matching existing design
  - [ ] Import and use Header in Dashboard page

- [ ] **Task 2: Logout Handler Implementation** (AC: 1, 2, 3)
  - [ ] Create `useLogout` hook or handler function in `frontend/src/hooks/useLogout.ts`
  - [ ] Call `authApi.logout(refresh_token)` to revoke server-side token
  - [ ] Clear `token` from localStorage
  - [ ] Clear `refresh_token` from localStorage
  - [ ] Navigate to `/login` after logout
  - [ ] Handle errors gracefully (still clear tokens and redirect even if API call fails)

- [ ] **Task 3: Update Dashboard Page** (AC: 1, 5)
  - [ ] Import Header component into Dashboard
  - [ ] Replace inline Dashboard component in App.tsx with proper page file
  - [ ] Create `frontend/src/pages/Dashboard.tsx` with Header integration

- [x] **Task 4: Backend Testing** (AC: 2) - *Already complete from Story 1.2*
  - [x] Test: logout returns 204 and revokes token
  - [x] Test: reusing revoked refresh token on /refresh returns 401
  - See: `backend/tests/api/test_auth_login_api.py:174` - `test_refresh_token_rotation_and_logout`

- [ ] **Task 5: Frontend Testing** (AC: 1, 3, 5)
  - [ ] Add test: logout button is visible on Dashboard
  - [ ] Add test: clicking logout clears localStorage tokens
  - [ ] Add test: clicking logout redirects to /login
  - [ ] Add test: logout calls the API endpoint

## Dev Notes

### Prior Work Notice

> **Backend Already Complete (Story 1.2 Scope Overlap)**
>
> During Story 1.2 implementation, the logout backend functionality was built as part of the refresh token system:
> - `POST /api/auth/logout` endpoint - revokes refresh token server-side
> - `authApi.logout()` frontend client function
> - Refresh token storage and rotation infrastructure
>
> This story focuses **only on frontend UI integration**. No backend changes required.
> See: [Story 1-2 commit 6f57914](../../) - "feat: enforce auth policies and expand tests"

### Architecture Compliance

**Backend:** Logout endpoint already implemented at `POST /api/auth/logout` in `backend/app/routers/auth.py:162-172`. No backend changes needed.

**Frontend Structure:**
- Create `frontend/src/components/Header.tsx` for reusable app header
- Create `frontend/src/hooks/useLogout.ts` for logout logic
- Create `frontend/src/pages/Dashboard.tsx` as proper page component
- Follow existing patterns from Login.tsx and Register.tsx

**Token Storage:** Uses localStorage keys `token` (access) and `refresh_token` (refresh) per story 1.2.

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| Logout API | `POST /api/auth/logout` (already exists) |
| Token clearing | `localStorage.removeItem('token')` and `localStorage.removeItem('refresh_token')` |
| Navigation | `useNavigate()` from react-router-dom |
| Error handling | Clear tokens and redirect even on API failure |

### Existing Code to Reuse

**Backend (already complete):**
```python
# backend/app/routers/auth.py:162-172
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Revoke refresh token."""
    token_hash = hash_refresh_token(payload.refresh_token)
    user = db.query(User).filter(User.refresh_token_hash == token_hash).first()
    if user:
        user.refresh_token_hash = None
        user.refresh_token_expires_at = None
        db.add(user)
        db.commit()
    return None
```

**Frontend API client (already complete):**
```typescript
// frontend/src/api/client.ts:91-92
logout: (refresh_token: string) =>
  api.post<null>('/auth/logout', { refresh_token }),
```

### Component Specifications

**Header.tsx:**
```tsx
interface HeaderProps {
  onLogout: () => void;
}
// Display app name, user email (optional), and logout button
// Style: fixed top, white background, shadow, flex layout
```

**useLogout.ts:**
```tsx
export function useLogout() {
  const navigate = useNavigate();

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } catch {
      // Ignore errors - still clear tokens
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      navigate('/login');
    }
  };

  return { logout };
}
```

### API Endpoint Spec (Reference)

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

Note: Returns 204 even if token is invalid (idempotent operation).

### References

**Planning Documents:**
- [PRD: FR3 - User Logout](../planning-artifacts/prd.md)
- [Architecture: Authentication & Security](../planning-artifacts/architecture.md)
- [Epics: Story 1.3](../planning-artifacts/epics.md#Story-1.3-User-Logout)
- [Project Context: React/TypeScript Rules](../project-context.md#React/TypeScript-Rules)

**Source: Story 1-2 (1-2-user-login.md)**
- Token storage pattern (localStorage keys)
- API client usage pattern
- Frontend component styling
- Test organization

**Source: Existing Codebase**
- [backend/app/routers/auth.py](../../backend/app/routers/auth.py) - Logout endpoint (lines 162-172)
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - authApi.logout() function
- [frontend/src/pages/Login.tsx](../../frontend/src/pages/Login.tsx) - UI patterns and styling
- [frontend/src/App.tsx](../../frontend/src/App.tsx) - Current Dashboard placeholder

## Dev Agent Record

### Agent Model Used

(To be filled by dev agent)

### Completion Notes List

(To be filled by dev agent)

### File List

**To Create (Frontend Only):**
- frontend/src/components/Header.tsx
- frontend/src/hooks/useLogout.ts
- frontend/src/pages/Dashboard.tsx
- frontend/src/components/Header.test.tsx
- frontend/src/hooks/useLogout.test.ts

**To Modify:**
- frontend/src/App.tsx (import Dashboard from pages, remove inline component)

**Already Exists (from Story 1.2):**
- backend/app/routers/auth.py - logout endpoint at lines 162-172
- frontend/src/api/client.ts - authApi.logout() function at lines 91-92
- backend/tests/api/test_auth_login_api.py:174 - `test_refresh_token_rotation_and_logout` (covers AC 2)
