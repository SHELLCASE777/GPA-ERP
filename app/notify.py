"""
GPA-ERP V5.0 — In-app notification helpers.
Call push() / push_to_role() before db.commit() — they only add objects to the session.
"""
from sqlalchemy.orm import Session

from app.models import Notification, RoleName, User


def push(db: Session, user_id: int, title: str, body: str, link: str | None = None) -> None:
    """Queue a notification for a single user (added to the current session)."""
    db.add(Notification(user_id=user_id, title=title, body=body, link=link))


def push_to_role(
    db: Session,
    role: RoleName,
    title: str,
    body: str,
    link: str | None = None,
) -> None:
    """Queue a notification for every active user that holds *role*."""
    from app.models import Role  # local import to avoid circular
    users = (
        db.query(User)
        .join(User.role)
        .filter(Role.name == role, User.is_active == True)
        .all()
    )
    for u in users:
        push(db, u.id, title, body, link)
