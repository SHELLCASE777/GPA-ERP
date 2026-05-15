# GPA-ERP V5.0 — Cost Control Backend

Production-ready FastAPI backend for GPA Construction Cost Control ERP.

---

## Architecture

```
gpa-erp/
├── app/
│   ├── main.py          # FastAPI app, CORS, routers
│   ├── config.py        # Settings (pydantic-settings)
│   ├── database.py      # SQLAlchemy engine + session
│   ├── models.py        # ORM models + hybrid_property budget
│   ├── schemas.py       # Pydantic v2 request/response models
│   ├── dependencies.py  # JWT auth, role guards, approval matrix
│   ├── audit.py         # Immutable audit log service
│   └── routers/
│       ├── auth.py          # POST /auth/login, GET /auth/me
│       ├── users.py         # CRUD /users
│       ├── projects.py      # CRUD /projects + POST /projects/import-excel
│       ├── receivables.py   # CRUD /receivables + POST /{id}/confirm
│       ├── expenses.py      # Full workflow /expenses + lifecycle actions
│       └── vault.py         # /vault/cost-codes, /vault/approval-rules, /vault/audit-log
├── alembic/             # Database migrations
├── scripts/
│   └── seed.py          # Initial data + sample records
├── .env.example
├── alembic.ini
└── requirements.txt
```

---

## Quick-Start (Local)

### 1 — Prerequisites

- Python 3.11+
- PostgreSQL 14+

### 2 — Clone & create virtual env

```bash
cd gpa-erp
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure environment

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL, SECRET_KEY, etc.
```

### 5 — Create database

```sql
-- in psql
CREATE USER gpa_user WITH PASSWORD 'gpa_pass';
CREATE DATABASE gpa_erp OWNER gpa_user;
GRANT ALL PRIVILEGES ON DATABASE gpa_erp TO gpa_user;
```

### 6 — Run Alembic migrations

```bash
# Generate the initial migration from your models
alembic revision --autogenerate -m "initial_schema"

# Apply it
alembic upgrade head
```

### 7 — Seed the database

```bash
python -m scripts.seed
```

This creates:
- All 7 roles
- Super Admin user (`admin@gpa.local` / `ChangeMe123!` by default — override in `.env`)
- 22 default Cost Codes (hierarchical, all categories)
- 10 Approval Rules (4-tier matrix)
- 3 sample Projects with draft ARs and Expenses

### 8 — Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs  
ReDoc:    http://localhost:8000/redoc

---

## API Overview

### Authentication

```
POST /api/auth/login      — returns JWT (Bearer)
GET  /api/auth/me         — current user profile
```

### Projects

```
GET    /api/projects                — list (filter by status)
POST   /api/projects                — create
GET    /api/projects/{id}           — detail (includes budget hybrid props)
PATCH  /api/projects/{id}           — update
DELETE /api/projects/{id}           — soft-cancel
POST   /api/projects/import-excel   — bulk import (Excel or CSV)
```

**Excel/CSV template columns**: `code | name | contract_value | start_date | end_date | status`

### Revenue — Account Receivables

```
GET    /api/receivables           — list
POST   /api/receivables           — create draft billing
GET    /api/receivables/{id}
POST   /api/receivables/{id}/confirm   — MD/SUPER_ADMIN only
DELETE /api/receivables/{id}           — draft only
```

### Spending — Expenses

```
GET    /api/expenses                     — list (filter: project, status, my_queue=true)
POST   /api/expenses                     — create draft
GET    /api/expenses/{id}
PATCH  /api/expenses/{id}                — edit draft
POST   /api/expenses/{id}/submit         — draft → submitted (builds approval chain)
POST   /api/expenses/{id}/verify         — COST_CONTROL verification
POST   /api/expenses/{id}/approve        — role-based chain approval
POST   /api/expenses/{id}/pay            — FINANCE disbursement
POST   /api/expenses/{id}/lock           — SUPER_ADMIN period close → hard_locked
POST   /api/expenses/{id}/reject         — reject back to draft
GET    /api/expenses/{id}/audit          — full audit trail
```

### Vault (Super Admin)

```
GET/POST/PATCH/DELETE /api/vault/cost-codes/{id}
GET/POST/PATCH/DELETE /api/vault/approval-rules/{id}
GET                   /api/vault/audit-log
```

---

## Roles & Permissions

| Role         | Create Expense | Verify | Approve (matrix) | Pay | Lock | Confirm AR | Vault |
|--------------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| SUPER_ADMIN  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| MD           | ✓ | — | ✓ | — | — | ✓ | read |
| PM           | ✓ | — | ✓ | — | — | — | read |
| COST_CONTROL | ✓ | ✓ | ✓ | — | — | — | read |
| FINANCE      | ✓ | — | ✓ | ✓ | — | — | — |
| GA           | ✓ | — | — | — | — | — | — |
| STAFF        | ✓ | — | — | — | — | — | — |

---

## Approval Matrix (default)

| Amount Range              | Chain                                |
|---------------------------|--------------------------------------|
| ₱0 – ₱50,000             | COST_CONTROL                         |
| ₱50,001 – ₱500,000       | COST_CONTROL → PM                    |
| ₱500,001 – ₱2,000,000    | COST_CONTROL → PM → FINANCE          |
| > ₱2,000,000             | COST_CONTROL → PM → FINANCE → MD     |

Matrix is fully configurable via `POST /api/vault/approval-rules`.

---

## Revenue-Driven Budget

`Project.budget` is a SQLAlchemy `hybrid_property`:

```
budget = total_revenue (confirmed ARs) − total_committed (verified/approved/paid/locked expenses)
```

This means teams can only commit spend up to recognised revenue — enforced at the data model level.

---

## Expense Lifecycle

```
draft ──submit──► submitted ──verify (CC)──► verified ──approve (matrix)──► approved ──pay (FIN)──► paid ──lock──► hard_locked
  ▲                    │                         │                    │
  └────────────────────┴─────────reject──────────┘                    │
                                                                      └──reject──► rejected ──resubmit──► submitted
```

---

## Alembic Cheatsheet

```bash
# New migration after model change
alembic revision --autogenerate -m "description"

# Apply all pending
alembic upgrade head

# Roll back one
alembic downgrade -1

# Show history
alembic history --verbose
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | (required) |
| `SECRET_KEY` | JWT signing secret — use a 64-char random string in prod | (required) |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL | `480` (8 h) |
| `DEBUG` | Verbose SQL + full error responses | `false` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000,...` |
| `SEED_SUPER_ADMIN_EMAIL` | Email for seeded admin | `admin@gpa.local` |
| `SEED_SUPER_ADMIN_PASSWORD` | Password for seeded admin | `ChangeMe123!` |
