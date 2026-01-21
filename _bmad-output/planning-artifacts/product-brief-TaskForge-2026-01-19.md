---
stepsCompleted: [1, 2, 3, 4, 5]
inputDocuments: []
userProvidedContext: |
  TaskForge is a small, self-contained side project built to practice end-to-end full-stack development.
  It focuses on a minimal but complete scope: user authentication, project and task management, and deployment.
  Backend: FastAPI + JWT-based authentication
  Frontend: React + TypeScript
  Infrastructure: Docker containers, AWS Lightsail deployment
  Goal: Fast iteration, clear system design, production-style deployment (not feature breadth)
date: 2026-01-19
author: Yuting
---

# Product Brief: TaskForge

## Executive Summary

TaskForge is a minimal, self-hosted task management application demonstrating end-to-end full-stack development using modern technologies: FastAPI (Python), React (TypeScript), Docker, and AWS Lightsail deployment.

Beyond its technical scope, TaskForge addresses a real pain point: task data scattered across multiple tools (Obsidian, Notion) with no unified system for hierarchical planning or data export for AI analysis.

---

## Core Vision

### Problem Statement

Developers and productivity-focused individuals manage tasks across fragmented tools (markdown files, Notion, Obsidian), losing the ability to:
- View tasks in a unified, hierarchical structure (yearly → quarterly → monthly → tasks)
- Prioritize effectively using frameworks like the Eisenhower Matrix
- Export historical data for personal analytics or AI-powered insights

### Problem Impact

Without integration, task history becomes inaccessible, planning across time horizons is manual, and valuable productivity data cannot be leveraged for self-improvement or analysis.

### Why Existing Solutions Fall Short

| Tool | Gap |
|------|-----|
| Obsidian | Local-only, no API, data lives in scattered markdown files |
| Notion | Difficult to bulk export historical data for external analysis |
| Todoist/Trello | No hierarchical time-period planning, no Eisenhower Matrix |

### Proposed Solution

TaskForge: A simple, self-hosted task manager with:
- **Phase 1:** User auth, projects, tasks - deployed on AWS Lightsail
- **Phase 2:** Subtasks, time-period organization (yearly/quarterly/monthly views)
- **Phase 3:** Eisenhower Matrix prioritization, full data export for AI analysis

### Key Differentiators

1. **Full data ownership** - Self-hosted, your data is always exportable
2. **Hierarchical time planning** - Native support for yearly → quarterly → monthly structure
3. **Built for analysis** - Export endpoint designed for AI/analytics consumption
4. **Clean architecture** - Production-ready practices with modern tech stack

---

## Target Users

### Primary User: The Structured Planner

**Profile:**
- Productivity-minded individual (developer, knowledge worker)
- Manages both personal life and work tasks in one system
- Thinks in time horizons: daily → weekly → monthly → yearly → multi-year
- Examples: "grocery shopping Monday" to "hit 500k savings in 5 years"

**Context:**
- Desktop browser workflow (no mobile)
- Uses TaskForge at home and work
- Interacts throughout the day: adding, editing, checking off, deleting tasks

**Pain Points:**
- Current tools (Obsidian, Notion) are fragmented
- No unified view across time horizons
- Can't export historical data for analysis

**Success Vision:**
- All tasks in one place with clear hierarchy
- Full data ownership and export capability
- Simple, focused interface without feature bloat

### User Journey

| Stage | Experience |
|-------|------------|
| **Daily** | Open TaskForge → check today's tasks → mark complete → add new items |
| **Weekly** | Review the week, reprioritize, plan ahead |
| **Monthly/Quarterly** | Review bigger goals, adjust long-term items |
| **Value Moment** | All daily tasks checked off - clean slate satisfaction |

### Secondary Users

N/A - Scope focused on primary user type.

---

## Success Metrics

### User Success Metrics

| Metric | Indicator |
|--------|-----------|
| **Adoption** | User opens TaskForge daily instead of other tools |
| **Engagement** | Tasks are actively added, edited, and completed |
| **Value Delivery** | Daily tasks checked off = clean slate satisfaction |
| **Retention** | User continues using TaskForge over time (not returning to Obsidian/Notion) |

### Project Success Metrics

| Level | Criteria |
|-------|----------|
| **Minimum Bar** | All features functioning, passing end-to-end user tests |
| **Success** | Deployed on AWS Lightsail, running reliably |
| **Exceed Expectations** | User genuinely likes it and chooses to use it daily |

### Key Performance Indicators

| KPI | Target |
|-----|--------|
| **Functional Completeness** | All Phase 1 features working (auth, projects, tasks) |
| **Test Coverage** | End-to-end tests pass for core user flows |
| **Deployment** | Running on AWS Lightsail with Docker |
| **Usability** | User (Yuting) actively uses it for real task management |

### Business Objectives

N/A - Personal project focused on learning and practical utility.

---

## MVP Scope

### Core Features (Phase 1)

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

### Out of Scope for MVP

| Feature | Deferred To |
|---------|-------------|
| Subtasks | Phase 2 |
| Time-period views (yearly/quarterly/monthly) | Phase 2 |
| Eisenhower Matrix prioritization | Phase 3 |
| Data export endpoint | Phase 3 |
| Mobile support | Not planned |

### MVP Success Criteria

| Criteria | Validation |
|----------|------------|
| **Functional** | All CRUD operations work for users, projects, and tasks |
| **Auth** | JWT-based login/register works securely |
| **Deployed** | Running on AWS Lightsail via Docker |
| **Tested** | End-to-end user flows pass |
| **Usable** | Can actually manage real tasks with it |

### Future Vision

**Phase 2:** Subtasks + time-period organization (yearly → quarterly → monthly views)

**Phase 3:** Eisenhower Matrix prioritization + full data export for AI analysis

**Long-term:** A simple, self-hosted task manager that proves you don't need complex SaaS tools - just clean architecture and full data ownership.
