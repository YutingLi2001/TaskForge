from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.project import Project
from ..models.task import Task
from ..models.user import User
from ..schemas.task import (
    TaskCreate,
    TaskDataResponse,
    TaskListResponse,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from ..utils.auth import get_current_user

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


async def get_project_or_404(
    project_id: int, current_user: User, db: AsyncSession
) -> Project:
    project = await db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )
    return project


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_or_404(project_id, current_user, db)
    result = await db.scalars(
        select(Task)
        .where(Task.project_id == project.id)
        .order_by(Task.created_at.asc(), Task.id.asc())
    )
    tasks = result.all()
    return TaskListResponse(data=[TaskResponse.model_validate(task) for task in tasks])


@router.post("", response_model=TaskDataResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_or_404(project_id, current_user, db)
    task = Task(title=task_data.title, project_id=project.id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskDataResponse(data=TaskResponse.model_validate(task))


@router.put("/{task_id}", response_model=TaskDataResponse)
async def update_task(
    project_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_or_404(project_id, current_user, db)
    task = await db.scalar(select(Task).where(Task.id == task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.project_id != project.id:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = task_data.title
    task.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return TaskDataResponse(data=TaskResponse.model_validate(task))


@router.patch("/{task_id}", response_model=TaskDataResponse)
async def toggle_task_status(
    project_id: int,
    task_id: int,
    task_data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_or_404(project_id, current_user, db)
    task = await db.scalar(
        select(Task).where(Task.id == task_id, Task.project_id == project.id)
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_complete = task_data.is_complete
    task.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return TaskDataResponse(data=TaskResponse.model_validate(task))


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

    task_response = TaskResponse.model_validate(task)

    await db.delete(task)
    await db.commit()

    return TaskDataResponse(data=task_response)
