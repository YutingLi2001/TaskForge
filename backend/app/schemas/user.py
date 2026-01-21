from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    @field_validator("email", mode="before")
    def normalize_email(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


class UserDataResponse(BaseModel):
    data: UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    remember_me: bool = False

    @field_validator("email", mode="before")
    def normalize_email(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


class LoginDataResponse(BaseModel):
    data: LoginResponse


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshDataResponse(BaseModel):
    data: RefreshResponse


class UserPublicResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserPublicDataResponse(BaseModel):
    data: UserPublicResponse
