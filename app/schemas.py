from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class ItemCreate(BaseModel):
    title: str
    description: str


class ItemOut(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    description: str
    status: str
    user_id: int
    start_date: datetime
    end_date: datetime
    jira_link: str
    created_by: int
    pull_requests_links: str
    priority: str


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    user_id: int
    start_date: datetime
    end_date: datetime
    jira_link: str
    created_by: int
    pull_requests_links: str
    priority: str
    username: str = ''

    class Config:
        from_attributes = True
