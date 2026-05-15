"""
Import GPA AR monitoring workbook into Project Command / Revenue.

Source:
  C:\\Garuda\\(NEW) Monitoring AR GPA_Update 13 Mei 26.xlsx

Re-running this script is safe: invoice numbers are used as the duplicate key.
"""
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import openpyxl
from sqlalchemy import func
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models import ARStatus, AccountReceivable, Project, ProjectStatus, User

WORKBOOK = Path(r"C:\Garuda\(NEW) Monitoring AR GPA_Update 13 Mei 26.xlsx")
SHEET = "ALL PROJECT (2)"

PROJECT_PATTERNS = [
    (r"revamping project|reactivation for turbines", "GPA-KN-REVAMP", "Revamping PT Kertas Nusantara"),
    (r"control valve", "P01.0825.J075", "Repair & Services Control Valve & ON OFF Valve - PT KN"),
    (r"probe x-y vibration|shinkawa", "P01.0825.316", "Additional Probe Shinkawa - PT KN"),
    (r"replacement instrument defective", "P01.0925.S489", "Replacement Instrument Defective MA 77 - PT KN"),
    (r"deviation list of generator", "P01.1025.S549", "Deviation List Of Generator Overhaul 2x63MW - PT KN"),
    (r"deviation parts turbine", "P01.1025.S528", "Deviation Parts Turbine - PT KN"),
    (r"electrical construction", "P01.1125.ELC", "Electrical Construction & Installation - PT KN"),
    (r"cooling tower pump", "P01.1125.S680", "Overhaul Cooling Tower Pump Area MA 42 - PT KN"),
    (r"proximity switch cable scun", "P01.1125.S690", "Proximity Switch Cable Scun & Ferrule MA 42/73 - PT KN"),
    (r"cable scun and ferrule terminal", "P01.1125.S689", "Cable Scun & Ferrule Terminal MA 42/73 - PT KN"),
    (r"air port rodding actuator", "P01.1125.S711", "Service & Repair Air Port Rodding Actuator MA 81 - PT KN"),
    (r"temperature sensor|thermowell", "P01.1225.S788", "Replacement Temperature Sensor & Thermowell - PT KN"),
    (r"toxic gas instrumentation", "P01.1225.S793", "Toxic Gas Instrumentation - PT KN"),
]

AR_DERIVED_CONTRACT_CODES = {
    "GPA-KN-REVAMP",
    "P01.1125.S680",
    "P01.1125.S689",
    "P01.1125.S690",
    "P01.1225.S788",
    "P01.1225.S793",
}


def norm(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "").replace("\xa0", " ")).strip()


def money(value: object) -> Decimal:
    if value in (None, ""):
        return Decimal("0.00")
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except Exception:
        return Decimal("0.00")


def date_value(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    return None


def slug(text: str, max_len: int = 22) -> str:
    clean = re.sub(r"[^A-Z0-9]+", "-", text.upper()).strip("-")
    return clean[:max_len].strip("-") or "PROJECT"


def base_project_name(description: str) -> str:
    desc = norm(description)
    desc = re.split(
        r"\s+(?:Tahap|Terms?|Term|Payment Tahap|Down Payment|DP\s|I \(|II \(|III \(|IV-|IV |V \()",
        desc,
        maxsplit=1,
        flags=re.I,
    )[0]
    desc = desc.replace('"', "").strip(" -")
    return desc


def project_for(description: str, invoice_no: str, customer: str) -> tuple[str, str]:
    low = norm(description).lower()
    for pattern, code, name in PROJECT_PATTERNS:
        if re.search(pattern, low):
            return code, name

    if "indopelita" in customer.lower():
        return f"INDO-{slug(base_project_name(description), 16)}", f"{base_project_name(description)} - {customer.title()}"

    tag_match = re.search(r"INV\.GPA\.KN\.([A-Z]+)", invoice_no.upper())
    if tag_match:
        return f"P01.AR.{tag_match.group(1)}", f"{base_project_name(description)} - PT KN"

    return f"AR-{slug(base_project_name(description), 18)}", f"{base_project_name(description)} - {customer.title()}"


def existing_invoice(db: Session, invoice_no: str) -> AccountReceivable | None:
    return (
        db.query(AccountReceivable)
        .filter(
            (AccountReceivable.invoice_no == invoice_no)
            | (AccountReceivable.description.like(f"%Invoice: {invoice_no}%"))
        )
        .first()
    )


def apply_payment_fields(
    ar: AccountReceivable,
    invoice_no: str,
    customer: str,
    invoice_date: datetime | None,
    due_date: datetime | None,
    paid_date: datetime | None,
    expected_paid: Decimal,
    actual_paid: Decimal,
    remaining: Decimal,
) -> None:
    ar.invoice_no = invoice_no
    ar.customer_name = customer
    ar.invoice_date = invoice_date
    ar.due_date = due_date
    ar.expected_payment = expected_paid if expected_paid > 0 else None
    ar.actual_payment = actual_paid if actual_paid > 0 else None
    ar.remaining_amount = remaining
    ar.paid_at = paid_date


def import_rows() -> tuple[int, int, int, int]:
    wb = openpyxl.load_workbook(WORKBOOK, data_only=True, read_only=True)
    ws = wb[SHEET]

    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@gpa.local").first() or db.query(User).first()
        if not admin:
            raise RuntimeError("No users found. Run seed first.")

        projects_created = projects_updated = ars_created = ars_skipped = 0
        billed_by_project: dict[str, Decimal] = {}

        for row in ws.iter_rows(min_row=7, values_only=True):
            if not row[0] or not row[1]:
                continue

            invoice_no = norm(row[1])
            customer = norm(row[2])
            description = norm(row[4])
            dpp = money(row[11])
            ar_outstanding = money(row[13])
            expected_paid = money(row[15])
            actual_paid = money(row[18])
            remaining = money(row[19])
            invoice_date = date_value(row[5])
            due_date = date_value(row[8])
            paid_date = date_value(row[16])

            if dpp <= 0:
                continue

            code, name = project_for(description, invoice_no, customer)
            project = db.query(Project).filter(Project.code == code).first()
            if not project:
                project = Project(
                    code=code,
                    name=name,
                    contract_value=Decimal("0.00"),
                    currency="IDR",
                    status=ProjectStatus.ACTIVE,
                    start_date=invoice_date.date() if invoice_date else None,
                )
                db.add(project)
                db.flush()
                projects_created += 1
            elif project.name != name and project.code.startswith(("INDO-", "P01.AR.", "AR-")):
                project.name = name
                projects_updated += 1

            billed_by_project[code] = billed_by_project.get(code, Decimal("0.00")) + dpp

            existing = existing_invoice(db, invoice_no)
            if existing:
                existing.project_id = project.id
                existing.amount = dpp
                is_paid = (paid_date is not None or actual_paid > 0) and abs(remaining) <= Decimal("1.00")
                apply_payment_fields(
                    existing, invoice_no, customer, invoice_date, due_date, paid_date,
                    expected_paid, actual_paid, remaining,
                )
                existing.status = ARStatus.CONFIRMED if is_paid else ARStatus.DRAFT
                existing.confirmed_by = admin.id if is_paid else None
                existing.confirmed_at = paid_date or (invoice_date if is_paid else None)
                ars_skipped += 1
                continue

            is_paid = (paid_date is not None or actual_paid > 0) and abs(remaining) <= Decimal("1.00")
            ar = AccountReceivable(
                project_id=project.id,
                amount=dpp,
                description=(
                    f"Invoice: {invoice_no}\n"
                    f"Customer: {customer}\n"
                    f"Description: {description}\n"
                    f"Invoice Date: {invoice_date.date().isoformat() if invoice_date else '-'}\n"
                    f"Due Date: {due_date.date().isoformat() if due_date else '-'}\n"
                    f"DPP: {dpp:,.2f}; AR Outstanding: {ar_outstanding:,.2f}; "
                    f"Expected Paid: {expected_paid:,.2f}; Actual Paid: {actual_paid:,.2f}; "
                    f"Remaining AR: {remaining:,.2f}"
                ),
                invoice_no=invoice_no,
                customer_name=customer,
                invoice_date=invoice_date,
                due_date=due_date,
                expected_payment=expected_paid if expected_paid > 0 else None,
                actual_payment=actual_paid if actual_paid > 0 else None,
                remaining_amount=remaining,
                paid_at=paid_date,
                status=ARStatus.CONFIRMED if is_paid else ARStatus.DRAFT,
                confirmed_by=admin.id if is_paid else None,
                confirmed_at=paid_date or (invoice_date if is_paid else None),
            )
            db.add(ar)
            ars_created += 1

        db.flush()

        for code, billed in billed_by_project.items():
            project = db.query(Project).filter(Project.code == code).first()
            if (
                project
                and billed > 0
                and (
                    (project.contract_value or Decimal("0.00")) == 0
                    or code in AR_DERIVED_CONTRACT_CODES
                    or code.startswith(("INDO-", "P01.AR.", "AR-"))
                )
            ):
                project.contract_value = billed
                projects_updated += 1

        db.commit()
        return projects_created, projects_updated, ars_created, ars_skipped
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    pc, pu, ac, askip = import_rows()
    print(f"Projects created: {pc}")
    print(f"Projects updated: {pu}")
    print(f"AR created: {ac}")
    print(f"AR skipped: {askip}")
