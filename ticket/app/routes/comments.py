from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/ticket/{ticket_id}", response_model=list[schemas.CommentRead])
def get_comments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.AuthenticatedUser = Depends(get_current_user),
):
    return crud.list_comments_by_ticket(db, ticket_id)


@router.post("", response_model=schemas.CommentRead)
def create_comment(
    payload: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.AuthenticatedUser = Depends(get_current_user),
):
    return crud.create_comment(db, payload, current_user.id)
