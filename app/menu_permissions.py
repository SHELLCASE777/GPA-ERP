from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser
from app.models import AppMenu, RoleName, User, UserMenuPermission

DEFAULT_MENUS = [
    ("dashboard", "Dashboard", "Workspace", "/dashboard", "Executive dashboard and KPI overview", 10),
    ("action_center", "Action Center", "Workspace", "/action-center", "Approval queue and pending actions", 15),
    ("project_command", "Project Command", "Operations", "/projects", "Projects, contracts, POs, budget, archive controls", 20),
    ("revenue_ar", "Revenue / AR", "Finance", "/revenue", "Client invoices, payments, outstanding AR", 30),
    ("spending", "Spending", "Finance", "/spending", "Expense drafts, approvals, payment workflow", 40),
    ("petty_cash", "Petty Cash", "Finance", "/spending", "Monthly petty cash reports and OCR/clipboard entry", 45),
    ("inventory", "Inventory & Assets", "Operations", "/inventory", "Materials, tools, consumables, stock movement", 50),
    ("legal", "Legal & Proposals", "Procurement / Legal", "/legal", "Legal proposals, drafts, documents, signatures", 60),
    ("procurement", "Procurement", "Procurement / Legal", "/procurement", "PO and contract tracking", 70),
    ("reports", "Reports", "Reports", "/reports", "Finance, project, and operational reports", 80),
    ("settings", "Settings", "Vault", "/settings", "Users, roles, branding, configuration", 90),
    ("vault", "Vault", "Vault", "/vault", "Approval matrix, cost codes, cost centres, audit log", 100),
    ("backend_admin", "Backend Admin", "System", "/admin", "Backend maintenance console", 110),
]
OBSOLETE_MENU_KEYS = {"expenses", "procurement"}

ROLE_PRESETS: dict[str, set[str]] = {
    "SUPER_ADMIN": {key for key, *_ in DEFAULT_MENUS},
    "MD": {"dashboard", "action_center", "project_command", "revenue_ar", "spending", "inventory", "legal", "reports"},
    "PM": {"dashboard", "action_center", "project_command", "spending", "inventory", "legal", "reports"},
    "COST_CONTROL": {"dashboard", "action_center", "project_command", "spending", "petty_cash", "inventory", "reports"},
    "FINANCE": {"dashboard", "action_center", "project_command", "revenue_ar", "spending", "petty_cash", "reports"},
    "GA": {"dashboard", "action_center", "spending", "petty_cash", "inventory"},
    "STAFF": {"dashboard", "action_center", "spending"},
}


def ensure_default_menus(db: Session) -> None:
    existing = {menu.key: menu for menu in db.query(AppMenu).all()}
    changed = False
    for key, label, section, path, description, sort_order in DEFAULT_MENUS:
        menu = existing.get(key)
        if menu:
            updates = {
                "label": label,
                "section": section,
                "path": path,
                "description": description,
                "sort_order": sort_order,
            }
            for field, value in updates.items():
                if getattr(menu, field) != value:
                    setattr(menu, field, value)
                    changed = True
        else:
            db.add(
                AppMenu(
                    key=key,
                    label=label,
                    section=section,
                    path=path,
                    description=description,
                    sort_order=sort_order,
                    is_active=True,
                )
            )
            changed = True
    for key in OBSOLETE_MENU_KEYS:
        menu = existing.get(key)
        if menu and menu.is_active:
            menu.is_active = False
            changed = True
    if changed:
        db.commit()
    seed_missing_user_permissions(db)


def seed_missing_user_permissions(db: Session) -> None:
    menus = {menu.key: menu for menu in db.query(AppMenu).filter(AppMenu.is_active == True).all()}
    users = db.query(User).filter(User.is_active == True).all()
    changed = False
    for user in users:
        if user.role.name == RoleName.SUPER_ADMIN:
            continue
        existing = (
            db.query(UserMenuPermission.id)
            .filter(UserMenuPermission.user_id == user.id)
            .first()
        )
        if existing:
            continue
        preset_keys = ROLE_PRESETS.get(user.role.name.value, ROLE_PRESETS["STAFF"])
        for key in preset_keys:
            menu = menus.get(key)
            if menu:
                db.add(UserMenuPermission(user_id=user.id, menu_id=menu.id, can_access=True))
                changed = True
    if changed:
        db.commit()


def menu_access_keys_for_user(db: Session, user: User) -> set[str]:
    if user.role.name == RoleName.SUPER_ADMIN:
        ensure_default_menus(db)
        return {menu.key for menu in db.query(AppMenu).filter(AppMenu.is_active == True).all()}

    rows = (
        db.query(AppMenu.key)
        .join(UserMenuPermission, UserMenuPermission.menu_id == AppMenu.id)
        .filter(
            UserMenuPermission.user_id == user.id,
            UserMenuPermission.can_access == True,
            AppMenu.is_active == True,
        )
        .all()
    )
    return {row[0] for row in rows}


def user_has_menu_access(db: Session, user: User, *menu_keys: str) -> bool:
    if user.role.name == RoleName.SUPER_ADMIN:
        return True
    allowed = menu_access_keys_for_user(db, user)
    return any(key in allowed for key in menu_keys)


def require_menu_access(*menu_keys: str):
    def _check(
        current_user: CurrentUser,
        db: Annotated[Session, Depends(get_db)],
    ) -> User:
        if not user_has_menu_access(db, current_user, *menu_keys):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Menu access required: {', '.join(menu_keys)}",
            )
        return current_user
    return _check
