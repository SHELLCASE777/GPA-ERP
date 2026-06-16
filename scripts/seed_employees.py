"""
Seed script — sample departments, job grades, and employees for GPA ERP HRIS.
Run: .venv/Scripts/python.exe scripts/seed_employees.py
"""
from datetime import date, datetime, timezone
from decimal import Decimal

from app.database import SessionLocal
from app.models import (
    Department, Employee, EmployeeDocument, EmployeeStatus, EmploymentType,
    JobGrade, LeaveBalance, LeaveType,
    SalaryComponent, SalaryAssignment, SalaryComponentType,
)

db = SessionLocal()

# ─── Departments ──────────────────────────────────────────────────────────────
print("Seeding departments…")
dept_data = [
    ("MGMT",  "Manajemen"),
    ("PROJ",  "Project Management"),
    ("CC",    "Cost Control"),
    ("FIN",   "Finance & Accounting"),
    ("GA",    "General Affairs"),
    ("TECH",  "Technical Engineering"),
    ("HRD",   "Human Resources"),
    ("IT",    "Information Technology"),
]
depts = {}
for code, name in dept_data:
    d = db.query(Department).filter_by(code=code).first()
    if not d:
        d = Department(code=code, name=name, is_active=True)
        db.add(d)
        db.flush()
    depts[code] = d
db.commit()
print(f"  {len(depts)} departments ready")

# ─── Job Grades ───────────────────────────────────────────────────────────────
print("Seeding job grades…")
grade_data = [
    ("DIR",  "Direktur",           8),
    ("MGR",  "Manager",            6),
    ("SPVR", "Supervisor",         5),
    ("LEAD", "Team Lead",          4),
    ("SR",   "Senior Staff",       3),
    ("STAFF","Staff",              2),
    ("JR",   "Junior Staff",       1),
]
grades = {}
for code, name, level in grade_data:
    g = db.query(JobGrade).filter_by(code=code).first()
    if not g:
        g = JobGrade(code=code, name=name, level=level, is_active=True)
        db.add(g)
        db.flush()
    grades[code] = g
db.commit()
print(f"  {len(grades)} grades ready")

# ─── Salary components ────────────────────────────────────────────────────────
comp_basic = db.query(SalaryComponent).filter_by(code="BASIC").first()
comp_transport = db.query(SalaryComponent).filter_by(code="TRANSPORT").first()
comp_meal = db.query(SalaryComponent).filter_by(code="MEAL").first()
comp_position = db.query(SalaryComponent).filter_by(code="POSITION").first()

# ─── Employees ────────────────────────────────────────────────────────────────
print("Seeding employees…")

employees_data = [
    # (emp_no, full_name, nik, email, phone, tipe, status, dept_code, grade_code, join_date, site, basic, transport, meal, position_allow)
    ("EMP-001", "Budi Santoso",       "3201010101800001", "budi.santoso@gpa.co.id",       "081234567001", "Tetap",     "active",    "MGMT",  "DIR",  date(2018, 3, 1),  "Jakarta",  35_000_000, 1_500_000, 750_000, 5_000_000),
    ("EMP-002", "Siti Rahayu",        "3201010101850002", "siti.rahayu@gpa.co.id",        "081234567002", "Tetap",     "active",    "FIN",   "MGR",  date(2019, 5, 15), "Jakarta",  18_000_000, 1_000_000, 600_000, 2_000_000),
    ("EMP-003", "Ahmad Fauzi",        "3201010101820003", "ahmad.fauzi@gpa.co.id",        "081234567003", "Tetap",     "active",    "PROJ",  "MGR",  date(2019, 8, 1),  "Jakarta",  20_000_000, 1_200_000, 600_000, 2_500_000),
    ("EMP-004", "Dewi Lestari",       "3201010101900004", "dewi.lestari@gpa.co.id",       "081234567004", "Tetap",     "active",    "CC",    "SPVR", date(2020, 2, 1),  "Jakarta",  12_000_000,   800_000, 500_000, 1_000_000),
    ("EMP-005", "Rudi Hartono",       "3201010101880005", "rudi.hartono@gpa.co.id",       "081234567005", "Tetap",     "active",    "TECH",  "LEAD", date(2020, 6, 1),  "Surabaya", 13_500_000,   900_000, 500_000, 1_200_000),
    ("EMP-006", "Rina Wahyuni",       "3201010101920006", "rina.wahyuni@gpa.co.id",       "081234567006", "Tetap",     "active",    "HRD",   "SPVR", date(2021, 1, 15), "Jakarta",  11_000_000,   700_000, 500_000,   900_000),
    ("EMP-007", "Hendra Kusuma",      "3201010101870007", "hendra.kusuma@gpa.co.id",      "081234567007", "Tetap",     "active",    "PROJ",  "SR",   date(2020, 9, 1),  "Bandung",  10_000_000,   700_000, 450_000,   500_000),
    ("EMP-008", "Yuli Andriani",      "3201010101950008", "yuli.andriani@gpa.co.id",      "081234567008", "Tetap",     "active",    "FIN",   "STAFF",date(2022, 3, 1),  "Jakarta",   7_500_000,   600_000, 400_000,         0),
    ("EMP-009", "Eko Prasetyo",       "3201010101910009", "eko.prasetyo@gpa.co.id",       "081234567009", "PKWT",      "active",    "TECH",  "SR",   date(2021, 7, 1),  "Surabaya",  9_500_000,   700_000, 450_000,   400_000),
    ("EMP-010", "Fitri Handayani",    "3201010101930010", "fitri.handayani@gpa.co.id",    "081234567010", "Tetap",     "active",    "IT",    "LEAD", date(2021, 4, 1),  "Jakarta",  13_000_000,   800_000, 500_000, 1_100_000),
    ("EMP-011", "Agus Setiawan",      "3201010101860011", "agus.setiawan@gpa.co.id",      "081234567011", "Tetap",     "active",    "CC",    "SR",   date(2020, 11, 1), "Jakarta",  10_500_000,   700_000, 450_000,   500_000),
    ("EMP-012", "Nurul Hidayah",      "3201010101940012", "nurul.hidayah@gpa.co.id",      "081234567012", "PKWT",      "active",    "GA",    "STAFF",date(2022, 6, 1),  "Jakarta",   6_500_000,   500_000, 400_000,         0),
    ("EMP-013", "Bambang Supriyadi",  "3201010101800013", "bambang.supriyadi@gpa.co.id",  "081234567013", "Tetap",     "active",    "PROJ",  "MGR",  date(2018, 1, 1),  "Medan",    19_000_000, 1_200_000, 600_000, 2_200_000),
    ("EMP-014", "Sri Mulyani",        "3201010101890014", "sri.mulyani@gpa.co.id",        "081234567014", "Tetap",     "active",    "FIN",   "SR",   date(2020, 3, 1),  "Jakarta",   9_000_000,   650_000, 450_000,   400_000),
    ("EMP-015", "Doni Firmansyah",    "3201010101960015", "doni.firmansyah@gpa.co.id",    "081234567015", "PKWT",      "probation", "TECH",  "JR",   date(2024, 1, 15), "Surabaya",  5_500_000,   500_000, 350_000,         0),
    ("EMP-016", "Citra Dewi",         "3201010101970016", "citra.dewi@gpa.co.id",         "081234567016", "Outsource", "active",    "GA",    "STAFF",date(2023, 3, 1),  "Jakarta",   5_000_000,   400_000, 350_000,         0),
    ("EMP-017", "Wahyu Prabowo",      "3201010101840017", "wahyu.prabowo@gpa.co.id",      "081234567017", "Tetap",     "active",    "TECH",  "LEAD", date(2019, 11, 1), "Bandung",  14_000_000,   900_000, 500_000, 1_300_000),
    ("EMP-018", "Lina Marlina",       "3201010101920018", "lina.marlina@gpa.co.id",       "081234567018", "Tetap",     "active",    "HRD",   "STAFF",date(2022, 9, 1),  "Jakarta",   7_000_000,   550_000, 400_000,         0),
    ("EMP-019", "Teguh Santoso",      "3201010101910019", "teguh.santoso@gpa.co.id",      "081234567019", "PKWT",      "active",    "IT",    "SR",   date(2021, 10, 1), "Jakarta",   9_000_000,   650_000, 450_000,   400_000),
    ("EMP-020", "Maya Sari",          "3201010101980020", "maya.sari@gpa.co.id",          "081234567020", "PKWT",      "probation", "CC",    "JR",   date(2024, 3, 1),  "Jakarta",   5_500_000,   500_000, 350_000,         0),
]

tipe_map   = {"Tetap": EmploymentType.TETAP, "PKWT": EmploymentType.PKWT, "Outsource": EmploymentType.OUTSOURCE}
status_map = {"active": EmployeeStatus.ACTIVE, "probation": EmployeeStatus.PROBATION}

created = 0
for row in employees_data:
    (emp_no, full_name, nik, email, phone, tipe, status,
     dept_code, grade_code, join_date, site,
     basic, transport, meal, position_allow) = row

    exists = db.query(Employee).filter_by(employee_no=emp_no).first()
    if exists:
        continue

    emp = Employee(
        employee_no = emp_no,
        full_name   = full_name,
        nik         = nik,
        email       = email,
        phone       = phone,
        tipe        = tipe_map[tipe],
        status      = status_map[status],
        dept_id     = depts[dept_code].id,
        grade_id    = grades[grade_code].id,
        join_date   = join_date,
        site        = site,
        bank_name   = "BCA",
        bank_account= f"1234{emp_no[-3:]}0000",
    )
    db.add(emp)
    db.flush()

    today = date.today()

    # Salary assignments
    if comp_basic and basic:
        db.add(SalaryAssignment(
            employee_id=emp.id, component_id=comp_basic.id,
            amount=Decimal(basic), effective_from=join_date,
        ))
    if comp_transport and transport:
        db.add(SalaryAssignment(
            employee_id=emp.id, component_id=comp_transport.id,
            amount=Decimal(transport), effective_from=join_date,
        ))
    if comp_meal and meal:
        db.add(SalaryAssignment(
            employee_id=emp.id, component_id=comp_meal.id,
            amount=Decimal(meal), effective_from=join_date,
        ))
    if comp_position and position_allow:
        db.add(SalaryAssignment(
            employee_id=emp.id, component_id=comp_position.id,
            amount=Decimal(position_allow), effective_from=join_date,
        ))

    created += 1

db.commit()
print(f"  {created} employees created")

# ─── Leave balances ───────────────────────────────────────────────────────────
print("Seeding leave balances…")
year = date.today().year
leave_types = db.query(LeaveType).all()
employees   = db.query(Employee).all()

bal_created = 0
for emp in employees:
    for lt in leave_types:
        if lt.max_days_per_year is None:
            continue
        exists = db.query(LeaveBalance).filter_by(
            employee_id=emp.id, leave_type_id=lt.id, year=year
        ).first()
        if not exists:
            db.add(LeaveBalance(
                employee_id=emp.id,
                leave_type_id=lt.id,
                year=year,
                accrued=lt.max_days_per_year,
                used=0,
            ))
            bal_created += 1

db.commit()
print(f"  {bal_created} leave balances seeded")

# ─── Summary ─────────────────────────────────────────────────────────────────
print("\nDone!")
print(f"  Departments: {db.query(Department).count()}")
print(f"  Job Grades:  {db.query(JobGrade).count()}")
print(f"  Employees:   {db.query(Employee).count()}")
print(f"  Leave Balances: {db.query(LeaveBalance).count()}")
db.close()
