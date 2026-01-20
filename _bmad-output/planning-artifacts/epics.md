---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - "_bmad-output/planning-artifacts/prd.md"
  - "_bmad-output/planning-artifacts/architecture.md"
status: 'complete'
completedAt: '2026-01-19'
---

# TaskForge - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for TaskForge, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

- FR1: User can register with email and password
- FR2: User can log in with credentials
- FR3: User can log out
- FR4: User can access protected routes only when authenticated
- FR5: User can view list of their projects
- FR6: User can create a new project with a name
- FR7: User can view a project's details and tasks
- FR8: User can edit project name
- FR9: User can delete a project
- FR10: User can view tasks within a project
- FR11: User can create a task with title
- FR12: User can edit task title
- FR13: User can mark task as complete/incomplete
- FR14: User can delete a task

### Non-Functional Requirements

- NFR1: Page load < 3s
- NFR2: API response < 500ms
- NFR3: Smooth UI interactions (no visible lag)
- NFR4: Passwords hashed with bcrypt
- NFR5: JWT tokens with expiration
- NFR6: HTTPS in production
- NFR7: Protected API endpoints require valid token
- NFR8: Data persists across sessions
- NFR9: Graceful error handling (no crashes on bad input)

### Additional Requirements

From Architecture:
- Docker containerization for backend and frontend
- PostgreSQL database with SQLAlchemy ORM
- Manual SQL migrations (no Alembic)
- JWT tokens stored in localStorage
- Native fetch() for API calls
- Tailwind CSS for styling
- Vite for frontend build
- Specific project structure as defined in Architecture document

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 1 | User can register with email and password |
| FR2 | Epic 1 | User can log in with credentials |
| FR3 | Epic 1 | User can log out |
| FR4 | Epic 1 | User can access protected routes only when authenticated |
| FR5 | Epic 2 | User can view list of their projects |
| FR6 | Epic 2 | User can create a new project with a name |
| FR7 | Epic 2 | User can view a project's details and tasks |
| FR8 | Epic 2 | User can edit project name |
| FR9 | Epic 2 | User can delete a project |
| FR10 | Epic 3 | User can view tasks within a project |
| FR11 | Epic 3 | User can create a task with title |
| FR12 | Epic 3 | User can edit task title |
| FR13 | Epic 3 | User can mark task as complete/incomplete |
| FR14 | Epic 3 | User can delete a task |

## Epic List

### Epic 1: User Authentication
Users can securely register, login, logout, and access protected areas of the application.
**FRs covered:** FR1, FR2, FR3, FR4
**Includes:** Project scaffolding, database setup, backend/frontend structure

### Epic 2: Project Management
Users can organize their work into projects - creating, viewing, editing, and deleting projects.
**FRs covered:** FR5, FR6, FR7, FR8, FR9
**Depends on:** Epic 1 (authentication)

### Epic 3: Task Management
Users can manage tasks within their projects - creating, viewing, editing, toggling status, and deleting tasks.
**FRs covered:** FR10, FR11, FR12, FR13, FR14
**Depends on:** Epic 1 + Epic 2

---

## Epic 1: User Authentication

Users can securely register, login, logout, and access protected areas of the application.

### Story 1.1: User Registration

As a **new user**,
I want to **register with email and password**,
So that **I can create an account**.

**Acceptance Criteria:**

**Given** I am on the registration page
**When** I submit valid email and password
**Then** my account is created and I see a success message
**And** my password is stored hashed with bcrypt
**And** duplicate emails are rejected with an error message

*Includes: Backend project structure, database connection, users table, registration API endpoint, registration UI*

### Story 1.2: User Login

As a **registered user**,
I want to **log in with my credentials**,
So that **I can access my account**.

**Acceptance Criteria:**

**Given** I have a registered account
**When** I submit correct email and password
**Then** I receive a JWT token and am redirected to the dashboard
**And** invalid credentials show an error message
**And** the JWT token has an expiration time

### Story 1.3: User Logout

As a **logged-in user**,
I want to **log out**,
So that **I can secure my session**.

**Acceptance Criteria:**

**Given** I am logged in
**When** I click logout
**Then** my token is cleared from localStorage and I am redirected to login
**And** I cannot access protected routes after logout

### Story 1.4: Protected Routes

As a **user**,
I want **protected routes to require authentication**,
So that **unauthorized users cannot access my data**.

**Acceptance Criteria:**

**Given** I am not authenticated
**When** I try to access a protected route
**Then** I am redirected to the login page
**And** API endpoints return 401 for invalid/missing tokens

---

## Epic 2: Project Management

Users can organize their work into projects - creating, viewing, editing, and deleting projects.

### Story 2.1: Project List & Create

As a **user**,
I want to **view my projects and create new ones**,
So that **I can organize my work**.

**Acceptance Criteria:**

**Given** I am logged in
**When** I navigate to the projects page
**Then** I see a list of my projects
**And** I can create a new project by entering a name
**And** only my own projects are visible (not other users')

*Includes: Projects table, GET/POST /api/projects, ProjectList UI*

### Story 2.2: View Project Details

As a **user**,
I want to **view a project's details**,
So that **I can see its information and tasks**.

**Acceptance Criteria:**

**Given** I own a project
**When** I click on it in the list
**Then** I see the project detail page with its name
**And** accessing another user's project returns 403

### Story 2.3: Edit Project

As a **user**,
I want to **edit my project's name**,
So that **I can rename it**.

**Acceptance Criteria:**

**Given** I am viewing my project
**When** I edit the name and save
**Then** the change is persisted
**And** empty names are rejected with an error

### Story 2.4: Delete Project

As a **user**,
I want to **delete a project**,
So that **I can remove projects I no longer need**.

**Acceptance Criteria:**

**Given** I own a project
**When** I delete it
**Then** it is removed from my list
**And** I see a confirmation before deletion

---

## Epic 3: Task Management

Users can manage tasks within their projects - creating, viewing, editing, toggling status, and deleting tasks.

### Story 3.1: View Tasks & Create

As a **user**,
I want to **view tasks in my project and create new ones**,
So that **I can track my work**.

**Acceptance Criteria:**

**Given** I am on a project detail page
**When** I view the tasks section
**Then** I see all tasks for that project
**And** I can create a new task by entering a title
**And** new tasks default to incomplete status

*Includes: Tasks table, GET/POST /api/projects/:id/tasks, TaskList UI*

### Story 3.2: Edit Task

As a **user**,
I want to **edit a task's title**,
So that **I can update task details**.

**Acceptance Criteria:**

**Given** I have a task in my project
**When** I edit its title and save
**Then** the change is persisted
**And** empty titles are rejected with an error

### Story 3.3: Toggle Task Status

As a **user**,
I want to **mark tasks as complete or incomplete**,
So that **I can track my progress**.

**Acceptance Criteria:**

**Given** I have a task
**When** I toggle its status
**Then** it switches between complete and incomplete
**And** the UI visually distinguishes completed tasks

### Story 3.4: Delete Task

As a **user**,
I want to **delete a task**,
So that **I can remove tasks I no longer need**.

**Acceptance Criteria:**

**Given** I have a task in my project
**When** I delete it
**Then** it is removed from the task list
