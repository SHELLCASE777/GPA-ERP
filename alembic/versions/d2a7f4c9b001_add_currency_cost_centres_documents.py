"""add_currency_cost_centres_documents

Revision ID: d2a7f4c9b001
Revises: c9f3a12e8b01
Create Date: 2026-05-12 21:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d2a7f4c9b001"
down_revision: Union[str, None] = "c9f3a12e8b01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("currency", sa.String(3), nullable=False, server_default="IDR"))

    op.create_table(
        "cost_centres",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_cost_centres_code"), "cost_centres", ["code"], unique=True)

    op.add_column("expenses", sa.Column("cost_centre_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_expenses_cost_centre_id", "expenses", "cost_centres", ["cost_centre_id"], ["id"])

    op.create_table(
        "project_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("doc_type", sa.String(50), nullable=False, server_default="contract"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(2048), nullable=False),
        sa.Column("reference_no", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_docs_project_type", "project_documents", ["project_id", "doc_type"])
    op.create_index(op.f("ix_project_documents_project_id"), "project_documents", ["project_id"])

    op.add_column("legal_documents", sa.Column("reference_number", sa.String(100), nullable=True))
    op.create_index(op.f("ix_legal_documents_reference_number"), "legal_documents", ["reference_number"])


def downgrade() -> None:
    op.drop_index(op.f("ix_legal_documents_reference_number"), table_name="legal_documents")
    op.drop_column("legal_documents", "reference_number")
    op.drop_index(op.f("ix_project_documents_project_id"), table_name="project_documents")
    op.drop_index("ix_project_docs_project_type", table_name="project_documents")
    op.drop_table("project_documents")
    op.drop_constraint("fk_expenses_cost_centre_id", "expenses", type_="foreignkey")
    op.drop_column("expenses", "cost_centre_id")
    op.drop_index(op.f("ix_cost_centres_code"), table_name="cost_centres")
    op.drop_table("cost_centres")
    op.drop_column("projects", "currency")
