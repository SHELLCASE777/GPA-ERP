"""
GPA-ERP — Import real projects into the target database.
Idempotent: skips any project whose code already exists.
Run (e.g. in Railway Console where DATABASE_URL points at production):
    python -m scripts.import_projects_data
"""
import sys, os
from decimal import Decimal
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Project, ProjectStatus

PROJECTS = [
    {"code": 'GPA-KN-REVAMP', "name": 'Revamping PT Kertas Nusantara', "contract_value": '30360000000.00', "currency": 'IDR', "start_date": '2025-01-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.0825.316', "name": 'Additional Probe Shinkawa – PT KN', "contract_value": '3486500000.00', "currency": 'IDR', "start_date": '2025-08-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.0825.J075', "name": 'Repair & Services Control Valve & ON OFF Valve – PT KN', "contract_value": '18534066792.00', "currency": 'IDR', "start_date": '2025-08-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.0925.S489', "name": 'Replacement Instrument Defective MA 77 – PT KN', "contract_value": '1400855000.00', "currency": 'IDR', "start_date": '2025-09-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.1025.S549', "name": 'Deviation List Of Generator Overhaul 2x63MW – PT KN', "contract_value": '6081000000.00', "currency": 'IDR', "start_date": '2025-10-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.1025.S528', "name": 'Deviation Parts Turbine – PT KN', "contract_value": '2049200000.00', "currency": 'IDR', "start_date": '2025-10-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.1125.ELC', "name": 'Electrical Construction & Installation – PT KN', "contract_value": '10261000000.00', "currency": 'IDR', "start_date": '2025-11-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.1125.S680', "name": 'Overhaul Cooling Tower Pump Area MA 42 – PT KN', "contract_value": '1920000000.00', "currency": 'IDR', "start_date": '2025-11-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.1125.S690', "name": 'Proximity Switch Cable Scun & Ferrule MA 42/73 – PT KN', "contract_value": '503999600.00', "currency": 'IDR', "start_date": '2025-11-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.1125.S689', "name": 'Cable Scun & Ferrule Terminal MA 42/73 – PT KN', "contract_value": '45993150.00', "currency": 'IDR', "start_date": '2025-11-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.1125.S711', "name": 'Service & Repair Air Port Rodding Actuator MA 81 – PT KN', "contract_value": '766021500.00', "currency": 'IDR', "start_date": '2025-11-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.1225.S788', "name": 'Replacement Temperature Sensor & Thermowell – PT KN', "contract_value": '3395496000.00', "currency": 'IDR', "start_date": '2025-12-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.1225.S793', "name": 'Toxic Gas Instrumentation – PT KN', "contract_value": '511919760.00', "currency": 'IDR', "start_date": '2025-12-01T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'INDO-PEKERJAAN-SAND-B', "name": 'Pekerjaan Sand Blasting dan NDT Nozzle STG 152G01AT - Pt Indopelita Aircraft Services', "contract_value": '116000000.00', "currency": 'IDR', "start_date": '2025-03-20T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'INDO-PEKERJAAN-OVERHA', "name": 'Pekerjaan Overhaul 3 Unit Steam Turbine 101P502AT, 102P511AT, 104P505AT - Pt Indopelita Aircraft Services', "contract_value": '631000000.00', "currency": 'IDR', "start_date": '2025-03-20T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.AR.THC', "name": 'General Stock Tubing & Hose Connector (Project Restorations PTKN) - PT KN', "contract_value": '259745000.00', "currency": 'IDR', "start_date": '2026-03-02T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.AR.MPSC', "name": 'Manpower Supply for Commissioning and Start Up - PT KN', "contract_value": '2520000000.00', "currency": 'IDR', "start_date": '2026-03-10T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.AR.SCBW', "name": 'Seal for CB Washer MA 40 & MA 41 Fibre Line Area (Project Restorations PTKN), EPC 5 - PT KN', "contract_value": '800000000.00', "currency": 'IDR', "start_date": '2026-03-11T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.AR.ARBO', "name": 'Air Port Rodding Parts Recovery Boiler (Project Restorations PT KN) - PT KN', "contract_value": '208545000.00', "currency": 'IDR', "start_date": '2026-04-02T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": 'P01.AR.PGTG', "name": 'Pressure Gauge for Turbine Generator MA77 (Project Restorations PTKN) - PT KN', "contract_value": '19968000.00', "currency": 'IDR', "start_date": '2026-04-27T00:00:00+08:00', "end_date": None, "status": 'ACTIVE'},
    {"code": '001', "name": 'Manpower Extension Electrical', "contract_value": '40000000.00', "currency": 'IDR', "start_date": '2026-05-15T00:00:00+08:00', "end_date": '2026-05-30T00:00:00+08:00', "status": 'ACTIVE'},
]


def _dt(v):
    return datetime.fromisoformat(v) if v else None


def _status(v):
    # Local DB may store the enum name ('ACTIVE') or value ('active') — accept both.
    try:
        return ProjectStatus[v]
    except KeyError:
        return ProjectStatus(v)


def run():
    db = SessionLocal()
    created = skipped = 0
    try:
        existing = {c for (c,) in db.query(Project.code).all()}
        for p in PROJECTS:
            if p["code"] in existing:
                skipped += 1
                continue
            db.add(Project(
                code=p["code"],
                name=p["name"],
                contract_value=Decimal(p["contract_value"]),
                currency=p["currency"],
                start_date=_dt(p["start_date"]),
                end_date=_dt(p["end_date"]),
                status=_status(p["status"]),
                is_archived=False,
            ))
            created += 1
        db.commit()
        print(f"Projects import complete: {created} created, {skipped} skipped (already existed).")
    finally:
        db.close()


if __name__ == "__main__":
    run()
