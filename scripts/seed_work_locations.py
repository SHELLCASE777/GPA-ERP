"""
GPA-ERP — Seed default work locations.

Seeds two locations:
  1. Home Office (Jakarta) — radius 60m, type: home_office
  2. Site (Berau, Kalimantan Timur) — radius 2000m, type: site

After seeding, assigns STAFF employees to Home Office and WORKER employees to Site
(only if they don't already have a work_location_id assigned).

Run: PYTHONPATH=. .venv/Scripts/python.exe scripts/seed_work_locations.py
"""
from decimal import Decimal

from app.database import SessionLocal
from app.models import Employee, EmploymentType, RoleName, User, WorkLocation, WorkLocationType

LOCATIONS = [
    {
        "name":          "Home Office — Jakarta",
        "location_type": WorkLocationType.HOME_OFFICE,
        "latitude":      Decimal("-6.238840"),
        "longitude":     Decimal("106.809590"),
        "radius_meters": 60,
        "is_active":     True,
    },
    {
        "name":          "Site — Berau, Kaltim",
        "location_type": WorkLocationType.SITE,
        "latitude":      Decimal("2.010866"),
        "longitude":     Decimal("117.728189"),
        "radius_meters": 2000,
        "is_active":     True,
    },
]


def seed(db):
    wl_map: dict[str, WorkLocation] = {}

    for loc in LOCATIONS:
        existing = db.query(WorkLocation).filter(WorkLocation.name == loc["name"]).first()
        if existing:
            print(f"  [skip] '{loc['name']}' already exists (id={existing.id})")
            wl_map[loc["location_type"].value] = existing
        else:
            wl = WorkLocation(**loc)
            db.add(wl)
            db.flush()
            print(f"  [created] '{wl.name}' id={wl.id} radius={wl.radius_meters}m")
            wl_map[loc["location_type"].value] = wl

    db.commit()

    # Auto-assign employees without a work location based on their linked user's role
    home_office = wl_map.get(WorkLocationType.HOME_OFFICE.value)
    site        = wl_map.get(WorkLocationType.SITE.value)

    employees = db.query(Employee).filter(Employee.work_location_id == None).all()
    assigned = 0

    for emp in employees:
        if emp.user_id is None:
            continue
        user = db.query(User).filter(User.id == emp.user_id).first()
        if user is None:
            continue
        role = user.role.name
        if role == RoleName.WORKER and site:
            emp.work_location_id = site.id
            assigned += 1
            print(f"  [assign] {emp.full_name} (WORKER) -> {site.name}")
        elif role == RoleName.STAFF and home_office:
            emp.work_location_id = home_office.id
            assigned += 1
            print(f"  [assign] {emp.full_name} (STAFF) -> {home_office.name}")

    db.commit()
    print(f"\nDone. Work locations seeded. Auto-assigned: {assigned} employees.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Seeding work locations...\n")
        seed(db)
    finally:
        db.close()
