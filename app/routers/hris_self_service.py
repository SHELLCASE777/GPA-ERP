"""
GPA-ERP HRIS — Self-Service Portal
/hris/me/* endpoints — scoped to the calling user's linked Employee record.

Accessible by any authenticated user who has an Employee linked via Employee.user_id.
Workers (WORKER role) use these exclusively; other roles (STAFF, PM, etc.) can
also reach them to see their own data without needing HR-admin access.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser
from app.models import (
    AttendanceRecord, Employee,
    LeaveBalance, LeaveRequest, LeaveRequestStatus, LeaveType,
    PayrollRun, PaySlip, PayrollPeriod, PayrollStatus,
    SalaryComponent, SalaryComponentType,
)

router = APIRouter(prefix="/hris/me", tags=["HRIS – Self Service"])


# ─── Helper ───────────────────────────────────────────────────────────────────

def _my_employee(cu: Any, db: Session) -> Employee:
    """Resolve the current user → their linked Employee, or 404."""
    emp = db.query(Employee).filter(Employee.user_id == cu.id).first()
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee record is linked to your account. Contact HR.",
        )
    return emp


# ─── My Profile ───────────────────────────────────────────────────────────────

@router.get("", summary="My employee profile")
def my_profile(
    cu: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    emp = _my_employee(cu, db)
    dept = emp.department
    grade = emp.job_grade
    return {
        "id":           emp.id,
        "employee_no":  emp.employee_no,
        "full_name":    emp.full_name,
        "email":        emp.email,
        "phone":        emp.phone,
        "tipe":         emp.tipe.value,
        "status":       emp.status.value,
        "site":         emp.site,
        "join_date":    emp.join_date.isoformat() if emp.join_date else None,
        "department":   {"id": dept.id, "name": dept.name} if dept else None,
        "grade":        {"id": grade.id, "name": grade.name, "level": grade.level} if grade else None,
        "bank_name":    emp.bank_name,
        "bank_account": emp.bank_account,
        "photo_url":    emp.photo_url,
    }


# ─── My Attendance ────────────────────────────────────────────────────────────

@router.get("/attendance", summary="My attendance records")
def my_attendance(
    cu: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    year:  int = Query(default=None),
    month: int = Query(default=None),
    limit: int = Query(default=31, le=100),
) -> dict:
    emp = _my_employee(cu, db)
    today = date.today()
    y = year  or today.year
    m = month or today.month

    q = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.employee_id == emp.id)
    )

    # Filter to the requested month
    from sqlalchemy import extract
    q = q.filter(
        extract("year",  AttendanceRecord.date) == y,
        extract("month", AttendanceRecord.date) == m,
    ).order_by(AttendanceRecord.date.desc()).limit(limit)

    records = q.all()

    # Today's record for clock-in/out state
    today_rec = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == emp.id,
        AttendanceRecord.date == today,
    ).first()

    def _fmt(r: AttendanceRecord) -> dict:
        return {
            "id":                       r.id,
            "date":                     r.date.isoformat(),
            "clock_in":                 r.clock_in.isoformat() if r.clock_in else None,
            "clock_out":                r.clock_out.isoformat() if r.clock_out else None,
            "hours_regular":            float(r.hours_regular or 0),
            "hours_overtime_weekday":   float(r.hours_overtime_weekday or 0),
            "hours_overtime_weekend":   float(r.hours_overtime_weekend or 0),
            "hours_overtime_holiday":   float(r.hours_overtime_holiday or 0),
            "source":                   r.source.value if r.source else None,
            "face_verified":            r.face_verified,
            "face_confidence":          r.face_confidence,
            "latitude":                 float(r.latitude)  if r.latitude  else None,
            "longitude":                float(r.longitude) if r.longitude else None,
            "note":                     r.note,
        }

    # Summary: working days, total hours this month
    total_hours = sum(
        float(r.hours_regular or 0) + float(r.hours_overtime_weekday or 0)
        + float(r.hours_overtime_weekend or 0) + float(r.hours_overtime_holiday or 0)
        for r in records
    )

    return {
        "year":        y,
        "month":       m,
        "employee_id": emp.id,
        "today": _fmt(today_rec) if today_rec else None,
        "clock_state": (
            "clocked_out"  if today_rec and today_rec.clock_out else
            "clocked_in"   if today_rec and today_rec.clock_in  else
            "not_clocked_in"
        ),
        "summary": {
            "working_days":  len(records),
            "total_hours":   round(total_hours, 2),
        },
        "records": [_fmt(r) for r in records],
    }


# ─── My Leave ─────────────────────────────────────────────────────────────────

@router.get("/leave-balance", summary="My leave balances for the current year")
def my_leave_balance(
    cu: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    year: int = Query(default=None),
) -> list[dict]:
    emp = _my_employee(cu, db)
    y = year or date.today().year

    rows = (
        db.query(LeaveBalance, LeaveType)
        .join(LeaveType, LeaveBalance.leave_type_id == LeaveType.id)
        .filter(
            LeaveBalance.employee_id == emp.id,
            LeaveBalance.year == y,
        )
        .all()
    )

    return [
        {
            "leave_type_id":    lt.id,
            "code":             lt.code,
            "name":             lt.name,
            "is_paid":          lt.is_paid,
            "max_days":         lt.max_days_per_year,
            "accrued":          float(bal.accrued or 0),
            "used":             float(bal.used or 0),
            "remaining":        float((bal.accrued or 0) - (bal.used or 0)),
            "year":             y,
        }
        for bal, lt in rows
    ]


@router.get("/leave-requests", summary="My leave request history")
def my_leave_requests(
    cu: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    status: str | None = Query(default=None),
    limit:  int        = Query(default=20, le=50),
) -> list[dict]:
    emp = _my_employee(cu, db)

    q = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.employee_id == emp.id)
        .order_by(LeaveRequest.created_at.desc())
    )
    if status:
        try:
            q = q.filter(LeaveRequest.status == LeaveRequestStatus(status))
        except ValueError:
            raise HTTPException(400, f"Invalid status: {status}")
    requests = q.limit(limit).all()

    def _fmt(r: LeaveRequest) -> dict:
        lt = db.get(LeaveType, r.leave_type_id)
        return {
            "id":           r.id,
            "leave_type":   {"id": lt.id, "name": lt.name} if lt else None,
            "start_date":   r.start_date.isoformat(),
            "end_date":     r.end_date.isoformat(),
            "days":         r.days,
            "reason":       r.reason,
            "status":       r.status.value,
            "submitted_at": r.created_at.isoformat() if r.created_at else None,
            "approval_history": r.approval_history or [],
        }

    return [_fmt(r) for r in requests]


# ─── My Payslips ──────────────────────────────────────────────────────────────

@router.get("/payslips", summary="My payslip list")
def my_payslips(
    cu: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=12, le=24),
) -> list[dict]:
    emp = _my_employee(cu, db)

    rows = (
        db.query(PayrollRun, PayrollPeriod)
        .join(PayrollPeriod, PayrollRun.period_id == PayrollPeriod.id)
        .filter(
            PayrollRun.employee_id == emp.id,
            PayrollPeriod.status == PayrollStatus.POSTED,
        )
        .order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc())
        .limit(limit)
        .all()
    )

    def _fmt(run: PayrollRun, period: PayrollPeriod) -> dict:
        slip = db.query(PaySlip).filter(PaySlip.run_id == run.id).first()
        return {
            "run_id":           run.id,
            "year":             period.year,
            "month":            period.month,
            "period_label":     f"{period.year}-{period.month:02d}",
            "gross_salary":     float(run.gross_salary or 0),
            "net_salary":       float(run.net_salary or 0),
            "bpjs_tk_employee": float(run.bpjs_tk_employee or 0),
            "bpjs_kes_employee":float(run.bpjs_kes_employee or 0),
            "pph21_amount":     float(run.pph21_amount or 0),
            "thr_amount":       float(run.thr_amount or 0) if run.thr_amount else None,
            "pdf_url":          slip.pdf_url if slip else None,
            "has_pdf":          slip is not None and bool(slip.pdf_url),
        }

    return [_fmt(run, period) for run, period in rows]


@router.get("/payslips/{run_id}", summary="My payslip detail (full breakdown)")
def my_payslip_detail(
    run_id: int,
    cu: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    emp = _my_employee(cu, db)

    run = db.query(PayrollRun).filter(
        PayrollRun.id == run_id,
        PayrollRun.employee_id == emp.id,   # ownership check
    ).first()
    if not run:
        raise HTTPException(404, "Payslip not found")

    period = db.get(PayrollPeriod, run.period_id)
    if period.status != PayrollStatus.POSTED:
        raise HTTPException(403, "Payslip not yet released")

    slip = db.query(PaySlip).filter(PaySlip.run_id == run.id).first()

    # Resolve component names from snapshot
    snapshot: list[dict] = run.components_snapshot or []
    enriched = []
    for item in snapshot:
        comp = db.get(SalaryComponent, item.get("component_id"))
        enriched.append({
            **item,
            "component_name": comp.name if comp else item.get("component_id"),
            "component_type": comp.component_type.value if comp else None,
        })

    return {
        "run_id":             run.id,
        "year":               period.year,
        "month":              period.month,
        "period_label":       f"{period.year}-{period.month:02d}",
        "employee": {
            "id":          emp.id,
            "employee_no": emp.employee_no,
            "full_name":   emp.full_name,
            "bank_name":   emp.bank_name,
            "bank_account":emp.bank_account,
        },
        "gross_salary":       float(run.gross_salary or 0),
        "net_salary":         float(run.net_salary or 0),
        "bpjs_tk_employee":   float(run.bpjs_tk_employee or 0),
        "bpjs_tk_employer":   float(run.bpjs_tk_employer or 0),
        "bpjs_kes_employee":  float(run.bpjs_kes_employee or 0),
        "bpjs_kes_employer":  float(run.bpjs_kes_employer or 0),
        "pph21_amount":       float(run.pph21_amount or 0),
        "pph21_method":       run.pph21_method.value if run.pph21_method else None,
        "thr_amount":         float(run.thr_amount or 0) if run.thr_amount else None,
        "components":         enriched,
        "pdf_url":            slip.pdf_url if slip else None,
    }
