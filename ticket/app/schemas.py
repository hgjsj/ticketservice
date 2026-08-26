from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuthenticatedUser(BaseModel):
    id: int
    username: str
    phone_number: str | None = None
    department: str | None = None


class TicketBase(BaseModel):
    title: str
    description: str
    priority: str = "medium"


class TicketCreate(TicketBase):
    assignee_id: int | None = None


class TicketUpdateStatus(BaseModel):
    status: str


class TicketRead(TicketBase):
    id: int
    status: str
    creator_id: int
    assignee_id: int | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    ticket_id: int
    content: str


class CommentRead(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
