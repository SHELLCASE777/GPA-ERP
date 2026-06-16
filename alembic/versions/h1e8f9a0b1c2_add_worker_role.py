"""add worker role and hris_my_payslip menu

Revision ID: h1e8f9a0b1c2
Revises: g4d5e6f7a8b9
Create Date: 2026-05-16

Adds the WORKER role (HRIS self-service only: attendance, leave, own payslip).
Uses ALTER TYPE … ADD VALUE because rolename is a native PG enum.
Also seeds the 'hris_my_payslip' AppMenu row and the Role row for WORKER.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "h1e8f9a0b1c2"
down_revision = "g4d5e6f7a8b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Extend the PG enum (safe to run twice – IF NOT EXISTS) ─────────────
    op.execute("ALTER TYPE rolename ADD VALUE IF NOT EXISTS 'WORKER'")

    # ── 2. Seed the Role row ───────────────────────────────────────────────────
    op.execute("""
        INSERT INTO roles (name) VALUES ('WORKER')
        ON CONFLICT (name) DO NOTHING
    """)

    # ── 3. Seed the hris_my_payslip AppMenu row ───────────────────────────────
    op.execute("""
        INSERT INTO app_menus (key, label, section, path, description, sort_order, is_active)
        VALUES (
            'hris_my_payslip',
            'Slip Gaji Saya',
            'Self Service',
            '/hris/me/payslip',
            'View own monthly payslips',
            245,
            TRUE
        )
        ON CONFLICT (key) DO NOTHING
    """)


def downgrade() -> None:
    # PG does not support removing enum values; skip enum rollback
    op.execute("DELETE FROM roles WHERE name = 'WORKER'")
    op.execute("DELETE FROM app_menus WHERE key = 'hris_my_payslip'")
