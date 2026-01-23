from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.scalars(
        select(Project).where(Project.user_id == current_user.id)
    )
    projects = result.all()
    return ProjectListResponse(data=projects)


@router.post("", response_model=ProjectDataResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = Project(name=project_data.name, user_id=current_user.id)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectDataResponse(data=ProjectResponse.model_validate(project))


@router.get("/{project_id}", response_model=ProjectDataResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )
    return ProjectDataResponse(data=ProjectResponse.model_validate(project))


@router.put("/{project_id}", response_model=ProjectDataResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )
    project.name = project_data.name
    await db.commit()
    await db.refresh(project)
    return ProjectDataResponse(data=ProjectResponse.model_validate(project))


@router.delete("/{project_id}", response_model=ProjectDataResponse)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )
    response_data = ProjectResponse.model_validate(project)
    await db.delete(project)
    await db.commit()
    return ProjectDataResponse(data=response_data)
