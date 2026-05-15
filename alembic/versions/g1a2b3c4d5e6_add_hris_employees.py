"""add_hris_employees

Revision ID: g1a2b3c4d5e6
Revises: f4c2a8d5e003
Create Date: 2026-05-16 09:00:00.000000

Phase H1 — Data Karyawan & Organisasi
Creates: hris_departments, hris_job_grades, hris_employees, hris_employee_documents
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "g1a2b3c4d5e6"
down_revision: Union[str, None] = "f4c2a8d5e003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── hris_departments ──────────────────────────────────────────────────────
    op.create_table(
        "hris_departments",
        sa.Column("id",         sa.Integer(),     primary_key=True),
        sa.Column("code",       sa.String(50),    nullable=False),
        sa.Column("name",       sa.String(255),   nullable=False),
        sa.Column("parent_id",  sa.Integer(),     nullable=True),
        sa.Column("is_active",  sa.Boolean(),     nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["hris_departments.id"], name="fk_dept_parent"),
        sa.UniqueConstraint("code", name="uq_hris_dept_code"),
    )
    op.create_index("ix_hris_departments_code", "hris_departments", ["code"])

    # ── hris_job_grades ───────────────────────────────────────────────────────
    op.create_table(
        "hris_job_grades",
        sa.Column("id",         sa.Integer(),   primary_key=True),
        sa.Column("code",       sa.String(50),  nullable=False),
        sa.Column("name",       sa.String(255), nullable=False),
        sa.Column("level",      sa.Integer(),   nullable=False, server_default="1"),
        sa.Column("is_active",  sa.Boolean(),   nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("code", name="uq_hris_grade_code"),
    )
    op.create_index("ix_hris_job_grades_code", "hris_job_grades", ["code"])

    # ── hris_employees ────────────────────────────────────────────────────────
    employment_type = sa.Enum(
        "Tetap", "PKWT", "Outsource",
        name="employmenttype",
    )
    employee_status = sa.Enum(
        "active", "probation", "leave", "terminated",
        name="employeestatus",
    )

    op.create_table(
        "hris_employees",
        sa.Column("id",             sa.Integer(),     primary_key=True),
        sa.Column("employee_no",    sa.String(50),    nullable=False),
        sa.Column("full_name",      sa.String(255),   nullable=False),
        sa.Column("nik",            sa.String(16),    nullable=True),
        sa.Column("npwp",           sa.String(20),    nullable=True),
        sa.Column("email",          sa.String(320),   nullable=True),
        sa.Column("phone",          sa.String(20),    nullable=True),
        sa.Column("tipe",           employment_type,  nullable=False),
        sa.Column("status",         employee_status,  nullable=False, server_default="active"),
        sa.Column("dept_id",        sa.Integer(),     nullable=True),
        sa.Column("grade_id",       sa.Integer(),     nullable=True),
        sa.Column("site",           sa.String(255),   nullable=True),
        sa.Column("join_date",      sa.Date(),        nullable=True),
        sa.Column("end_date",       sa.Date(),        nullable=True),
        sa.Column("bank_name",      sa.String(100),   nullable=True),
        sa.Column("bank_account",   sa.String(50),    nullable=True),
        sa.Column("bpjs_tk_no",     sa.String(30),    nullable=True),
        sa.Column("bpjs_kes_no",    sa.String(30),    nullable=True),
        sa.Column("user_id",        sa.Integer(),     nullable=True),
        sa.Column("photo_url",      sa.String(500),   nullable=True),
        sa.Column("face_embedding", JSONB,            nullable=True),
        sa.Column("created_at",     sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at",     sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["dept_id"],  ["hris_departments.id"], name="fk_emp_dept"),
        sa.ForeignKeyConstraint(["grade_id"], ["hris_job_grades.id"],  name="fk_emp_grade"),
        sa.ForeignKeyConstraint(["user_id"],  ["users.id"],            name="fk_emp_user"),
        sa.UniqueConstraint("employee_no", name="uq_hris_emp_no"),
        sa.UniqueConstraint("nik",         name="uq_hris_emp_nik"),
        sa.UniqueConstraint("user_id",     name="uq_hris_emp_user"),
    )
    op.create_index("ix_hris_employees_employee_no", "hris_employees", ["employee_no"])
    op.create_index("ix_hris_employees_dept",        "hris_employees", ["dept_id"])
    op.create_index("ix_hris_employees_status",      "hris_employees", ["status"])
    op.create_index("ix_hris_employees_tipe",        "hris_employees", ["tipe"])

    # ── hris_employee_documents ───────────────────────────────────────────────
    emp_doc_type = sa.Enum(
        "KTP", "NPWP", "BPJS_TK", "BPJS_KES", "IJAZAH", "SKCK", "OTHER",
        name="empdoctype",
    )

    op.create_table(
        "hris_employee_documents",
        sa.Column("id",          sa.Integer(),   primary_key=True),
        sa.Column("employee_id", sa.Integer(),   nullable=False),
        sa.Column("doc_type",    emp_doc_type,   nullable=False),
        sa.Column("file_url",    sa.String(500), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at",  sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at",  sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["hris_employees.id"], name="fk_empdoc_emp", ondelete="CASCADE"),
    )
    op.create_index("ix_hris_employee_documents_emp", "hris_employee_documents", ["employee_id"])


def downgrade() -> None:
    op.drop_table("hris_employee_documents")
    op.drop_table("hris_employees")
    op.drop_table("hris_job_grades")
    op.drop_table("hris_departments")
    op.execute("DROP TYPE IF EXISTS empdoctype")
    op.execute("DROP TYPE IF EXISTS employeestatus")
    op.execute("DROP TYPE IF EXISTS employmenttype")
