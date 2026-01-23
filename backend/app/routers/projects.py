from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.project import Project
from ..models.user import User
from ..schemas.project import (
    ProjectCreate,
    ProjectDataResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
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
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )
    return ProjectDataResponse(data=ProjectResponse.model_validate(project))


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
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )
    response_data = ProjectResponse.model_validate(project)
    db.delete(project)
    db.commit()
    return ProjectDataResponse(data=response_data)
