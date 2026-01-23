# Story 2.4: Delete Project

Status: done

## Story

As a **user**,
I want to **delete a project**,
So that **I can remove projects I no longer need**.

## Acceptance Criteria

1. **Given** I own a project **When** I click "Delete" and confirm **Then** the project is deleted and I am returned to the projects list
2. **Given** I delete a project **Then** it is removed from my project list
3. **Given** I click "Delete" and cancel **Then** the project is not deleted and no API call is made
4. **Given** I try to delete a project I don't own **Then** the API returns 403 Forbidden
5. **Given** I try to delete a project that doesn't exist **Then** the API returns 404 Not Found
6. **Given** I am not authenticated **When** I try to delete a project **Then** the API returns 401 Unauthorized
7. **Given** I am viewing a project **Then** I see a confirmation step before deletion
8. **Given** I delete a project that was already deleted **Then** the API returns 404 Not Found

## Tasks / Subtasks

- [x] **Task 1: Backend DELETE Endpoint** (AC: 1, 4, 5, 6)
  - [x] Add `DELETE /api/projects/{project_id}` endpoint to `backend/app/routers/projects.py`
  - [x] Use `get_current_user` dependency for authentication
  - [x] Query project by ID, return 404 if not found
  - [x] Check ownership, return 403 if not owner
  - [x] Delete project and commit
  - [x] Return a JSON response body (keep `ApiResponse` parsing intact in frontend)

- [x] **Task 2: Backend Testing** (AC: 1, 4, 5, 6)
  - [x] Add tests to `backend/tests/api/test_projects_api.py`
  - [x] Test: DELETE /projects/{id} deletes project for owner
  - [x] Test: DELETE /projects/{id} returns 404 for non-existent project
  - [x] Test: DELETE /projects/{id} returns 404 for already deleted project (AC: 8)
  - [x] Test: DELETE /projects/{id} returns 403 for non-owner
  - [x] Test: DELETE /projects/{id} returns 401 for unauthenticated request

- [x] **Task 3: Frontend API Client** (AC: 1, 2)
  - [x] Add `delete(id: number)` method to `projectsApi` in `frontend/src/api/client.ts`
  - [x] Return `ApiResponse<ProjectData>` (or equivalent JSON) to match API response

- [x] **Task 4: Delete UI in ProjectDetail** (AC: 1, 2, 3, 7)
  - [x] Add "Delete" button to `frontend/src/pages/ProjectDetail.tsx`
  - [x] Prompt for confirmation (simple `window.confirm` is acceptable)
  - [x] If confirmed, call `projectsApi.delete(project.id)`
  - [x] On success, navigate to `/projects` (list reload removes deleted project)
  - [x] If cancelled, do nothing
  - [x] Handle 401 by logging out, 403/404 by showing an error message
  - [x] Style delete button with destructive styling consistent with existing UI

- [x] **Task 5: Frontend Testing** (AC: 1, 2, 3, 7)
  - [x] Update `frontend/src/pages/ProjectDetail.test.tsx`
  - [x] Test: Delete button renders for project
  - [x] Test: Confirm delete calls API and navigates to /projects
  - [x] Test: Cancel delete does not call API
  - [x] Test: 403/404 delete shows error message

## Dev Notes

### Architecture Compliance

**Backend Structure:**
- Endpoint: `backend/app/routers/projects.py` (add to existing file)
- Tests: `backend/tests/api/test_projects_api.py` (add to existing file)

**Frontend Structure:**
- API: `frontend/src/api/client.ts` (add delete method to projectsApi)
- Page: `frontend/src/pages/ProjectDetail.tsx` (add delete UI)
- Tests: `frontend/src/pages/ProjectDetail.test.tsx` (add delete tests)

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| Authentication | `get_current_user` dependency |
| Authorization | Check `project.user_id == current_user.id` |
| 403 Response | `HTTPException(status_code=403, detail="Not authorized to access this project")` |
| 404 Response | `HTTPException(status_code=404, detail="Project not found")` |
| Response Format | Must return JSON body (frontend `api.delete` parses JSON) |
| Confirmation | `window.confirm` or simple inline confirmation step |

### API Endpoint Spec

**DELETE /api/projects/{project_id}** (Protected)

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
    "updated_at": "2026-01-22T12:00:00Z"
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

**Backend DELETE Endpoint:**
```python
@router.delete("/{project_id}", response_model=ProjectDataResponse)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    db.delete(project)
    db.commit()
    return ProjectDataResponse(data=ProjectResponse.model_validate(project))
```

**Frontend projectsApi delete:**
```typescript
export const projectsApi = {
  list: () => api.get<ApiResponse<ProjectData[]>>('/projects'),
  create: (data: CreateProjectData) =>
    api.post<ApiResponse<ProjectData>>('/projects', data),
  get: (id: number) => api.get<ApiResponse<ProjectData>>(`/projects/${id}`),
  update: (id: number, data: UpdateProjectData) =>
    api.put<ApiResponse<ProjectData>>(`/projects/${id}`, data),
  delete: (id: number) => api.delete<ApiResponse<ProjectData>>(`/projects/${id}`),
};
```

**ProjectDetail delete flow:**
```tsx
const handleDelete = async () => {
  if (!project) return;
  const confirmed = window.confirm('Delete this project?');
  if (!confirmed) return;

  try {
    await projectsApi.delete(project.id);
    navigate('/projects');
  } catch (err) {
    if (err instanceof ApiRequestError) {
      if (err.status === 401) {
        logout();
        return;
      }
      if (err.status === 403) {
        setError('You do not have permission to delete this project.');
        return;
      }
      if (err.status === 404) {
        setError('Project not found.');
        return;
      }
    }
    setError(err instanceof Error ? err.message : 'Failed to delete project');
  }
};
```

### References

**Planning Documents:**
- [PRD: FR9](../planning-artifacts/prd.md)
- [Architecture: Project Structure](../planning-artifacts/architecture.md)
- [Epics: Story 2.4](../planning-artifacts/epics.md#Story-2.4-Delete-Project)

**Source: Story 2-3 Implementation Patterns**
- [backend/app/routers/projects.py](../../backend/app/routers/projects.py) - Add DELETE endpoint here
- [backend/tests/api/test_projects_api.py](../../backend/tests/api/test_projects_api.py) - Add delete tests here
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - Add delete method here
- [frontend/src/pages/ProjectDetail.tsx](../../frontend/src/pages/ProjectDetail.tsx) - Add delete UI here
- [frontend/src/pages/ProjectDetail.test.tsx](../../frontend/src/pages/ProjectDetail.test.tsx) - Add delete tests here

## Dev Agent Record

### Agent Model Used

GPT-5 (Codex CLI)

### Implementation Plan

- Add backend DELETE endpoint with ownership checks and JSON response.
- Add backend tests for delete scenarios (owner, 401, 403, 404).
- Add frontend projectsApi delete method.
- Add delete flow UI with confirmation and error handling.
- Add frontend tests for delete flow and navigation.

### Debug Log References

- logs/backend-tests-20260122-230346.log
- logs/frontend-tests-20260122-230401.log

### Completion Notes List

- Added DELETE /api/projects/{id} with 401/403/404 handling and JSON response.
- Added backend delete tests (owner success, 401, 403, 404) with response body assertions and delete-twice 404 behavior.
- Added projectsApi.delete and delete button flow with confirm + navigation, plus delete-in-progress UI state.
- Added delete UI error handling and destructive button styling, with error reset on success and edit disabled during delete.
- Added frontend delete tests for confirm/cancel and error states, including 401 logout, deleting state, and no-navigation on failure.
- Prevented delete re-entry during confirmation by setting deleting state pre-confirm.
- Documented AC8 in tasks and aligned test naming.
- Tests: scripts/windows/run-backend-tests.ps1, scripts/windows/run-frontend-tests.ps1 (pass).

### File List

**Modified:**
- backend/app/routers/projects.py
- backend/tests/api/test_projects_api.py
- frontend/src/api/client.ts
- frontend/src/pages/ProjectDetail.tsx
- frontend/src/pages/ProjectDetail.test.tsx
- _bmad-output/implementation-artifacts/2-4-delete-project.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-01-23: Implemented Story 2.4 delete project endpoint, UI, tests, and updated sprint status.
- 2026-01-23: Code review fixes: safe delete response serialization, delete loading state, 401 delete test.
- 2026-01-23: Final review fixes: async delete handler, delete response assertions, delete loading test.
- 2026-01-23: Final-final review fixes: keep delete endpoint sync, stabilize delete loading test, clear delete error on success.
- 2026-01-23: Review loop fixes: disable edit during delete, add delete-twice 404 test, assert no navigation on delete errors.
- 2026-01-23: Review loop fixes: prevent delete re-entry during confirmation, document delete-twice 404 AC.
- 2026-01-23: Review loop fixes: align AC8 task and test name.
