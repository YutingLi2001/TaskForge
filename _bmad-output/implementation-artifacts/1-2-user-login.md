# Story 1.2: User Login

Status: ready-for-dev

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

- [ ] **Task 1: JWT Token Generation** (AC: 2, 5)
  - [ ] Create JWT secret key configuration in `backend/app/config.py`
  - [ ] Implement `create_access_token(data: dict)` in `backend/app/utils/auth.py`
  - [ ] Add token expiration handling (e.g., 30 days or configurable)

- [ ] **Task 2: Login API Endpoint** (AC: 1, 2, 3, 4)
  - [ ] Create `LoginRequest` schema in `backend/app/schemas/user.py`
  - [ ] Create `LoginResponse` schema with `access_token` and `user` fields
  - [ ] Implement `POST /api/auth/login` in `backend/app/routers/auth.py`
  - [ ] Validate credentials using `verify_password()` from utils
  - [ ] Return 401 for invalid credentials
  - [ ] Return 200 with token + user data on success

- [ ] **Task 3: Login Frontend Page** (AC: 1, 3, 4, 5)
  - [ ] Create `frontend/src/pages/Login.tsx`
  - [ ] Form with email and password fields (similar to Register)
  - [ ] Call `/auth/login` endpoint on submit
  - [ ] Store `access_token` in localStorage on success
  - [ ] Display error messages for failures
  - [ ] Redirect to dashboard/home after successful login
  - [ ] Link to registration page

- [ ] **Task 4: Update API Client** (AC: 2, 5)
  - [ ] Add `login()` function to `authApi` in `frontend/src/api/client.ts`
  - [ ] Verify token is automatically included in subsequent requests (already implemented)

- [ ] **Task 5: Testing** (AC: all)
  - [ ] Test successful login flow end-to-end
  - [ ] Test invalid email returns 401
  - [ ] Test invalid password returns 401
  - [ ] Test token is stored in localStorage
  - [ ] Test token is sent in Authorization header

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
| Password Verification | Use existing `verify_password()` from `utils/auth.py` |
| Token Storage | localStorage in browser |
| Token Header | `Authorization: Bearer <token>` (already implemented in client.ts:19) |
| Token Expiration | 30 days (configurable via environment variable) |

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

### JWT Token Structure

```python
# Token payload
{
  "sub": "user@example.com",  # Subject (user email)
  "exp": 1234567890,           # Expiration timestamp
  "iat": 1234567890            # Issued at timestamp
}
```

### Code Examples

**Backend - JWT Token Creation:**
```python
from jose import jwt
from datetime import datetime, timedelta
from ..config import settings

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

**Backend - Login Endpoint:**
```python
@router.post("/login", response_model=LoginDataResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    return LoginDataResponse(
        data=LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
    )
```

**Frontend - Login Page Structure:**
```tsx
// Similar to Register.tsx with these changes:
// 1. Call authApi.login() instead of authApi.register()
// 2. On success: localStorage.setItem('token', response.data.access_token)
// 3. On success: navigate('/dashboard') or navigate('/')
// 4. Link to /register instead of /login
```

### Previous Story Intelligence (from 1-1-user-registration)

**Key Learnings:**
1. ✅ Password verification function `verify_password()` already exists in `utils/auth.py`
2. ✅ User model has email + hashed_password fields ready for login
3. ✅ API response pattern: wrap in `{data: {...}}` format
4. ✅ Frontend uses React functional components with useState hooks
5. ✅ Error handling: display error messages in red alert boxes
6. ✅ Success handling: display success messages in green alert boxes
7. ✅ Form validation: use HTML5 required + minLength attributes
8. ✅ API client already has token injection logic (client.ts:15-19)
9. ✅ Tailwind CSS classes for consistent styling

**Files Already Created (from 1-1):**
- `backend/app/routers/auth.py` - ADD login endpoint here
- `backend/app/utils/auth.py` - ADD create_access_token() here
- `backend/app/schemas/user.py` - ADD Login schemas here
- `backend/app/models/user.py` - Already has all fields needed
- `frontend/src/api/client.ts` - ADD authApi.login() here
- `frontend/src/pages/Register.tsx` - Use as template for Login.tsx

**Dependencies Already Installed:**
- Backend: `python-jose` (for JWT), `passlib` (for password verification)
- Frontend: React Router (for navigation), Tailwind CSS (for styling)

### Git Intelligence

**Recent Commits Analysis:**
- ✅ Story 1-1 merged to develop branch
- ✅ Registration feature fully implemented and tested
- ✅ Project scaffolding complete (backend + frontend + docker)
- Pattern: Feature branches merged to develop

**Recommended Approach:**
1. Create feature branch: `feature/story-1-2-login`
2. Follow same commit pattern as 1-1: implement → test → merge
3. Update sprint-status.yaml after completion

### Dependencies and Environment

**Required Environment Variables (add to .env):**
```env
SECRET_KEY=<generate-secure-random-string>  # For JWT signing
TOKEN_EXPIRE_DAYS=30  # Optional, defaults to 30
```

**No New Package Dependencies** - All required libraries already installed in story 1-1

### Security Considerations

1. **Secret Key**: MUST be a secure random string, never commit to git
2. **Token Expiration**: Set reasonable expiration (30 days recommended)
3. **HTTPS**: In production, tokens should only be transmitted over HTTPS
4. **Password Attempts**: Consider rate limiting in future (not required for this story)
5. **Token Storage**: localStorage is acceptable for MVP (consider httpOnly cookies in production)

### Testing Checklist

- [ ] Login with valid credentials returns 200 + token + user data
- [ ] Login with invalid email returns 401
- [ ] Login with invalid password returns 401
- [ ] Login with empty fields shows validation errors
- [ ] Token is stored in localStorage after successful login
- [ ] Subsequent API requests include token in Authorization header
- [ ] Frontend redirects to dashboard after successful login
- [ ] Error messages display correctly in UI

### References

**Source: Story 1-1 (1-1-user-registration.md)**
- Backend structure and patterns
- Frontend component structure
- API response format
- Error handling approach

**Source: Existing Codebase**
- [backend/app/utils/auth.py](../../backend/app/utils/auth.py) - verify_password() already implemented
- [backend/app/routers/auth.py](../../backend/app/routers/auth.py) - Add login endpoint here
- [backend/app/models/user.py](../../backend/app/models/user.py) - User model with email/password
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - Token injection already implemented (line 15)
- [frontend/src/pages/Register.tsx](../../frontend/src/pages/Register.tsx) - Template for Login page

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Completion Notes List

_To be filled by dev agent during implementation_

### File List

**To be created:**
- frontend/src/pages/Login.tsx

**To be modified:**
- backend/app/config.py (add SECRET_KEY)
- backend/app/utils/auth.py (add create_access_token)
- backend/app/schemas/user.py (add LoginRequest, LoginResponse, LoginDataResponse)
- backend/app/routers/auth.py (add POST /login endpoint)
- frontend/src/api/client.ts (add authApi.login)
- frontend/src/App.tsx (add /login route)
- .env.example (add SECRET_KEY)
