from sqlalchemy.orm import Session
from datetime import datetime

from app import models, schemas


def create_ticket(db: Session, payload: schemas.TicketCreate, creator_id: int) -> models.Ticket:
    ticket = models.Ticket(**payload.model_dump(), creator_id=creator_id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(db: Session, user_id: int = None, mine: bool = False, assigned: bool = False, related: bool = False):
    query = db.query(models.Ticket).order_by(models.Ticket.created_at.desc())
    if mine:
        query = query.filter(models.Ticket.creator_id == user_id)
    elif assigned:
        query = query.filter(models.Ticket.assignee_id == user_id)
    elif related:
        query = query.filter(
            db.or_(
                models.Ticket.creator_id == user_id,
                models.Ticket.assignee_id == user_id
            )
        )
    return query.all()


def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()


def update_ticket_status(db: Session, ticket: models.Ticket, status: str) -> models.Ticket:
    ticket.status = status
    ticket.updated_at = datetime.utcnow()
    ticket.closed_at = datetime.utcnow() if status == "closed" else None
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def create_comment(db: Session, payload: schemas.CommentCreate, author_id: int) -> models.Comment:
    comment = models.Comment(**payload.model_dump(), author_id=author_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments_by_ticket(db: Session, ticket_id: int):
    return db.query(models.Comment).filter(models.Comment.ticket_id == ticket_id).all()
