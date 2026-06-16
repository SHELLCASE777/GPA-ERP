"""
Seed standard salary components for GPA ERP payroll.

Run from repo root:
    PYTHONPATH=. .venv/Scripts/python.exe scripts/seed_salary_components.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import SalaryComponent, SalaryComponentType

# Standard GPA salary components
# (code, name, type, is_taxable, is_active)
COMPONENTS = [
    # ── Earnings ────────────────────────────────────────────────────────────
    ("BASIC",       "Gaji Pokok",               SalaryComponentType.BASIC,     True,  True),
    ("TPT",         "Tunjangan Posisi",          SalaryComponentType.ALLOWANCE, True,  True),
    ("TRANSPORT",   "Tunjangan Transportasi",    SalaryComponentType.ALLOWANCE, False, True),
    ("MEAL",        "Tunjangan Makan",           SalaryComponentType.ALLOWANCE, False, True),
    ("COMMUNICATION","Tunjangan Komunikasi",     SalaryComponentType.ALLOWANCE, False, True),
    ("HOUSING",     "Tunjangan Perumahan",       SalaryComponentType.ALLOWANCE, True,  True),
    ("HEALTH",      "Tunjangan Kesehatan",       SalaryComponentType.ALLOWANCE, False, True),
    ("OT",          "Upah Lembur",               SalaryComponentType.ALLOWANCE, True,  True),
    ("INCENTIVE",   "Insentif / Bonus",          SalaryComponentType.ALLOWANCE, True,  True),
    ("PROJECT_SITE","Tunjangan Site Proyek",     SalaryComponentType.ALLOWANCE, False, True),

    # ── Deductions ──────────────────────────────────────────────────────────
    ("ABSENT_CUT",  "Potongan Absensi",          SalaryComponentType.DEDUCTION, False, True),
    ("LOAN",        "Cicilan Pinjaman",           SalaryComponentType.DEDUCTION, False, True),
    ("ADVANCE",     "Kasbon / Uang Muka",         SalaryComponentType.DEDUCTION, False, True),

    # ── BPJS (auto-calculated — these are reference lines on the slip) ──────
    ("BPJS_TK_EMP", "BPJS TK Karyawan",         SalaryComponentType.BPJS,      False, True),
    ("BPJS_KES_EMP","BPJS Kesehatan Karyawan",   SalaryComponentType.BPJS,      False, True),

    # ── Tax ─────────────────────────────────────────────────────────────────
    ("PPH21",       "PPh 21",                    SalaryComponentType.TAX,       False, True),
]


def main():
    db = SessionLocal()
    try:
        created = 0
        skipped = 0
        for code, name, ctype, is_taxable, is_active in COMPONENTS:
            existing = db.query(SalaryComponent).filter(SalaryComponent.code == code).first()
            if existing:
                skipped += 1
                continue
            db.add(SalaryComponent(
                code=code,
                name=name,
                component_type=ctype,
                is_taxable=is_taxable,
                is_active=is_active,
            ))
            created += 1

        db.commit()
        print(f"Done! Created {created} components, skipped {skipped} existing.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
