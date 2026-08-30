"""
Database models (SQLModel table=True) and request/response schemas
(SQLModel table=False, behaving like plain Pydantic models).
"""
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = False


class UserCreate(SQLModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)


class UserRead(SQLModel):
    id: int
    username: str
    is_admin: bool


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=3)
    power: str = Field(min_length=3)
    level: int = Field(default=1, ge=1, le=100)
    active: bool = True


class HeroCreate(SQLModel):
    name: str = Field(min_length=3)
    power: str = Field(min_length=3)
    level: int = Field(default=1, ge=1, le=100)
    active: bool = True


class HeroUpdate(SQLModel):
    """All fields optional -> supports PATCH with exclude_unset=True."""
    name: str | None = Field(default=None, min_length=3)
    power: str | None = Field(default=None, min_length=3)
    level: int | None = Field(default=None, ge=1, le=100)
    active: bool | None = None


class HeroRead(SQLModel):
    id: int
    name: str
    power: str
    level: int
    active: bool


class Mission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = False
    hero_id: int = Field(foreign_key="hero.id")


class MissionCreate(SQLModel):
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = False
    hero_id: int


class MissionUpdate(SQLModel):
    """All fields optional -> supports PATCH with exclude_unset=True."""
    title: str | None = Field(default=None, min_length=5)
    difficulty: int | None = Field(default=None, ge=1, le=10)
    completed: bool | None = None
    hero_id: int | None = None


class MissionRead(SQLModel):
    id: int
    title: str
    difficulty: int
    completed: bool
    hero_id: int
