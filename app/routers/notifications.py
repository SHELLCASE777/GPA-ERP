"""
GPA-ERP V5.0 — Notifications router.

GET  /notifications               → last 30 notifications for current user (unread first)
GET  /notifications/unread-count  → { count: int }
POST /notifications/{id}/read     → mark one notification as read
POST /notifications/read-all      → mark all current user's notifications as read
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser
from app.models import Notification
from app.schemas import MessageResponse, NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut], summary="List my notifications")
def list_notifications(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    """Return the 30 most-recent notifications for the authenticated user, unread first."""
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.is_read.asc(), Notification.created_at.desc())
        .limit(30)
        .all()
    )
    return notifications


@router.get("/unread-count", response_model=dict, summary="Count of unread notifications")
def unread_count(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    count = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
        .count()
    )
    return {"count": count}


@router.post("/{notification_id}/read", response_model=MessageResponse, summary="Mark one notification as read")
def mark_one_read(
    notification_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    notif = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .first()
    )
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.post("/read-all", response_model=MessageResponse, summary="Mark all notifications as read")
def mark_all_read(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
        )
        .update({"is_read": True}, synchronize_session=False)
    )
    db.commit()
    return {"message": "All notifications marked as read"}
