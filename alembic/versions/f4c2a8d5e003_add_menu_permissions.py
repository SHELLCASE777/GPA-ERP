"""add_menu_permissions

Revision ID: f4c2a8d5e003
Revises: e1b7a9c4d002
Create Date: 2026-05-14 19:15:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f4c2a8d5e003"
down_revision: Union[str, None] = "e1b7a9c4d002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_menus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(80), nullable=False),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("section", sa.String(80), nullable=False, server_default="Workspace"),
        sa.Column("path", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(op.f("ix_app_menus_key"), "app_menus", ["key"], unique=True)
    op.create_index("ix_app_menus_section_sort", "app_menus", ["section", "sort_order"])

    op.create_table(
        "user_menu_permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("menu_id", sa.Integer(), nullable=False),
        sa.Column("can_access", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["menu_id"], ["app_menus.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "menu_id", name="uq_user_menu_permission"),
    )
    op.create_index(op.f("ix_user_menu_permissions_user_id"), "user_menu_permissions", ["user_id"])
    op.create_index(op.f("ix_user_menu_permissions_menu_id"), "user_menu_permissions", ["menu_id"])
    op.create_index("ix_user_menu_permission_lookup", "user_menu_permissions", ["user_id", "menu_id"])


def downgrade() -> None:
    op.drop_index("ix_user_menu_permission_lookup", table_name="user_menu_permissions")
    op.drop_index(op.f("ix_user_menu_permissions_menu_id"), table_name="user_menu_permissions")
    op.drop_index(op.f("ix_user_menu_permissions_user_id"), table_name="user_menu_permissions")
    op.drop_table("user_menu_permissions")
    op.drop_index("ix_app_menus_section_sort", table_name="app_menus")
    op.drop_index(op.f("ix_app_menus_key"), table_name="app_menus")
    op.drop_table("app_menus")
