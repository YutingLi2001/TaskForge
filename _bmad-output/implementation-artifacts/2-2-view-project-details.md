# Story 2.2: View Project Details

Status: done

## Story

As a **user**,
I want to **view a project's details**,
So that **I can see its information and tasks**.

## Acceptance Criteria

1. **Given** I own a project **When** I click on it in the list **Then** I am navigated to the project detail page
2. **Given** I am on a project detail page **Then** I see the project name, created date, and updated date
3. **Given** I try to access a project I don't own via URL **Then** the API returns 403 Forbidden
4. **Given** I try to access a project that doesn't exist **Then** the API returns 404 Not Found
5. **Given** I am not authenticated **When** I try to access /projects/:id **Then** I am redirected to login / API returns 401
6. **Given** I am on the project detail page **Then** I see a link to go back to the projects list

## Tasks / Subtasks

- [x] **Task 1: Backend GET Project Endpoint** (AC: 2, 3, 4, 5)
  - [x] Add `GET /api/projects/{project_id}` endpoint to `backend/app/routers/projects.py`
  - [x] Use `get_current_user` dependency for authentication
  - [x] Query project by ID
  - [x] Return 404 if project not found
  - [x] Return 403 if project.user_id != current_user.id
  - [x] Return project data with 200 on success

- [x] **Task 2: Backend Testing** (AC: 2, 3, 4, 5)
  - [x] Add tests to `backend/tests/api/test_projects_api.py`
  - [x] Test: GET /projects/{id} returns project data for owner
  - [x] Test: GET /projects/{id} returns 404 for non-existent project
  - [x] Test: GET /projects/{id} returns 403 for non-owner
  - [x] Test: GET /projects/{id} returns 401 for unauthenticated request

- [x] **Task 3: Frontend API Client** (AC: 2)
  - [x] Add `get(id: number)` method to `projectsApi` in `frontend/src/api/client.ts`
  - [x] Returns `ApiResponse<ProjectData>`

- [x] **Task 4: Project Detail Page** (AC: 1, 2, 6)
  - [x] Create `frontend/src/pages/ProjectDetail.tsx`
  - [x] Fetch project data on mount using project ID from URL params
  - [x] Display project name, created date, updated date
  - [x] Show loading state while fetching
  - [x] Show error state on fetch failure
  - [x] Add "Back to Projects" link
  - [x] Handle 403/404 errors gracefully (show message, link back)
  - [x] Style with Tailwind CSS matching existing design

- [x] **Task 5: Make Project List Clickable** (AC: 1)
  - [x] Update `frontend/src/pages/Projects.tsx`
  - [x] Wrap each project item with `Link` to `/projects/{id}`
  - [x] Add hover state styling for clickable items

- [x] **Task 6: Update App Routing** (AC: 1, 5)
  - [x] Add `/projects/:id` route to `frontend/src/App.tsx`
  - [x] Wrap with ProtectedRoute
  - [x] Import and render ProjectDetail component

- [x] **Task 7: Frontend Testing** (AC: 1, 2, 3, 4, 6)
  - [x] Create `frontend/src/pages/ProjectDetail.test.tsx`
  - [x] Test: ProjectDetail renders project data
  - [x] Test: ProjectDetail shows loading state
  - [x] Test: ProjectDetail shows error for 404
  - [x] Test: ProjectDetail shows error for 403
  - [x] Test: Back link navigates to /projects
  - [x] Update `frontend/src/pages/Projects.test.tsx` if needed for clickable items

## Dev Notes

### Architecture Compliance

**Backend Structure:**
- Endpoint: `backend/app/routers/projects.py` (add to existing file)
- Tests: `backend/tests/api/test_projects_api.py` (add to existing file)

**Frontend Structure:**
- Page: `frontend/src/pages/ProjectDetail.tsx` (new file)
- API: `frontend/src/api/client.ts` (add method to projectsApi)
- Route: `frontend/src/App.tsx` (add route)

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| Authentication | `get_current_user` dependency |
| Authorization | Check `project.user_id == current_user.id` |
| 403 Response | `HTTPException(status_code=403, detail="Not authorized")` |
| 404 Response | `HTTPException(status_code=404, detail="Project not found")` |
| URL Parameter | Use `useParams` from react-router-dom |

### API Endpoint Spec

**GET /api/projects/{project_id}** (Protected)

Request Headers:
```
Authorization: Bearer <access_token>
```

Success Response (200):
```json
{
  "data": {
    "id": 1,
    "name": "My Project",
    "user_id": 1,
    "created_at": "2026-01-21T00:00:00Z",
    "updated_at": "2026-01-21T00:00:00Z"
  }
}
```

Error Response (401 - not authenticated):
```json
{
  "detail": "Not authenticated"
}
```

Error Response (403 - not owner):
```json
{
  "detail": "Not authorized to access this project"
}
```

Error Response (404 - not found):
```json
{
  "detail": "Project not found"
}
```

### Component Specifications

**Backend Endpoint:**
```python
@router.get("/{project_id}", response_model=ProjectDataResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    return ProjectDataResponse(data=ProjectResponse.model_validate(project))
```

**Frontend projectsApi update:**
```typescript
export const projectsApi = {
  list: () => api.get<ApiResponse<ProjectData[]>>('/projects'),
  create: (data: CreateProjectData) =>
    api.post<ApiResponse<ProjectData>>('/projects', data),
  get: (id: number) => api.get<ApiResponse<ProjectData>>(`/projects/${id}`),
};
```

**ProjectDetail.tsx:**
```tsx
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Header from '../components/Header';
import { ApiRequestError, projectsApi, ProjectData } from '../api/client';
import { useLogout } from '../hooks/useLogout';

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const { logout } = useLogout();
  const userEmail = localStorage.getItem('user_email');
  const [project, setProject] = useState<ProjectData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    setLoading(true);
    projectsApi
      .get(parseInt(id, 10))
      .then((response) => {
        setProject(response.data);
        setError(null);
      })
      .catch((err) => {
        if (err instanceof ApiRequestError) {
          if (err.status === 401) {
            logout();
            return;
          }
          if (err.status === 403) {
            setError('You do not have access to this project.');
            return;
          }
          if (err.status === 404) {
            setError('Project not found.');
            return;
          }
        }
        setError(err instanceof Error ? err.message : 'Failed to load project');
      })
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onLogout={logout} userEmail={userEmail} />
      <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-8 px-6 pb-12 pt-24">
        <Link to="/projects" className="text-blue-600 hover:underline text-sm">
          &larr; Back to Projects
        </Link>

        {loading ? (
          <p className="text-sm text-gray-600">Loading project...</p>
        ) : error ? (
          <div className="rounded-lg bg-white p-6 shadow-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        ) : project ? (
          <section className="rounded-lg bg-white p-6 shadow-md">
            <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
            <div className="mt-4 space-y-2 text-sm text-gray-600">
              <p>Created: {new Date(project.created_at).toLocaleString()}</p>
              <p>Updated: {new Date(project.updated_at).toLocaleString()}</p>
            </div>
          </section>
        ) : null}
      </main>
    </div>
  );
}
```

**Projects.tsx update (make items clickable):**
```tsx
import { Link } from 'react-router-dom';

// In the project list, wrap with Link:
<li key={project.id}>
  <Link
    to={`/projects/${project.id}`}
    className="block rounded-md border border-gray-200 px-4 py-3 hover:bg-gray-50 transition-colors"
  >
    <p className="text-sm font-semibold text-gray-900">{project.name}</p>
    <p className="text-xs text-gray-500">
      Created {new Date(project.created_at).toLocaleDateString(...)}
    </p>
  </Link>
</li>
```

### References

**Planning Documents:**
- [PRD: FR7](../planning-artifacts/prd.md)
- [Architecture: Project Structure](../planning-artifacts/architecture.md)
- [Epics: Story 2.2](../planning-artifacts/epics.md#Story-2.2-View-Project-Details)

**Source: Story 2-1 Implementation**
- [backend/app/routers/projects.py](../../backend/app/routers/projects.py) - Add endpoint here
- [backend/app/schemas/project.py](../../backend/app/schemas/project.py) - Response schemas exist
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - Add get method here
- [frontend/src/pages/Projects.tsx](../../frontend/src/pages/Projects.tsx) - Update list items

**Source: Epic 1 Patterns**
- [frontend/src/components/ProtectedRoute.tsx](../../frontend/src/components/ProtectedRoute.tsx) - Route protection
- [frontend/src/App.tsx](../../frontend/src/App.tsx) - Routing structure

## Dev Agent Record

### Agent Model Used

GPT-5 (Codex CLI)

### Implementation Plan

- Add GET /api/projects/{id} with ownership checks and proper 401/403/404 handling.
- Expand projects API tests for owner access, forbidden, not found, and unauthenticated cases.
- Extend frontend projectsApi with get(id) and add ProjectDetail page with error states and back link.
- Make project list items link to detail view and add /projects/:id route.
- Add frontend tests for ProjectDetail and clickable list behavior.

### Completion Notes List

- Implemented GET /api/projects/{id} with 404/403 handling and owner validation.
- Added backend tests for project detail access (owner, 403, 404, 401).
- Added ProjectDetail page with loading/error states and back link.
- Made project list items link to detail view and added /projects/:id route.
- Added ProjectDetail tests and updated Projects tests for links.
- Tests: `python -m unittest backend.tests.api.test_projects_api`, `npm test`, `scripts/windows/run-backend-tests.bat`, `scripts/windows/run-frontend-tests.bat`.

### File List

**Created:**
- frontend/src/pages/ProjectDetail.test.tsx
- frontend/src/pages/ProjectDetail.tsx

**Modified:**
- backend/app/routers/projects.py
- backend/tests/api/test_projects_api.py
- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/src/hooks/useLogout.ts
- frontend/src/pages/Projects.test.tsx
- frontend/src/pages/Projects.tsx
- _bmad-output/implementation-artifacts/2-2-view-project-details.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-01-22: Added project detail endpoint, UI, and tests for Story 2.2.
