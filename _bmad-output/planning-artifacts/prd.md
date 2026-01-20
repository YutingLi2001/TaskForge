---
stepsCompleted: ["step-01-init", "step-02-discovery", "step-03-success", "step-04-journeys", "step-05-domain", "step-06-innovation", "step-07-project-type", "step-08-scoping", "step-09-functional", "step-10-nonfunctional", "step-11-polish", "step-12-complete"]
inputDocuments:
  - "_bmad-output/planning-artifacts/product-brief-TaskForge-2026-01-19.md"
workflowType: "prd"
briefCount: 1
researchCount: 0
brainstormingCount: 0
projectDocsCount: 0
classification:
  projectType: "Web Application (Full-stack)"
  domain: "Productivity / Task Management"
  complexity: "Low"
  projectContext: "greenfield"
---

# Product Requirements Document - TaskForge

**Author:** Yuting
**Date:** 2026-01-19

## Success Criteria

### User Success

- All core features function correctly (auth, projects, tasks CRUD)
- End-to-end user flows pass testing
- Clean, intuitive interface that doesn't get in the way

### Business Success

N/A - Personal learning project focused on skill development and practical utility.

### Technical Success

- Deployed and running on AWS Lightsail
- Docker containers working properly
- JWT authentication implemented securely
- RESTful API design following best practices

### Measurable Outcomes

| Outcome | Validation |
|---------|------------|
| All CRUD operations work | Manual + E2E tests pass |
| Authentication secure | JWT flow works correctly |
| Deployed successfully | Running on AWS Lightsail |
| Usable | Yuting actively uses it for real task management |

## Product Scope

### MVP - Minimum Viable Product (Phase 1)

**Backend (FastAPI + Python):**
- User registration & login with JWT authentication
- CRUD operations for Projects
- CRUD operations for Tasks (within projects)
- RESTful API design

**Frontend (React + TypeScript):**
- Authentication flows (login, register, protected routes)
- Project list and detail views
- Task management UI (add, edit, delete, check-off)
- Clean, simple interface

**Infrastructure:**
- Dockerized backend and frontend
- PostgreSQL database
- Deployed on AWS Lightsail

### Growth Features (Phase 2)

- Subtasks within tasks
- Time-period views (yearly → quarterly → monthly organization)

### Vision (Phase 3)

- Eisenhower Matrix prioritization
- Data export endpoint for AI analysis

## User Journeys

### Journey 1: Daily Task Management

Yuting opens TaskForge → sees project list → selects active project → reviews tasks → checks off completed ones → adds new tasks as needed → done.

### Journey 2: New Project Setup

Yuting has a new goal → logs in → creates new project → adds initial tasks → organizes work breakdown → starts working.

### Journey Requirements Summary

| Capability | Source |
|------------|--------|
| User authentication | Both |
| Project CRUD | Journey 2 |
| Task CRUD | Both |
| Task status toggle | Journey 1 |

## Web Application Requirements

### Technical Architecture

- **Frontend:** React SPA with TypeScript
- **Backend:** FastAPI REST API
- **Database:** PostgreSQL
- **Auth:** JWT tokens

### Browser Support

- Modern browsers only (Chrome, Firefox, Edge latest versions)
- Desktop-focused, no mobile optimization for MVP

### Performance Targets

- Page load < 3s on standard connection
- API response < 500ms for CRUD operations

## Functional Requirements

### User Management

- FR1: User can register with email and password
- FR2: User can log in with credentials
- FR3: User can log out
- FR4: User can access protected routes only when authenticated

### Project Management

- FR5: User can view list of their projects
- FR6: User can create a new project with a name
- FR7: User can view a project's details and tasks
- FR8: User can edit project name
- FR9: User can delete a project

### Task Management

- FR10: User can view tasks within a project
- FR11: User can create a task with title
- FR12: User can edit task title
- FR13: User can mark task as complete/incomplete
- FR14: User can delete a task

## Non-Functional Requirements

### Performance

- Page load < 3s
- API response < 500ms
- Smooth UI interactions (no visible lag)

### Security

- Passwords hashed (bcrypt)
- JWT tokens with expiration
- HTTPS in production
- Protected API endpoints require valid token

### Reliability

- Data persists across sessions
- Graceful error handling (no crashes on bad input)
