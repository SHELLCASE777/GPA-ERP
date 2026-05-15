"""
GPA-ERP — Inventory & Assets router
CRUD for inventory items + stock-in / stock-out / adjustment transactions.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser, get_current_user, require_role
from app.models import InventoryItem, InventoryTxn, RoleName, TxnType, User
from app.schemas import (
    InventoryItemCreate, InventoryItemResponse, InventoryItemUpdate,
    InventoryTxnCreate, InventoryTxnResponse, MessageResponse, PaginatedResponse,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])

DB        = Annotated[Session, Depends(get_db)]
Auth      = Annotated[User,    Depends(get_current_user)]
# Mutations restricted to roles that manage physical stock
_inv_roles = (RoleName.GA, RoleName.COST_CONTROL, RoleName.PM, RoleName.MD, RoleName.SUPER_ADMIN)
InvWrite  = Annotated[User,    Depends(require_role(*_inv_roles))]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_item_or_404(item_id: int, db: Session) -> InventoryItem:
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    return item


def _apply_txn(item: InventoryItem, txn: InventoryTxnCreate) -> None:
    if txn.txn_type == TxnType.IN:
        item.qty_on_hand += txn.quantity
    elif txn.txn_type == TxnType.OUT:
        if item.qty_on_hand < txn.quantity:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Insufficient stock: have {item.qty_on_hand} {item.unit}, need {txn.quantity}",
            )
        item.qty_on_hand -= txn.quantity
    else:
        item.qty_on_hand = txn.quantity


# ── Item endpoints ────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse[InventoryItemResponse])
def list_items(
    db:          DB,
    _:           Auth,
    category:    str | None = Query(None),
    low_stock:   bool       = Query(False),
    active_only: bool       = Query(True),
    q:           str | None = Query(None),
    skip:        int        = Query(0, ge=0),
    limit:       int        = Query(50, ge=1, le=200),
):
    query = db.query(InventoryItem)
    if active_only:
        query = query.filter(InventoryItem.is_active == True)
    if category:
        query = query.filter(InventoryItem.category == category)
    if low_stock:
        query = query.filter(InventoryItem.qty_on_hand <= InventoryItem.min_stock)
    if q:
        like = f"%{q}%"
        query = query.filter(
            InventoryItem.name.ilike(like) | InventoryItem.code.ilike(like)
        )
    total = query.count()
    items = query.order_by(InventoryItem.category, InventoryItem.name).offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.post("", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(payload: InventoryItemCreate, db: DB, _: InvWrite):
    if db.query(InventoryItem).filter(InventoryItem.code == payload.code).first():
        raise HTTPException(status.HTTP_409_CONFLICT, f"Item code '{payload.code}' already exists")
    item = InventoryItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_item(item_id: int, db: DB, _: Auth):
    return _get_item_or_404(item_id, db)


@router.patch("/{item_id}", response_model=InventoryItemResponse)
def update_item(item_id: int, payload: InventoryItemUpdate, db: DB, _: InvWrite):
    item = _get_item_or_404(item_id, db)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", response_model=MessageResponse)
def delete_item(item_id: int, db: DB, _: InvWrite):
    item = _get_item_or_404(item_id, db)
    item.is_active = False
    db.commit()
    return {"message": "Item deactivated"}


# ── Transaction endpoints ─────────────────────────────────────────────────────

@router.post("/{item_id}/txn", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def record_transaction(item_id: int, payload: InventoryTxnCreate, db: DB, user: InvWrite):
    item = _get_item_or_404(item_id, db)
    _apply_txn(item, payload)
    txn = InventoryTxn(
        item_id    = item_id,
        txn_type   = payload.txn_type,
        quantity   = payload.quantity,
        reference  = payload.reference,
        notes      = payload.notes,
        project_id = payload.project_id,
        created_by = user.id,
    )
    db.add(txn)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}/txns", response_model=list[InventoryTxnResponse])
def list_transactions(
    item_id: int,
    db:      DB,
    _:       Auth,
    limit:   int = Query(50, le=200),
):
    _get_item_or_404(item_id, db)
    return (
        db.query(InventoryTxn)
        .filter(InventoryTxn.item_id == item_id)
        .order_by(InventoryTxn.created_at.desc())
        .limit(limit)
        .all()
    )
