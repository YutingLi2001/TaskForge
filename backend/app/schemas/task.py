from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title", mode="before")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Task title must be a string")
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Task title cannot be blank")
        return trimmed


class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title", mode="before")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Task title must be a string")
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Task title cannot be blank")
        return trimmed


class TaskStatusUpdate(BaseModel):
    is_complete: bool


class TaskResponse(BaseModel):
    id: int
    title: str
    is_complete: bool
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    data: list[TaskResponse]


class TaskDataResponse(BaseModel):
    data: TaskResponse
