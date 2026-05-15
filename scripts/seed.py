"""
GPA-ERP V5.0 — Database seed script
Run: python -m scripts.seed

Creates:
  • All 7 Roles
  • Super Admin user (from .env / defaults)
  • Default Cost Codes (Direct / Site / Personnel / Overhead / Other)
  • Default Approval Rules (the approval matrix)
  • 3 sample Projects
  • 1 sample AR + 1 sample Expense (draft) per project
"""
import sys
import os

# Allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import (
    AccountReceivable, ApprovalRule, Base, CostCentre, CostCode,
    CostCodeCategory, Expense, ExpenseStatus, Project, Role, RoleName, User,
)
from app.dependencies import hash_password
from app.config import get_settings

settings = get_settings()


def seed_roles(db: Session) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for name in RoleName:
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            role = Role(name=name)
            db.add(role)
            db.flush()
            print(f"  [+] Role: {name.value}")
        roles[name.value] = role
    return roles


def seed_super_admin(db: Session, roles: dict[str, Role]) -> User:
    email = settings.SEED_SUPER_ADMIN_EMAIL.lower()
    user  = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email           = email,
            hashed_password = hash_password(settings.SEED_SUPER_ADMIN_PASSWORD),
            full_name       = settings.SEED_SUPER_ADMIN_NAME,
            role_id         = roles[RoleName.SUPER_ADMIN.value].id,
            is_active       = True,
        )
        db.add(user)
        db.flush()
        print(f"  [+] Super Admin: {email}")
    else:
        print(f"  [=] Super Admin already exists: {email}")
    return user


def seed_cost_codes(db: Session) -> dict[str, CostCode]:
    definitions = [
        # Direct costs
        ("01.00", "Direct Costs",                   None,    CostCodeCategory.DIRECT),
        ("01.10", "Structural Works",               "01.00", CostCodeCategory.DIRECT),
        ("01.20", "MEP Rough-In",                   "01.00", CostCodeCategory.DIRECT),
        ("01.30", "Finishing Works",                "01.00", CostCodeCategory.DIRECT),
        ("01.40", "Electrical Works",               "01.00", CostCodeCategory.DIRECT),
        # Site costs
        ("02.00", "Site Costs",                     None,    CostCodeCategory.SITE),
        ("02.10", "Temporary Facilities",           "02.00", CostCodeCategory.SITE),
        ("02.20", "Site Security",                  "02.00", CostCodeCategory.SITE),
        ("02.30", "Site Utilities",                 "02.00", CostCodeCategory.SITE),
        ("02.40", "Equipment Rental",               "02.00", CostCodeCategory.SITE),
        # Personnel
        ("03.00", "Personnel",                      None,    CostCodeCategory.PERSONNEL),
        ("03.10", "Direct Labor",                   "03.00", CostCodeCategory.PERSONNEL),
        ("03.20", "Subcontract Labor",              "03.00", CostCodeCategory.PERSONNEL),
        ("03.30", "Staff Overtime",                 "03.00", CostCodeCategory.PERSONNEL),
        # Overhead
        ("04.00", "Overhead",                       None,    CostCodeCategory.OVERHEAD),
        ("04.10", "Office & Admin",                 "04.00", CostCodeCategory.OVERHEAD),
        ("04.20", "Transportation",                 "04.00", CostCodeCategory.OVERHEAD),
        ("04.30", "Communication",                  "04.00", CostCodeCategory.OVERHEAD),
        ("04.40", "Insurance & Permits",            "04.00", CostCodeCategory.OVERHEAD),
        ("04.50", "MEP Rough-In (Overhead Alloc.)", "04.00", CostCodeCategory.OVERHEAD),
        # Other
        ("05.00", "Other",                          None,    CostCodeCategory.OTHER),
        ("05.10", "Petty Cash Replenishment",       "05.00", CostCodeCategory.OTHER),
        ("05.20", "Miscellaneous",                  "05.00", CostCodeCategory.OTHER),
    ]

    # Build parent code → CostCode lookup
    code_map: dict[str, CostCode] = {}
    for cc in db.query(CostCode).all():
        code_map[cc.code] = cc

    created: dict[str, CostCode] = {}
    for code, name, parent_code, category in definitions:
        if code in code_map:
            created[code] = code_map[code]
            continue

        parent_id = code_map[parent_code].id if parent_code and parent_code in code_map else None
        cc = CostCode(code=code, name=name, parent_id=parent_id, category=category)
        db.add(cc)
        db.flush()
        code_map[code] = cc
        created[code]  = cc
        print(f"  [+] CostCode: {code} — {name}")

    return created


def seed_cost_centres(db: Session):
    definitions = [
        ("OPS", "Operational Cash", "Day-to-day project spending pocket"),
        ("PETTY", "Petty Cash", "Small reimbursable site and office expenses"),
        ("CLIENT", "Client Funded", "Spend backed directly by client PO or billing"),
        ("CAPEX", "Company Capex", "Company-owned tools, assets, and equipment"),
    ]
    for code, name, description in definitions:
        if db.query(CostCentre).filter(CostCentre.code == code).first():
            continue
        db.add(CostCentre(code=code, name=name, description=description, is_active=True))
        db.flush()
        print(f"  [+] CostCentre: {code} - {name}")


def seed_approval_rules(db: Session):
    """
    Default multi-level approval matrix.
    Priority 1 = first in chain, 2 = second, etc.

    Tier 1 — up to ₱50,000       : COST_CONTROL (any category)
    Tier 2 — ₱50,001–₱500,000    : COST_CONTROL → PM
    Tier 3 — ₱500,001–₱2,000,000 : COST_CONTROL → PM → FINANCE
    Tier 4 — above ₱2,000,000    : COST_CONTROL → PM → FINANCE → MD
    """
    if db.query(ApprovalRule).count() > 0:
        print("  [=] Approval rules already seeded — skipping")
        return

    rules = [
        # Tier 1
        dict(min_amount=Decimal("0"),          max_amount=Decimal("50000"),    required_role=RoleName.COST_CONTROL, priority=1),
        # Tier 2
        dict(min_amount=Decimal("50000.01"),   max_amount=Decimal("500000"),   required_role=RoleName.COST_CONTROL, priority=1),
        dict(min_amount=Decimal("50000.01"),   max_amount=Decimal("500000"),   required_role=RoleName.PM,           priority=2),
        # Tier 3
        dict(min_amount=Decimal("500000.01"),  max_amount=Decimal("2000000"),  required_role=RoleName.COST_CONTROL, priority=1),
        dict(min_amount=Decimal("500000.01"),  max_amount=Decimal("2000000"),  required_role=RoleName.PM,           priority=2),
        dict(min_amount=Decimal("500000.01"),  max_amount=Decimal("2000000"),  required_role=RoleName.FINANCE,      priority=3),
        # Tier 4
        dict(min_amount=Decimal("2000000.01"), max_amount=None,                required_role=RoleName.COST_CONTROL, priority=1),
        dict(min_amount=Decimal("2000000.01"), max_amount=None,                required_role=RoleName.PM,           priority=2),
        dict(min_amount=Decimal("2000000.01"), max_amount=None,                required_role=RoleName.FINANCE,      priority=3),
        dict(min_amount=Decimal("2000000.01"), max_amount=None,                required_role=RoleName.MD,           priority=4),
    ]

    for r in rules:
        rule = ApprovalRule(**r, is_active=True)
        db.add(rule)
    db.flush()
    print(f"  [+] Approval rules: {len(rules)} entries seeded")


def seed_projects(db: Session) -> list[Project]:
    now = datetime.now(timezone.utc)
    samples = [
        dict(code="CW-1142", name="Greenfield Office Tower – Phase 1",
             contract_value=Decimal("125000000.00"),
             start_date=now - timedelta(days=90), end_date=now + timedelta(days=275)),
        dict(code="NV-0891", name="North Viaduct Bridge Rehabilitation",
             contract_value=Decimal("48500000.00"),
             start_date=now - timedelta(days=30), end_date=now + timedelta(days=180)),
        dict(code="MK-0712", name="Makati Mixed-Use Development",
             contract_value=Decimal("310000000.00"),
             start_date=now + timedelta(days=15),  end_date=now + timedelta(days=730)),
    ]
    projects = []
    for s in samples:
        p = db.query(Project).filter(Project.code == s["code"]).first()
        if not p:
            p = Project(**s)
            db.add(p)
            db.flush()
            print(f"  [+] Project: {s['code']} — {s['name']}")
        projects.append(p)
    return projects


def seed_sample_data(db: Session, projects: list[Project], cost_codes: dict[str, CostCode],
                     admin_user: User):
    """One AR + one Expense per project for demo purposes."""
    for project in projects:
        # AR
        if not db.query(AccountReceivable).filter(AccountReceivable.project_id == project.id).first():
            ar = AccountReceivable(
                project_id  = project.id,
                amount      = project.contract_value * Decimal("0.20"),
                description = "Progress Billing #1 — 20% Mobilisation",
            )
            db.add(ar)
            db.flush()
            print(f"  [+] AR for {project.code}: ₱{ar.amount:,.2f}")

        # Expense
        if not db.query(Expense).filter(Expense.project_id == project.id).first():
            cc = cost_codes.get("01.10")
            if cc:
                exp = Expense(
                    project_id       = project.id,
                    cost_code_id     = cc.id,
                    amount           = Decimal("85000.00"),
                    description      = "Structural steel procurement — sample draft",
                    status           = ExpenseStatus.DRAFT,
                    submitted_by     = admin_user.id,
                    approval_chain   = [],
                    approval_history = [],
                    approval_step    = 0,
                )
                db.add(exp)
                db.flush()
                print(f"  [+] Expense (draft) for {project.code}: ₱{exp.amount:,.2f}")


def run():
    print("\n══════════════════════════════════════")
    print("  GPA-ERP V5.0 — Database Seed")
    print("══════════════════════════════════════\n")

    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        print("▶ Seeding roles …")
        roles = seed_roles(db)
        db.commit()

        print("▶ Seeding super admin …")
        admin = seed_super_admin(db, roles)
        db.commit()

        print("▶ Seeding cost codes …")
        cost_codes = seed_cost_codes(db)
        db.commit()

        print("▶ Seeding cost centres …")
        seed_cost_centres(db)
        db.commit()

        print("▶ Seeding approval rules …")
        seed_approval_rules(db)
        db.commit()

        print("▶ Seeding sample projects …")
        projects = seed_projects(db)
        db.commit()

        print("▶ Seeding sample ARs & expenses …")
        seed_sample_data(db, projects, cost_codes, admin)
        db.commit()

        print("\n✓ Seed complete.\n")
    except Exception as exc:
        db.rollback()
        print(f"\n✗ Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
