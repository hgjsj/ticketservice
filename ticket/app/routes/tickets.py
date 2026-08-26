from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[schemas.TicketRead])
def get_tickets(
    db: Session = Depends(get_db),
    current_user: schemas.AuthenticatedUser = Depends(get_current_user),
    mine: bool = Query(default=False, description="只返回当前用户创建的工单"),
    assigned: bool = Query(default=False, description="只返回分配给当前用户的工单"),
    related: bool = Query(default=False, description="只返回与当前用户相关的工单（创建或分配）"),
):
    return crud.list_tickets(db, current_user.id, mine, assigned, related)


@router.post("", response_model=schemas.TicketRead)
def create_ticket(
    payload: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user: schemas.AuthenticatedUser = Depends(get_current_user),
):
    return crud.create_ticket(db, payload, current_user.id)


@router.get("/{ticket_id}", response_model=schemas.TicketRead)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.AuthenticatedUser = Depends(get_current_user),
):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}/status", response_model=schemas.TicketRead)
def patch_ticket_status(
    ticket_id: int,
    payload: schemas.TicketUpdateStatus,
    db: Session = Depends(get_db),
    current_user: schemas.AuthenticatedUser = Depends(get_current_user),
):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return crud.update_ticket_status(db, ticket, payload.status)
