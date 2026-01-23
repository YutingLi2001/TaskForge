# Story 2.3: Edit Project

Status: review

## Story

As a **user**,
I want to **edit my project's name**,
So that **I can rename it**.

## Acceptance Criteria

1. **Given** I am viewing my project **When** I click an "Edit" button **Then** I can edit the project name inline or in a form
2. **Given** I am editing a project name **When** I submit a valid new name **Then** the change is persisted and the UI updates
3. **Given** I am editing a project name **When** I submit an empty name **Then** I see a validation error
4. **Given** I try to edit a project I don't own **Then** the API returns 403 Forbidden
5. **Given** I try to edit a project that doesn't exist **Then** the API returns 404 Not Found
6. **Given** I am not authenticated **When** I try to edit a project **Then** the API returns 401 Unauthorized
7. **Given** I am editing **When** I click "Cancel" **Then** the edit is discarded and the original name is shown

## Tasks / Subtasks

- [x] **Task 1: Backend ProjectUpdate Schema** (AC: 2, 3)
  - [x] Add `ProjectUpdate` schema to `backend/app/schemas/project.py`
  - [x] Use same validation as `ProjectCreate` (name: str, min_length=1, strip whitespace)
  - [x] Export from `backend/app/schemas/__init__.py`

- [x] **Task 2: Backend PUT Endpoint** (AC: 2, 3, 4, 5, 6)
  - [x] Add `PUT /api/projects/{project_id}` endpoint to `backend/app/routers/projects.py`
  - [x] Use `get_current_user` dependency for authentication
  - [x] Query project by ID, return 404 if not found
  - [x] Check ownership, return 403 if not owner
  - [x] Update project name and `updated_at` timestamp
  - [x] Return updated project data with 200

- [x] **Task 3: Backend Testing** (AC: 2, 3, 4, 5, 6)
  - [x] Add tests to `backend/tests/api/test_projects_api.py`
  - [x] Test: PUT /projects/{id} updates name and returns updated project
  - [x] Test: PUT /projects/{id} with empty name returns 422
  - [x] Test: PUT /projects/{id} returns 404 for non-existent project
  - [x] Test: PUT /projects/{id} returns 403 for non-owner
  - [x] Test: PUT /projects/{id} returns 401 for unauthenticated request
  - [x] Test: whitespace-only name returns 422

- [x] **Task 4: Frontend API Client** (AC: 2)
  - [x] Add `UpdateProjectData` interface to `frontend/src/api/client.ts`
  - [x] Add `update(id: number, data: UpdateProjectData)` method to `projectsApi`
  - [x] Returns `ApiResponse<ProjectData>`

- [x] **Task 5: Edit UI in ProjectDetail** (AC: 1, 2, 3, 7)
  - [x] Add edit mode state to `frontend/src/pages/ProjectDetail.tsx`
  - [x] Add "Edit" button that toggles edit mode
  - [x] Show input field with current name when in edit mode
  - [x] Add "Save" and "Cancel" buttons in edit mode
  - [x] Call `projectsApi.update()` on save
  - [x] Show validation error for empty name
  - [x] Update local project state on successful save
  - [x] Handle 403/404 errors gracefully
  - [x] Style with Tailwind CSS matching existing design

- [x] **Task 6: Frontend Testing** (AC: 1, 2, 3, 7)
  - [x] Update `frontend/src/pages/ProjectDetail.test.tsx`
  - [x] Test: Edit button toggles edit mode
  - [x] Test: Save submits update and shows new name
  - [x] Test: Empty name shows validation error
  - [x] Test: Cancel discards changes and exits edit mode

## Dev Notes

### Architecture Compliance

**Backend Structure:**
- Schema: `backend/app/schemas/project.py` (add ProjectUpdate)
- Endpoint: `backend/app/routers/projects.py` (add PUT endpoint)
- Tests: `backend/tests/api/test_projects_api.py` (add update tests)

**Frontend Structure:**
- Page: `frontend/src/pages/ProjectDetail.tsx` (add edit functionality)
- API: `frontend/src/api/client.ts` (add update method)
- Tests: `frontend/src/pages/ProjectDetail.test.tsx` (add edit tests)

### Technical Requirements

| Requirement | Implementation |
|-------------|----------------|
| Authentication | `get_current_user` dependency |
| Authorization | Check `project.user_id == current_user.id` |
| Validation | Pydantic schema with min_length, strip whitespace |
| HTTP Method | PUT for full resource update |
| Timestamp | Auto-update `updated_at` on save |

### API Endpoint Spec

**PUT /api/projects/{project_id}** (Protected)

Request Headers:
```
Authorization: Bearer <access_token>
```

Request Body:
```json
{
  "name": "Updated Project Name"
}
```

Success Response (200):
```json
{
  "data": {
    "id": 1,
    "name": "Updated Project Name",
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

Validation Error (422 - empty name):
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```

### Component Specifications

**ProjectUpdate Schema:**
```python
class ProjectUpdate(BaseModel):
    name: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Project name cannot be blank")
        return trimmed
```

**Backend PUT Endpoint:**
```python
@router.put("/{project_id}", response_model=ProjectDataResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )
    project.name = project_data.name
    db.commit()
    db.refresh(project)
    return ProjectDataResponse(data=ProjectResponse.model_validate(project))
```

**Frontend projectsApi update:**
```typescript
export interface UpdateProjectData {
  name: string;
}

export const projectsApi = {
  list: () => api.get<ApiResponse<ProjectData[]>>('/projects'),
  create: (data: CreateProjectData) =>
    api.post<ApiResponse<ProjectData>>('/projects', data),
  get: (id: number) => api.get<ApiResponse<ProjectData>>(`/projects/${id}`),
  update: (id: number, data: UpdateProjectData) =>
    api.put<ApiResponse<ProjectData>>(`/projects/${id}`, data),
};
```

**ProjectDetail Edit Mode Pattern:**
```tsx
const [isEditing, setIsEditing] = useState(false);
const [editName, setEditName] = useState('');
const [editError, setEditError] = useState<string | null>(null);
const [saving, setSaving] = useState(false);

const handleEdit = () => {
  setEditName(project?.name ?? '');
  setEditError(null);
  setIsEditing(true);
};

const handleCancel = () => {
  setIsEditing(false);
  setEditError(null);
};

const handleSave = async () => {
  const trimmed = editName.trim();
  if (!trimmed) {
    setEditError('Project name is required.');
    return;
  }
  setSaving(true);
  try {
    const response = await projectsApi.update(project!.id, { name: trimmed });
    setProject(response.data);
    setIsEditing(false);
  } catch (err) {
    // Handle errors...
  } finally {
    setSaving(false);
  }
};

// In render:
{isEditing ? (
  <div>
    <input value={editName} onChange={(e) => setEditName(e.target.value)} />
    {editError && <p className="text-red-600">{editError}</p>}
    <button onClick={handleSave} disabled={saving}>Save</button>
    <button onClick={handleCancel}>Cancel</button>
  </div>
) : (
  <div>
    <h1>{project.name}</h1>
    <button onClick={handleEdit}>Edit</button>
  </div>
)}
```

### References

**Planning Documents:**
- [PRD: FR8](../planning-artifacts/prd.md)
- [Architecture: Project Structure](../planning-artifacts/architecture.md)
- [Epics: Story 2.3](../planning-artifacts/epics.md#Story-2.3-Edit-Project)

**Source: Story 2-1 and 2-2 Implementation**
- [backend/app/routers/projects.py](../../backend/app/routers/projects.py) - Add PUT endpoint here
- [backend/app/schemas/project.py](../../backend/app/schemas/project.py) - Add ProjectUpdate schema
- [frontend/src/api/client.ts](../../frontend/src/api/client.ts) - Add update method
- [frontend/src/pages/ProjectDetail.tsx](../../frontend/src/pages/ProjectDetail.tsx) - Add edit UI

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5

### Implementation Plan

- Add ProjectUpdate schema with same validation as ProjectCreate
- Implement PUT /api/projects/{id} endpoint with ownership checks
- Write backend tests first (TDD), then implement endpoint
- Add update method to frontend projectsApi
- Write frontend tests for edit UI
- Implement edit mode in ProjectDetail with Save/Cancel buttons

### Completion Notes List

- Added ProjectUpdate schema to backend/app/schemas/project.py with whitespace trimming
- Implemented PUT /api/projects/{id} endpoint with 401/403/404 handling
- Added 6 backend tests for update functionality (success, empty name, whitespace, 404, 403, 401)
- Added UpdateProjectData interface and update method to frontend API client
- Implemented edit mode UI in ProjectDetail with inline editing
- Added 5 frontend tests for edit functionality
- Tests: `scripts/windows/run-backend-tests.ps1` (pass), `scripts/windows/run-frontend-tests.ps1` (pass)

### File List

**Modified:**
- backend/app/schemas/project.py
- backend/app/schemas/__init__.py
- backend/app/routers/projects.py
- backend/tests/api/test_projects_api.py
- frontend/src/api/client.ts
- frontend/src/pages/ProjectDetail.tsx
- frontend/src/pages/ProjectDetail.test.tsx

### Change Log

- 2026-01-22: Implemented Story 2.3 - Edit Project with TDD approach
