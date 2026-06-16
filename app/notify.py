"""
GPA-ERP V5.0 — In-app notification helpers.
Call push() / push_to_role() before db.commit() — they only add objects to the session.
"""
from sqlalchemy.orm import Session

from app.models import Notification, RoleName, User


def push(db: Session, user_id: int, title: str, body: str, link: str | None = None) -> None:
    """Queue a notification for a single user (added to the current session)."""
    db.add(Notification(user_id=user_id, title=title, body=body, link=link))

    # Send email notification if user has an email address
    try:
        from app.notify_channels import send_email, build_notification_email
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.email:
            html, text = build_notification_email(title, body, link or "")
            # Run in background thread to not block the request
            import threading
            threading.Thread(target=send_email, args=(user.email, title, html, text), daemon=True).start()
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Could not queue email notification: %s", exc)


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
