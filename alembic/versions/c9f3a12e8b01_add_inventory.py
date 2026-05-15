"""add_inventory

Revision ID: c9f3a12e8b01
Revises: b4b2538d71e3
Create Date: 2026-05-12 18:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c9f3a12e8b01"
down_revision: Union[str, None] = "b4b2538d71e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inventory_items",
        sa.Column("id",          sa.Integer(),                  nullable=False),
        sa.Column("code",        sa.String(50),                 nullable=False),
        sa.Column("name",        sa.String(255),                nullable=False),
        sa.Column("category",    sa.Enum(
            "equipment", "tools", "consumables", "materials", "other",
            name="itemcategory"
        ), nullable=False),
        sa.Column("unit",        sa.String(50),  server_default="pcs", nullable=False),
        sa.Column("qty_on_hand", sa.Numeric(18, 3), server_default="0", nullable=False),
        sa.Column("min_stock",   sa.Numeric(18, 3), server_default="0", nullable=False),
        sa.Column("unit_cost",   sa.Numeric(18, 2), nullable=True),
        sa.Column("location",    sa.String(255),    nullable=True),
        sa.Column("notes",       sa.Text(),         nullable=True),
        sa.Column("is_active",   sa.Boolean(),   server_default="true", nullable=False),
        sa.Column("created_at",  sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at",  sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_inv_items_category", "inventory_items", ["category"])
    op.create_index("ix_inv_items_active",   "inventory_items", ["is_active"])

    op.create_table(
        "inventory_txns",
        sa.Column("id",          sa.Integer(),     nullable=False),
        sa.Column("item_id",     sa.Integer(),     nullable=False),
        sa.Column("txn_type",    sa.Enum("in", "out", "adjustment", name="txntype"), nullable=False),
        sa.Column("quantity",    sa.Numeric(18, 3), nullable=False),
        sa.Column("reference",   sa.String(255),   nullable=True),
        sa.Column("notes",       sa.Text(),         nullable=True),
        sa.Column("project_id",  sa.Integer(),     nullable=True),
        sa.Column("created_by",  sa.Integer(),     nullable=False),
        sa.Column("created_at",  sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["item_id"],    ["inventory_items.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_inv_txns_item",    "inventory_txns", ["item_id"])
    op.create_index("ix_inv_txns_project", "inventory_txns", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_inv_txns_project", table_name="inventory_txns")
    op.drop_index("ix_inv_txns_item",    table_name="inventory_txns")
    op.drop_table("inventory_txns")
    op.drop_index("ix_inv_items_active",   table_name="inventory_items")
    op.drop_index("ix_inv_items_category", table_name="inventory_items")
    op.drop_table("inventory_items")
    op.execute("DROP TYPE IF EXISTS itemcategory")
    op.execute("DROP TYPE IF EXISTS txntype")
