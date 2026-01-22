from fastapi import APIRouter, Depends, status
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
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    return ProjectListResponse(data=projects)


@router.post("", response_model=ProjectDataResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = Project(name=project_data.name, user_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectDataResponse(data=ProjectResponse.model_validate(project))
