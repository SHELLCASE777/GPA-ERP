"""
GPA-ERP HRIS — Phase H1: Data Karyawan & Organisasi
Endpoints for employees, departments, and job grades.
"""
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.audit import model_to_dict, write_audit
from app.database import get_db
from app.dependencies import CurrentUser, get_client_ip, require_role
from app.models import (
    Department, EmpDocType, Employee, EmployeeDocument,
    JobGrade, RoleName,
)
from app.schemas import (
    DepartmentCreate, DepartmentResponse, DepartmentUpdate,
    EmployeeCreate, EmployeeDocumentResponse, EmployeeResponse, EmployeeUpdate,
    JobGradeCreate, JobGradeResponse, JobGradeUpdate,
    MessageResponse, PaginatedResponse,
)

router = APIRouter(prefix="/hris", tags=["HRIS – Employees"])

# Roles allowed to manage HRIS data
_hr_roles = (RoleName.SUPER_ADMIN, RoleName.MD)

_UPLOADS_DIR = Path("uploads") / "employee_docs"
_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

_PHOTO_DIR = Path("uploads") / "employee_photos"
_PHOTO_DIR.mkdir(parents=True, exist_ok=True)

_ALLOWED_EXTS = {".pdf", ".jpg", ".jpeg", ".png"}


# ─── Departments ─────────────────────────────────────────────────────────────

@router.get("/departments", response_model=list[DepartmentResponse], summary="List departments")
def list_departments(
    _:  CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = True,
):
    q = db.query(Department)
    if active_only:
        q = q.filter(Department.is_active == True)
    return q.order_by(Department.code).all()


@router.post("/departments", response_model=DepartmentResponse, status_code=201,
             summary="Create department")
def create_department(
    request:      Request,
    payload:      DepartmentCreate,
    current_user: Annotated[CurrentUser, Depends(require_role(*_hr_roles))],
    db:           Annotated[Session, Depends(get_db)],
):
    if db.query(Department).filter(Department.code == payload.code).first():
        raise HTTPException(409, "Department code already exists")
    if payload.parent_id:
        parent = db.query(Department).filter(Department.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(404, "Parent department not found")

    dept = Department(**payload.model_dump())
    db.add(dept)
    db.flush()
    write_audit(db, "Department", dept.id, "CREATE",
                changed_by=current_user.id, ip_address=get_client_ip(request),
                after=model_to_dict(dept))
    db.commit()
    db.refresh(dept)
    return dept


@router.patch("/departments/{dept_id}", response_model=DepartmentResponse,
              summary="Update department")
def update_department(
    dept_id:      int,
    request:      Request,
    payload:      DepartmentUpdate,
    current_user: Annotated[CurrentUser, Depends(require_role(*_hr_roles))],
    db:           Annotated[Session, Depends(get_db)],
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(404, "Department not found")

    updates = payload.model_dump(exclude_unset=True)
    if "code" in updates:
        existing = db.query(Department).filter(
            Department.code == updates["code"], Department.id != dept_id
        ).first()
        if existing:
            raise HTTPException(409, "Department code already exists")

    before = model_to_dict(dept)
    for k, v in updates.items():
        setattr(dept, k, v)
    write_audit(db, "Department", dept.id, "UPDATE",
                changed_by=current_user.id, ip_address=get_client_ip(request),
                before=before, after=model_to_dict(dept))
    db.commit()
    db.refresh(dept)
    return dept


# ─── Job Grades ──────────────────────────────────────────────────────────────

@router.get("/job-grades", response_model=list[JobGradeResponse], summary="List job grades")
def list_job_grades(
    _:  CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = True,
):
    q = db.query(JobGrade)
    if active_only:
        q = q.filter(JobGrade.is_active == True)
    return q.order_by(JobGrade.level, JobGrade.code).all()


@router.post("/job-grades", response_model=JobGradeResponse, status_code=201,
             summary="Create job grade")
def create_job_grade(
    request:      Request,
    payload:      JobGradeCreate,
    current_user: Annotated[CurrentUser, Depends(require_role(*_hr_roles))],
    db:           Annotated[Session, Depends(get_db)],
):
    if db.query(JobGrade).filter(JobGrade.code == payload.code).first():
        raise HTTPException(409, "Job grade code already exists")

    grade = JobGrade(**payload.model_dump())
    db.add(grade)
    db.flush()
    write_audit(db, "JobGrade", grade.id, "CREATE",
                changed_by=current_user.id, ip_address=get_client_ip(request),
                after=model_to_dict(grade))
    db.commit()
    db.refresh(grade)
    return grade


@router.patch("/job-grades/{grade_id}", response_model=JobGradeResponse,
              summary="Update job grade")
def update_job_grade(
    grade_id:     int,
    request:      Request,
    payload:      JobGradeUpdate,
    current_user: Annotated[CurrentUser, Depends(require_role(*_hr_roles))],
    db:           Annotated[Session, Depends(get_db)],
):
    grade = db.query(JobGrade).filter(JobGrade.id == grade_id).first()
    if not grade:
        raise HTTPException(404, "Job grade not found")

    updates = payload.model_dump(exclude_unset=True)
    if "code" in updates:
        existing = db.query(JobGrade).filter(
            JobGrade.code == updates["code"], JobGrade.id != grade_id
        ).first()
        if existing:
            raise HTTPException(409, "Job grade code already exists")

    before = model_to_dict(grade)
    for k, v in updates.items():
        setattr(grade, k, v)
    write_audit(db, "JobGrade", grade.id, "UPDATE",
                changed_by=current_user.id, ip_address=get_client_ip(request),
                before=before, after=model_to_dict(grade))
    db.commit()
    db.refresh(grade)
    return grade


# ─── Employees ───────────────────────────────────────────────────────────────

@router.get("/employees", response_model=PaginatedResponse[EmployeeResponse],
            summary="List employees")
def list_employees(
    _:           CurrentUser,
    db:          Annotated[Session, Depends(get_db)],
    search:      str | None  = None,
    dept_id:     int | None  = None,
    tipe:        str | None  = None,
    status:      str | None  = None,
    skip:        int         = 0,
    limit:       int         = 50,
):
    from app.models import EmploymentType, EmployeeStatus
    q = db.query(Employee)
    if search:
        like = f"%{search}%"
        from sqlalchemy import or_
        q = q.filter(or_(
            Employee.full_name.ilike(like),
            Employee.employee_no.ilike(like),
            Employee.nik.ilike(like),
            Employee.email.ilike(like),
        ))
    if dept_id:
        q = q.filter(Employee.dept_id == dept_id)
    if tipe:
        try:
            q = q.filter(Employee.tipe == EmploymentType(tipe))
        except ValueError:
            pass
    if status:
        try:
            q = q.filter(Employee.status == EmployeeStatus(status))
        except ValueError:
            pass

    total = q.count()
    items = q.order_by(Employee.full_name).offset(skip).limit(limit).all()
    return PaginatedResponse(items=items, total=total)


@router.post("/employees", response_model=EmployeeResponse, status_code=201,
             summary="Create employee")
def create_employee(
    request:      Request,
    payload:      EmployeeCreate,
    current_user: Annotated[CurrentUser, Depends(require_role(*_hr_roles))],
    db:           Annotated[Session, Depends(get_db)],
):
    if db.query(Employee).filter(Employee.employee_no == payload.employee_no).first():
        raise HTTPException(409, "Employee number already exists")
    if payload.nik and db.query(Employee).filter(Employee.nik == payload.nik).first():
        raise HTTPException(409, "NIK already registered")
    if payload.user_id:
        if db.query(Employee).filter(
            Employee.user_id == payload.user_id, Employee.id != -1
        ).first():
            raise HTTPException(409, "User already linked to another employee")

    emp = Employee(**payload.model_dump())
    db.add(emp)
    db.flush()
    write_audit(db, "Employee", emp.id, "CREATE",
                changed_by=current_user.id, ip_address=get_client_ip(request),
                after=model_to_dict(emp))
    db.commit()
    db.refresh(emp)
    return emp


@router.get("/employees/{emp_id}", response_model=EmployeeResponse,
            summary="Get employee detail")
def get_employee(
    emp_id: int,
    _:      CurrentUser,
    db:     Annotated[Session, Depends(get_db)],
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    return emp


@router.patch("/employees/{emp_id}", response_model=EmployeeResponse,
              summary="Update employee")
def update_employee(
    emp_id:       int,
    request:      Request,
    payload:      EmployeeUpdate,
    current_user: Annotated[CurrentUser, Depends(require_role(*_hr_roles))],
    db:           Annotated[Session, Depends(get_db)],
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")

    updates = payload.model_dump(exclude_unset=True)
    if "nik" in updates and updates["nik"]:
        existing = db.query(Employee).filter(
            Employee.nik == updates["nik"], Employee.id != emp_id
        ).first()
        if existing:
            raise HTTPException(409, "NIK already registered to another employee")

    before = model_to_dict(emp)
    for k, v in updates.items():
        setattr(emp, k, v)
    write_audit(db, "Employee", emp.id, "UPDATE",
                changed_by=current_user.id, ip_address=get_client_ip(request),
                before=before, after=model_to_dict(emp))
    db.commit()
    db.refresh(emp)
    return emp


@router.post("/employees/{emp_id}/photo", summary="Upload employee photo")
async def upload_employee_photo(
    emp_id:       int,
    file:         UploadFile,
    current_user: Annotated[CurrentUser, Depends(require_role(*_hr_roles))],
    db:           Annotated[Session, Depends(get_db)],
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")

    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(400, "Photo must be JPEG or PNG")

    dest = _PHOTO_DIR / f"{emp_id}{ext}"
    data = await file.read()
    dest.write_bytes(data)

    emp.photo_url = f"/uploads/employee_photos/{emp_id}{ext}"
    db.commit()
    return {"url": emp.photo_url}


@router.post("/employees/{emp_id}/documents",
             response_model=EmployeeDocumentResponse, status_code=201,
             summary="Upload employee document")
async def upload_employee_document(
    emp_id:       int,
    doc_type:     EmpDocType,
    file:         UploadFile,
    current_user: Annotated[CurrentUser, Depends(require_role(*_hr_roles))],
    db:           Annotated[Session, Depends(get_db)],
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")

    ext = Path(file.filename or "").suffix.lower()
    if ext not in _ALLOWED_EXTS:
        raise HTTPException(400, f"Allowed file types: {', '.join(_ALLOWED_EXTS)}")

    import uuid
    filename = f"{emp_id}_{doc_type.value}_{uuid.uuid4().hex[:8]}{ext}"
    dest = _UPLOADS_DIR / filename
    data = await file.read()
    dest.write_bytes(data)

    doc = EmployeeDocument(
        employee_id=emp_id,
        doc_type=doc_type,
        file_url=f"/uploads/employee_docs/{filename}",
    )
    db.add(doc)
    db.flush()
    write_audit(db, "EmployeeDocument", doc.id, "CREATE",
                changed_by=current_user.id, ip_address=None,
                after={"employee_id": emp_id, "doc_type": doc_type.value})
    db.commit()
    db.refresh(doc)
    return doc
