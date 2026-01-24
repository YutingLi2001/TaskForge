# Story 3.4: Delete Task

Status: done

## Story

As a **user**,
I want to **delete a task**,
So that **I can remove tasks I no longer need**.

## Acceptance Criteria

1. **Given** I have a task in my project **When** I click "Delete" and confirm **Then** the task is removed from the list
2. **Given** I click "Delete" and cancel **Then** the task is not deleted and no API call is made
3. **Given** I try to delete a task in a project I don't own **Then** the API returns 403 Forbidden
4. **Given** I try to delete a task that doesn't exist **Then** the API returns 404 Not Found
5. **Given** I am not authenticated **When** I try to delete a task **Then** the API returns 401 Unauthorized
6. **Given** I try to delete a task in a project that doesn't exist **Then** the API returns 404 Not Found
7. **Given** I delete a task that was already deleted **Then** the API returns 404 Not Found (idempotency)
8. **Given** I am deleting a task **Then** I cannot click delete again until the operation completes (double-click prevention)
9. **Given** I am deleting a task **Then** I cannot edit or toggle that task until the operation completes

## Tasks / Subtasks

**IMPORTANT: This story follows Test-Driven Development (TDD). Write all tests BEFORE implementing the functionality.**

### Phase 1: Backend Tests First (TDD)

- [x] **Task 1: Write Backend API Tests** (AC: 1, 3, 4, 5, 6, 7)
  - [x] Add test file structure to `backend/tests/api/test_tasks_api.py`
  - [x] Test: DELETE /projects/{pid}/tasks/{tid} returns 200 and removes task for owner
  - [x] Test: DELETE /projects/{pid}/tasks/{tid} returns 404 for non-existent task
  - [x] Test: DELETE /projects/{pid}/tasks/{tid} returns 404 for non-existent project
  - [x] Test: DELETE /projects/{pid}/tasks/{tid} returns 403 for project not owned by user
  - [x] Test: DELETE /projects/{pid}/tasks/{tid} returns 401 for unauthenticated request
  - [x] Test: DELETE /projects/{pid}/tasks/{tid} returns 404 when task doesn't belong to specified project
  - [x] Test: DELETE /projects/{pid}/tasks/{tid} returns 404 on second delete (already deleted - AC: 7)
  - [x] **Run tests - expect all to FAIL (RED phase)**

### Phase 2: Backend Implementation

- [x] **Task 2: Backend DELETE Endpoint** (AC: 1, 3, 4, 5, 6, 7)
  - [x] Add `DELETE /api/projects/{project_id}/tasks/{task_id}` endpoint to `backend/app/routers/tasks.py`
  - [x] Use `get_current_user` dependency for authentication
  - [x] Use existing `get_project_or_404` helper for project lookup and ownership check
  - [x] Query task by ID and verify it belongs to project, return 404 if not found
  - [x] Delete task and commit
  - [x] Return deleted task data with 200 (maintain JSON response for frontend parsing)
  - [x] **Run tests - expect all to PASS (GREEN phase)**

### Phase 3: Frontend Tests First (TDD)

- [x] **Task 3: Write Frontend API Client Tests** (AC: 1)
  - [x] Add tests to `frontend/src/api/client.test.ts` (if exists) or inline
  - [x] Test: tasksApi.delete calls correct endpoint with DELETE method
  - [x] **Run tests - expect to FAIL (RED phase)**

- [x] **Task 4: Write Frontend UI Tests** (AC: 1, 2, 8, 9)
  - [x] Add tests to `frontend/src/pages/ProjectDetail.test.tsx`
  - [x] Test: Delete button renders for each task
  - [x] Test: Clicking delete shows confirmation dialog
  - [x] Test: Confirming delete calls API and removes task from list
  - [x] Test: Cancelling delete does not call API and task remains
  - [x] Test: Delete button is disabled during delete operation (AC: 8)
  - [x] Test: Edit button is disabled during delete operation (AC: 9)
  - [x] Test: Toggle checkbox is disabled during delete operation (AC: 9)
  - [x] Test: 403 error shows error message
  - [x] Test: 404 error shows error message
  - [x] Test: 401 error triggers logout
  - [x] **Run tests - expect to FAIL (RED phase)**

### Phase 4: Frontend Implementation

- [x] **Task 5: Frontend API Client** (AC: 1)
  - [x] Add `delete(projectId: number, taskId: number)` method to `tasksApi` in `frontend/src/api/client.ts`
  - [x] Returns `ApiResponse<TaskData>`
  - [x] **Run API client tests - expect to PASS (GREEN phase)**

- [x] **Task 6: Delete UI for Tasks in ProjectDetail** (AC: 1, 2, 8, 9)
  - [x] Update `frontend/src/pages/ProjectDetail.tsx`
  - [x] Add "Delete" button to each task item
  - [x] Add `deletingTaskId` state to track which task is being deleted
  - [x] Show confirmation dialog (window.confirm) before delete
  - [x] If cancelled, do nothing (no API call)
  - [x] If confirmed, call `tasksApi.delete()` and remove task from local state on success
  - [x] Disable delete button during operation (double-click prevention)
  - [x] Disable edit and toggle for task being deleted
  - [x] Handle 401 (logout), 403/404 (show error message)
  - [x] Style delete button with destructive styling (red text/border)
  - [x] **Run UI tests - expect all to PASS (GREEN phase)**

### Phase 5: Refactor & Full Test Suite

- [x] **Task 7: Refactor and Final Validation**
  - [x] Review code for any cleanup opportunities
  - [x] Run full backend test suite: `scripts/windows/run-backend-tests.ps1`
  - [x] Run full frontend test suite: `scripts/windows/run-frontend-tests.ps1`
  - [x] Run linters: `npm run lint`
  - [x] All tests pass, no lint errors

## Dev Notes

### Architecture Compliance

**Backend Structure:**
- Endpoint: `backend/app/routers/tasks.py` (add DELETE endpoint)
- Tests: `backend/tests/api/test_tasks_api.py` (add delete tests)

**Frontend Structure:**
- API: `frontend/src/api/client.ts` (add delete method to tasksApi)
- Page: `frontend/src/pages/ProjectDetail.tsx` (add delete UI)
- Tests: `frontend/src/pages/ProjectDetail.test.tsx` (add delete tests)

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| Authentication | `get_current_user` dependency |
| Authorization | Verify project ownership via `get_project_or_404` helper |
| Nested Routes | `DELETE /api/projects/{project_id}/tasks/{task_id}` |
| Response Format | Return JSON body `{ "data": {...} }` for frontend parsing |
| Confirmation | `window.confirm` before delete |
| Double-click Prevention | Disable delete button while `deletingTaskId` is set |
| Idempotency | Return 404 for already-deleted tasks |

### API Endpoint Spec

**DELETE /api/projects/{project_id}/tasks/{task_id}** (Protected)

Request Headers:
```
Authorization: Bearer <access_token>
```

Success Response (200):
```json
{
  "data": {
    "id": 1,
    "title": "Deleted Task",
    "is_complete": false,
    "project_id": 1,
    "created_at": "2026-01-23T00:00:00Z",
    "updated_at": "2026-01-24T12:00:00Z"
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

Error Response (404 - project not found):
```json
{
  "detail": "Project not found"
}
```

Error Response (404 - task not found):
```json
{
  "detail": "Task not found"
}
```

### TDD Test Specifications

**Backend Tests (Write First):**
```python
# test_tasks_api.py - Add these tests BEFORE implementing delete endpoint

class TasksApiTests(IsolatedAsyncioTestCase):
    # ... existing tests ...

    async def test_delete_task_returns_200_and_removes_task(self):
        """DELETE /projects/{pid}/tasks/{tid} deletes task for owner."""
        # Create user, project, task
        # Call DELETE endpoint
        # Assert 200 response with task data
        # Assert task no longer exists in DB

    async def test_delete_task_returns_404_for_nonexistent_task(self):
        """DELETE /projects/{pid}/tasks/{tid} returns 404 for missing task."""
        # Create user, project (no task)
        # Call DELETE with non-existent task_id
        # Assert 404 response

    async def test_delete_task_returns_404_for_nonexistent_project(self):
        """DELETE /projects/{pid}/tasks/{tid} returns 404 for missing project."""
        # Create user (no project)
        # Call DELETE with non-existent project_id
        # Assert 404 response

    async def test_delete_task_returns_403_for_non_owner(self):
        """DELETE /projects/{pid}/tasks/{tid} returns 403 for non-owner."""
        # Create owner user with project and task
        # Create other user
        # Call DELETE as other user
        # Assert 403 response

    async def test_delete_task_returns_401_for_unauthenticated(self):
        """DELETE /projects/{pid}/tasks/{tid} returns 401 without auth."""
        # Create project and task
        # Call DELETE without auth header
        # Assert 401 response

    async def test_delete_task_returns_404_when_task_not_in_project(self):
        """DELETE /projects/{pid}/tasks/{tid} returns 404 for cross-project access."""
        # Create user with two projects
        # Create task in project 1
        # Call DELETE with project 2 ID and task from project 1
        # Assert 404 response

    async def test_delete_task_returns_404_on_second_delete(self):
        """DELETE /projects/{pid}/tasks/{tid} returns 404 for already deleted task."""
        # Create user, project, task
        # Call DELETE first time - expect 200
        # Call DELETE second time - expect 404
```

**Frontend Tests (Write First):**
```typescript
// ProjectDetail.test.tsx - Add these tests BEFORE implementing delete UI

describe('Task Delete', () => {
  it('renders delete button for each task', async () => {
    // Render ProjectDetail with tasks
    // Assert delete button exists for each task
  });

  it('shows confirmation dialog when delete clicked', async () => {
    // Mock window.confirm
    // Click delete button
    // Assert confirm was called
  });

  it('calls API and removes task on confirm', async () => {
    // Mock window.confirm to return true
    // Mock tasksApi.delete
    // Click delete button
    // Assert API called with correct IDs
    // Assert task removed from UI
  });

  it('does not call API on cancel', async () => {
    // Mock window.confirm to return false
    // Mock tasksApi.delete
    // Click delete button
    // Assert API NOT called
    // Assert task still in UI
  });

  it('disables delete button during delete operation', async () => {
    // Mock slow API response
    // Click delete button
    // Assert delete button is disabled
  });

  it('disables edit button during delete operation', async () => {
    // Mock slow API response
    // Click delete button
    // Assert edit button is disabled for that task
  });

  it('disables toggle checkbox during delete operation', async () => {
    // Mock slow API response
    // Click delete button
    // Assert toggle checkbox is disabled for that task
  });

  it('shows error message on 403', async () => {
    // Mock tasksApi.delete to throw 403
    // Click delete and confirm
    // Assert error message shown
  });

  it('shows error message on 404', async () => {
    // Mock tasksApi.delete to throw 404
    // Click delete and confirm
    // Assert error message shown
  });

  it('triggers logout on 401', async () => {
    // Mock tasksApi.delete to throw 401
    // Mock logout
    // Click delete and confirm
    // Assert logout was called
  });
});
```

### Component Specifications

**Backend DELETE Endpoint:**
```python
@router.delete("/{task_id}", response_model=TaskDataResponse)
async def delete_task(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_or_404(project_id, current_user, db)
    task = await db.scalar(
        select(Task).where(Task.id == task_id, Task.project_id == project.id)
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Capture task data before deletion for response
    task_response = TaskResponse.model_validate(task)

    await db.delete(task)
    await db.commit()

    return TaskDataResponse(data=task_response)
```

**Frontend tasksApi delete:**
```typescript
export const tasksApi = {
  list: (projectId: number) =>
    api.get<ApiResponse<TaskData[]>>(`/projects/${projectId}/tasks`),
  create: (projectId: number, data: CreateTaskData) =>
    api.post<ApiResponse<TaskData>>(`/projects/${projectId}/tasks`, data),
  update: (projectId: number, taskId: number, data: UpdateTaskData) =>
    api.put<ApiResponse<TaskData>>(
      `/projects/${projectId}/tasks/${taskId}`,
      data
    ),
  toggleStatus: (projectId: number, taskId: number, data: ToggleTaskStatusData) =>
    api.patch<ApiResponse<TaskData>>(
      `/projects/${projectId}/tasks/${taskId}`,
      data
    ),
  delete: (projectId: number, taskId: number) =>
    api.delete<ApiResponse<TaskData>>(
      `/projects/${projectId}/tasks/${taskId}`
    ),
};
```

**ProjectDetail.tsx Delete Pattern:**
```tsx
// Add to existing state
const [deletingTaskId, setDeletingTaskId] = useState<number | null>(null);

const handleDeleteTask = async (task: TaskData) => {
  // Set deleting state BEFORE confirm to prevent double-click
  setDeletingTaskId(task.id);

  const confirmed = window.confirm(`Delete task "${task.title}"?`);
  if (!confirmed) {
    setDeletingTaskId(null);
    return;
  }

  try {
    await tasksApi.delete(project!.id, task.id);
    setTasks(tasks.filter(t => t.id !== task.id));
    setTaskError(null);
  } catch (err) {
    if (err instanceof ApiRequestError) {
      if (err.status === 401) {
        logout();
        return;
      }
      if (err.status === 403) {
        setTaskError('You do not have permission to delete this task.');
        return;
      }
      if (err.status === 404) {
        setTaskError('Task not found.');
        return;
      }
    }
    setTaskError(err instanceof Error ? err.message : 'Failed to delete task');
  } finally {
    setDeletingTaskId(null);
  }
};

// In render - Task item with delete button:
{tasks.map((task) => {
  const isDeleting = deletingTaskId === task.id;
  const isToggling = togglingTaskId === task.id;
  const isEditing = editingTaskId === task.id;
  const isDisabled = isDeleting || isToggling;

  return (
    <li key={task.id} className="flex items-center gap-3 rounded-md border border-gray-200 px-4 py-3">
      {isEditing ? (
        // ... existing edit mode UI ...
      ) : (
        <>
          <button
            onClick={() => handleToggleTask(task)}
            disabled={isDisabled}
            className="..."
            aria-label={task.is_complete ? 'Mark as incomplete' : 'Mark as complete'}
          >
            {/* checkbox UI */}
          </button>
          <span className={`flex-1 ${task.is_complete ? 'text-gray-500 line-through' : 'text-gray-900'}`}>
            {task.title}
          </span>
          <button
            onClick={() => handleEditTask(task)}
            disabled={isDisabled}
            className="text-sm text-blue-600 hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Edit
          </button>
          <button
            onClick={() => handleDeleteTask(task)}
            disabled={isDisabled}
            className="text-sm text-red-600 hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Delete
          </button>
        </>
      )}
    </li>
  );
})}
```

### References

**Planning Documents:**
- [PRD: FR14](../planning-artifacts/prd.md)
- [Architecture: Task Structure](../planning-artifacts/architecture.md)
- [Epics: Story 3.4](../planning-artifacts/epics.md#Story-3.4-Delete-Task)

**Source: Story 2.4 Delete Project (Follow This Pattern!)**
- [2-4-delete-project.md](./2-4-delete-project.md) - Delete operation patterns
- Confirmation flow with `window.confirm`
- Double-click prevention with state
- Idempotency (404 on second delete)
- Disabling related actions during delete

**Source: Story 3.1-3.3 Implementation**
- [backend/app/routers/tasks.py](../../backend/app/routers/tasks.py) - Add DELETE endpoint here
- [backend/tests/api/test_tasks_api.py](../../backend/tests/api/test_tasks_api.py) - Add delete tests here
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - Add delete method here
- [frontend/src/pages/ProjectDetail.tsx](../../frontend/src/pages/ProjectDetail.tsx) - Add delete UI here
- [frontend/src/pages/ProjectDetail.test.tsx](../../frontend/src/pages/ProjectDetail.test.tsx) - Add delete tests here

### Key Learnings from Previous Stories to Apply

1. **TDD approach** - Write tests FIRST, then implement (from Epic 2 retro)
2. **Delete edge cases** - Confirmation, idempotency, double-click prevention (from Epic 2 retro action item #1)
3. **Consistent error handling** - Use `ApiRequestError` pattern for 401/403/404 (from Story 3.1-3.3)
4. **Disable related actions** - Disable edit/toggle during delete operation (from Story 2.4)
5. **Set state before confirm** - Prevent double-click by setting `deletingTaskId` before `window.confirm` (from Story 2.4)
6. **Reuse `get_project_or_404`** - Already exists in tasks.py router

### Epic 2 Retrospective Action Items Applied

1. **Explicitly spec delete operation edge cases** ✅ Applied
   - Confirmation flow (AC: 1, 2)
   - Idempotency - 404 on second delete (AC: 7)
   - Double-click prevention (AC: 8)
   - Disable related actions during delete (AC: 9)
2. **Continue spec-driven + TDD approach** ✅ Applied
   - Tests written in Phase 1 and 3 BEFORE implementation in Phase 2 and 4

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Implementation Plan

**TDD Workflow:**
1. **RED** - Write backend delete tests (all should fail)
2. **GREEN** - Implement backend delete endpoint (tests pass)
3. **RED** - Write frontend tests (all should fail)
4. **GREEN** - Implement frontend delete method and UI (tests pass)
5. **REFACTOR** - Review, cleanup, run full test suite

### Completion Notes List

- Added backend delete tests for tasks covering success and error cases.
- Implemented DELETE task endpoint with ownership checks and idempotent 404.
- Tests: `scripts/windows/run-backend-tests.ps1`.
- Added frontend delete API client test and method.
- Added delete UI tests and implemented task delete flow with confirmation and disabled actions.
- Tests: `scripts/windows/run-frontend-tests.ps1`.
- Tests: `scripts/windows/run-backend-tests.ps1`, `scripts/windows/run-frontend-tests.ps1`, `npm run lint`.
- Code review fixes: clear edit mode when delete starts; simplify task row rendering logic.
- Tests: `scripts/windows/run-frontend-tests.ps1` (2026-01-24).

### File List

**Modified:**
- backend/app/routers/tasks.py
- backend/tests/api/test_tasks_api.py
- frontend/src/api/client.test.ts
- frontend/src/api/client.ts
- frontend/src/pages/ProjectDetail.test.tsx
- frontend/src/pages/ProjectDetail.tsx
- _bmad-output/implementation-artifacts/3-4-delete-task.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-01-24: Story created with ready-for-dev status, TDD emphasis, and Epic 2 retro action items applied.
- 2026-01-24: Implemented task deletion with backend and frontend tests; status set to review.
- 2026-01-24: Code review fixes applied (delete/edit state guard, render cleanup).
