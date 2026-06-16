"""
GPA-ERP — Resync all user menu permissions to current ROLE_PRESETS.

Use after updating ROLE_PRESETS to push new matrix to all existing users.
Safe to run multiple times (idempotent).

Run: PYTHONPATH=. .venv/Scripts/python.exe scripts/resync_permissions.py
"""
from app.database import SessionLocal
from app.models import AppMenu, RoleName, User, UserMenuPermission
from app.menu_permissions import ROLE_PRESETS


def resync(db):
    menus_by_key = {m.key: m for m in db.query(AppMenu).filter(AppMenu.is_active == True).all()}
    users = db.query(User).filter(User.is_active == True).all()

    total_added = 0
    total_removed = 0

    for user in users:
        role_name = user.role.name.value  # e.g. "STAFF"

        if user.role.name == RoleName.SUPER_ADMIN:
            print(f"  [skip] {user.email} — SUPER_ADMIN (always gets all menus)")
            continue

        preset_keys: set[str] = ROLE_PRESETS.get(role_name, set())

        # Current permissions for this user
        existing_perms = db.query(UserMenuPermission).filter(
            UserMenuPermission.user_id == user.id
        ).all()

        # Build reverse map: menu_id → key
        id_to_key = {m.id: k for k, m in menus_by_key.items()}
        existing_by_key: dict[str, UserMenuPermission] = {}
        for p in existing_perms:
            k = id_to_key.get(p.menu_id)
            if k:
                existing_by_key[k] = p

        existing_keys = set(existing_by_key.keys())

        keys_to_add    = preset_keys - existing_keys
        keys_to_remove = existing_keys - preset_keys

        for key in keys_to_add:
            menu = menus_by_key.get(key)
            if menu:
                db.add(UserMenuPermission(user_id=user.id, menu_id=menu.id, can_access=True))
                total_added += 1

        for key in keys_to_remove:
            perm = existing_by_key.get(key)
            if perm:
                db.delete(perm)
                total_removed += 1

        changes = []
        if keys_to_add:    changes.append(f"+{len(keys_to_add)} ({', '.join(sorted(keys_to_add))})")
        if keys_to_remove: changes.append(f"-{len(keys_to_remove)} ({', '.join(sorted(keys_to_remove))})")
        status = ", ".join(changes) if changes else "no changes"
        print(f"  [{role_name:12s}] {user.email}: {status}")

    db.commit()
    print(f"\nDone. Added: {total_added}  Removed: {total_removed}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Resyncing user menu permissions to current ROLE_PRESETS...\n")
        resync(db)
    finally:
        db.close()
