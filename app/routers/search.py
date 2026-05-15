"""
GPA-ERP — Global search endpoint.
Returns top-N results per entity group in a single call.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser
from app.models import (
    AccountReceivable, Expense, InventoryItem,
    LegalDocument, Project,
)

router = APIRouter(prefix="/search", tags=["Search"])

_LIMIT = 5  # results per group


@router.get("", summary="Global cross-entity search")
def global_search(
    current_user: CurrentUser,
    db:           Annotated[Session, Depends(get_db)],
    q:            str = Query(..., min_length=1, max_length=200),
    limit:        int = Query(_LIMIT, ge=1, le=20),
):
    like = f"%{q}%"

    projects = (
        db.query(Project.id, Project.code, Project.name, Project.status)
        .filter(
            Project.name.ilike(like) | Project.code.ilike(like),
            Project.is_archived == False,  # noqa: E712
        )
        .order_by(Project.code)
        .limit(limit)
        .all()
    )

    expenses = (
        db.query(Expense.id, Expense.description, Expense.amount, Expense.status)
        .filter(Expense.description.ilike(like))
        .order_by(Expense.id.desc())
        .limit(limit)
        .all()
    )

    receivables = (
        db.query(
            AccountReceivable.id,
            AccountReceivable.invoice_no,
            AccountReceivable.customer_name,
            AccountReceivable.amount,
            AccountReceivable.status,
        )
        .filter(
            AccountReceivable.invoice_no.ilike(like)
            | AccountReceivable.customer_name.ilike(like)
        )
        .order_by(AccountReceivable.id.desc())
        .limit(limit)
        .all()
    )

    legal_docs = (
        db.query(
            LegalDocument.id,
            LegalDocument.doc_number,
            LegalDocument.title,
            LegalDocument.doc_type,
            LegalDocument.status,
        )
        .filter(
            LegalDocument.doc_number.ilike(like) | LegalDocument.title.ilike(like)
        )
        .order_by(LegalDocument.created_at.desc())
        .limit(limit)
        .all()
    )

    inventory = (
        db.query(
            InventoryItem.id,
            InventoryItem.code,
            InventoryItem.name,
            InventoryItem.category,
            InventoryItem.qty_on_hand,
            InventoryItem.unit,
        )
        .filter(
            InventoryItem.name.ilike(like) | InventoryItem.code.ilike(like),
            InventoryItem.is_active == True,  # noqa: E712
        )
        .order_by(InventoryItem.name)
        .limit(limit)
        .all()
    )

    def _row(r):
        return dict(zip(r._fields, r))

    return {
        "projects":    [_row(r) for r in projects],
        "expenses":    [_row(r) for r in expenses],
        "receivables": [_row(r) for r in receivables],
        "legal_docs":  [_row(r) for r in legal_docs],
        "inventory":   [_row(r) for r in inventory],
    }
