# Story 1.1: User Registration

Status: done

## Story

As a **new user**,
I want to **register with email and password**,
So that **I can create an account**.

## Acceptance Criteria

1. **Given** I am on the registration page **When** I submit valid email and password **Then** my account is created and I see a success message
2. **Given** I submit a registration form **Then** my password is stored hashed with bcrypt (never plaintext)
3. **Given** I try to register with an existing email **Then** I receive an error message and registration is rejected
4. **Given** I submit empty/invalid email or password **Then** I receive validation error messages

## Tasks / Subtasks

- [x] **Task 1: Project Scaffolding** (AC: all)
  - [x] Create `backend/` directory structure per architecture
  - [x] Create `frontend/` with Vite React-TS template
  - [x] Create `docker-compose.yml` for PostgreSQL
  - [x] Create `.env.example` with required variables
  - [x] Create `backend/requirements.txt`

- [x] **Task 2: Database Setup** (AC: 1, 2)
  - [x] Create `backend/app/database.py` with SQLAlchemy engine
  - [x] Create `backend/app/models/user.py` with User model
  - [x] Create `users` table (id, email, hashed_password, created_at)
  - [x] Test database connection

- [x] **Task 3: Backend Auth Utils** (AC: 2)
  - [x] Create `backend/app/utils/auth.py`
  - [x] Implement `hash_password(password)` using bcrypt
  - [x] Implement `verify_password(plain, hashed)` for future login

- [x] **Task 4: Registration API** (AC: 1, 2, 3, 4)
  - [x] Create `backend/app/schemas/user.py` with UserCreate, UserResponse
  - [x] Create `backend/app/routers/auth.py`
  - [x] Implement `POST /api/auth/register` endpoint
  - [x] Return 400 for duplicate email
  - [x] Return 422 for validation errors
  - [x] Return 201 with user data on success

- [x] **Task 5: Frontend Setup** (AC: 1)
  - [x] Install Tailwind CSS
  - [x] Create `frontend/src/api/client.ts` with fetch wrapper
  - [x] Create basic routing structure

- [x] **Task 6: Registration UI** (AC: 1, 3, 4)
  - [x] Create `frontend/src/pages/Register.tsx`
  - [x] Form with email and password fields
  - [x] Display success message on registration
  - [x] Display error messages for failures
  - [x] Link to login page

## Dev Notes

### Architecture Compliance

- **Backend Structure:** `backend/app/` with `models/`, `routers/`, `schemas/`, `utils/`
- **Frontend Structure:** `frontend/src/` with `api/`, `components/`, `pages/`
- **Database:** PostgreSQL via Docker, SQLAlchemy ORM
- **No Alembic** - create tables directly via SQLAlchemy `create_all()`

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| Password hashing | `passlib` with bcrypt scheme |
| DB ORM | SQLAlchemy with `declarative_base()` |
| API framework | FastAPI with Pydantic schemas |
| Frontend | React 18+ functional components |
| Styling | Tailwind CSS |
| Build | Vite |

### File Structure to Create

```
TaskForge/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── auth.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── auth.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── pages/
│   │       └── Register.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── docker-compose.yml
└── .env.example
```

### API Endpoint Spec

**POST /api/auth/register**

Request:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Success Response (201):
```json
{
  "data": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-01-19T00:00:00Z"
  }
}
```

Error Response (400 - duplicate email):
```json
{
  "detail": "Email already registered"
}
```

### Dependencies

**Backend (requirements.txt):**
```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-jose
passlib[bcrypt]
python-dotenv
```

**Frontend:**
```
npm create vite@latest frontend -- --template react-ts
npm install -D tailwindcss postcss autoprefixer
```

### References

- [Architecture: Project Structure](../_bmad-output/planning-artifacts/architecture.md#project-structure)
- [Architecture: Authentication & Security](../_bmad-output/planning-artifacts/architecture.md#authentication--security)
- [Project Context: Python/FastAPI Rules](../_bmad-output/project-context.md#pythonfastapi-rules)
- [Project Context: Naming Conventions](../_bmad-output/project-context.md#naming-conventions)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Completion Notes List

- Created full project scaffolding with backend and frontend directories
- Set up PostgreSQL database connection with SQLAlchemy ORM
- Implemented bcrypt password hashing with passlib
- Created FastAPI registration endpoint with Pydantic validation
- Set up React frontend with Vite, TypeScript, and Tailwind CSS
- Implemented registration form with error/success handling
- Added server-side password length validation and backend registration tests
- Updated CORS config to use FRONTEND_URL and fixed password placeholder text

### File List

**Created:**
- backend/requirements.txt
- backend/Dockerfile
- backend/app/__init__.py
- backend/app/main.py
- backend/app/config.py
- backend/app/database.py
- backend/app/models/__init__.py
- backend/app/models/user.py
- backend/app/schemas/__init__.py
- backend/app/schemas/user.py
- backend/app/routers/__init__.py
- backend/app/routers/auth.py
- backend/app/utils/__init__.py
- backend/app/utils/auth.py
- backend/tests/test_auth_registration.py
- frontend/ (Vite scaffold)
- frontend/package.json
- frontend/package-lock.json
- frontend/index.html
- frontend/vite.config.ts
- frontend/tsconfig.json
- frontend/tsconfig.app.json
- frontend/tsconfig.node.json
- frontend/eslint.config.js
- frontend/README.md
- frontend/src/main.tsx
- frontend/src/App.tsx
- frontend/src/App.css
- frontend/src/index.css
- frontend/src/assets/react.svg
- frontend/public/vite.svg
- frontend/tailwind.config.js
- frontend/postcss.config.js
- frontend/src/api/client.ts
- frontend/src/pages/Register.tsx
- docker-compose.yml
- .env.example

**Modified:**
- frontend/src/App.tsx
- frontend/src/index.css
- backend/app/config.py
- backend/app/main.py
- backend/app/schemas/user.py
- frontend/src/pages/Register.tsx
