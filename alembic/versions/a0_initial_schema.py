"""initial_schema

Revision ID: a0_initial_schema
Revises:
Create Date: 2026-05-01 00:00:00.000000

Creates the core ERP tables that pre-existed the incremental migration chain.
Previously these were created via Base.metadata.create_all(); this migration
makes a fresh Railway Postgres deployment work without that shortcut.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a0_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Enums ────────────────────────────────────────────────────────────────
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE rolename AS ENUM (
                'SUPER_ADMIN','MD','PM','COST_CONTROL','FINANCE','GA','STAFF','WORKER'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE projectstatus AS ENUM ('active','completed','on_hold','cancelled');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE costcodecategory AS ENUM (
                'Direct','Site','Personnel','Overhead','Other','Reimbursement'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE arstatus AS ENUM ('draft','confirmed');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE expensestatus AS ENUM (
                'draft','submitted','verified','approved','paid','hard_locked','rejected'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE expensetype AS ENUM ('regular','reimbursement');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)

    # ── roles ─────────────────────────────────────────────────────────────────
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Enum(
            'SUPER_ADMIN','MD','PM','COST_CONTROL','FINANCE','GA','STAFF','WORKER',
            name='rolename', create_type=False,
        ), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(320), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # ── projects ──────────────────────────────────────────────────────────────
    # Note: 'currency' column is added by migration d2a7f4c9b001
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('contract_value', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum(
            'active','completed','on_hold','cancelled',
            name='projectstatus', create_type=False,
        ), nullable=False, server_default='active'),
        sa.Column('imported_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index(op.f('ix_projects_code'), 'projects', ['code'], unique=True)

    # ── cost_codes ────────────────────────────────────────────────────────────
    op.create_table(
        'cost_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.Enum(
            'Direct','Site','Personnel','Overhead','Other','Reimbursement',
            name='costcodecategory', create_type=False,
        ), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['cost_codes.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index(op.f('ix_cost_codes_code'), 'cost_codes', ['code'], unique=True)

    # ── approval_rules ────────────────────────────────────────────────────────
    op.create_table(
        'approval_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('min_amount', sa.Numeric(18, 2), nullable=False, server_default='0'),
        sa.Column('max_amount', sa.Numeric(18, 2), nullable=True),
        sa.Column('cost_code_category', sa.Enum(
            'Direct','Site','Personnel','Overhead','Other','Reimbursement',
            name='costcodecategory', create_type=False,
        ), nullable=True),
        sa.Column('required_role', sa.Enum(
            'SUPER_ADMIN','MD','PM','COST_CONTROL','FINANCE','GA','STAFF','WORKER',
            name='rolename', create_type=False,
        ), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_approval_rules_priority', 'approval_rules', ['priority'])
    op.create_index('ix_approval_rules_active', 'approval_rules', ['is_active'])

    # ── account_receivables ───────────────────────────────────────────────────
    op.create_table(
        'account_receivables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('invoice_no', sa.String(100), nullable=True),
        sa.Column('customer_name', sa.String(255), nullable=True),
        sa.Column('invoice_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expected_payment', sa.Numeric(18, 2), nullable=True),
        sa.Column('actual_payment', sa.Numeric(18, 2), nullable=True),
        sa.Column('remaining_amount', sa.Numeric(18, 2), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('draft','confirmed', name='arstatus', create_type=False), nullable=False, server_default='draft'),
        sa.Column('confirmed_by', sa.Integer(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['confirmed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_account_receivables_invoice_no'), 'account_receivables', ['invoice_no'])
    op.create_index('ix_ar_project_status', 'account_receivables', ['project_id', 'status'])

    # ── expenses ──────────────────────────────────────────────────────────────
    # cost_centre_id   → added by migration d2a7f4c9b001
    # petty_cash_line_id → added by migration e1b7a9c4d002
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('expense_type', sa.Enum('regular','reimbursement', name='expensetype', create_type=False), nullable=False, server_default='regular'),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('cost_code_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('vendor_name', sa.String(255), nullable=True),
        sa.Column('reference_no', sa.String(100), nullable=True),
        sa.Column('receipt_url', sa.String(2048), nullable=True),
        sa.Column('status', sa.Enum(
            'draft','submitted','verified','approved','paid','hard_locked','rejected',
            name='expensestatus', create_type=False,
        ), nullable=False, server_default='draft'),
        sa.Column('submitted_by', sa.Integer(), nullable=True),
        sa.Column('receipt_reviewed_by', sa.Integer(), nullable=True),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('paid_by', sa.Integer(), nullable=True),
        sa.Column('current_approver_role', sa.String(50), nullable=True),
        sa.Column('approval_chain', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('approval_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('approval_history', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.ForeignKeyConstraint(['cost_code_id'], ['cost_codes.id']),
        sa.ForeignKeyConstraint(['paid_by'], ['users.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['receipt_reviewed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id']),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_expenses_project_status', 'expenses', ['project_id', 'status'])
    op.create_index('ix_expenses_current_approver', 'expenses', ['current_approver_role'])
    op.create_index('ix_expenses_submitted_by', 'expenses', ['submitted_by'])

    # ── audit_logs ────────────────────────────────────────────────────────────
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('before_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('after_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('changed_by', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_changed_by', 'audit_logs', ['changed_by'])
    op.create_index('ix_audit_created_at', 'audit_logs', ['created_at'])

    # ── notifications ─────────────────────────────────────────────────────────
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('body', sa.String(500), nullable=False),
        sa.Column('link', sa.String(500), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'])
    op.create_index('ix_notifications_user_is_read', 'notifications', ['user_id', 'is_read'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('audit_logs')
    op.drop_table('expenses')
    op.drop_table('account_receivables')
    op.drop_table('approval_rules')
    op.drop_table('cost_codes')
    op.drop_table('projects')
    op.drop_table('users')
    op.drop_table('roles')
    op.execute("DROP TYPE IF EXISTS expensetype")
    op.execute("DROP TYPE IF EXISTS expensestatus")
    op.execute("DROP TYPE IF EXISTS arstatus")
    op.execute("DROP TYPE IF EXISTS costcodecategory")
    op.execute("DROP TYPE IF EXISTS projectstatus")
    op.execute("DROP TYPE IF EXISTS rolename")
