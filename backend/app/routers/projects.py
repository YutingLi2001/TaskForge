from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.project import Project
from ..models.user import User
from ..schemas.project import (
    ProjectCreate,
    ProjectDataResponse,
    ProjectListResponse,
    ProjectResponse,
)
from ..utils.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    def _load_projects() -> list[Project]:
        return (
            db.query(Project)
            .filter(Project.user_id == current_user.id)
            .all()
        )

    projects = await run_in_threadpool(_load_projects)
    return ProjectListResponse(data=projects)


@router.post("", response_model=ProjectDataResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    def _create_project() -> ProjectResponse:
        project = Project(name=project_data.name, user_id=current_user.id)
        db.add(project)
        db.commit()
        db.refresh(project)
        return ProjectResponse.model_validate(project)

    project = await run_in_threadpool(_create_project)
    return ProjectDataResponse(data=project)
