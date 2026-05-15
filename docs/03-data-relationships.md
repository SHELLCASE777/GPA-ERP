# GPA-ERP — Data Relationship Diagram

This diagram shows how **data flows between modules** — not just foreign key links, but the business logic that connects them.

---

## High-Level Module Flow

```mermaid
flowchart TD
    subgraph Revenue["Revenue Module"]
        AR[Account Receivable\ninvoice_no · amount · status]
        AR -->|confirm| CONF[Confirmed AR\nactual_payment recorded]
    end

    subgraph Budget["Project Budget Engine"]
        CONF -->|sums into| TREV[total_revenue\nΣ confirmed ARs]
        TREV -->|minus| TCOM[total_committed\nΣ verified+approved+paid+locked expenses]
        TCOM --> BUD[project.budget\n= total_revenue − total_committed]
    end

    subgraph Spending["Spending Module"]
        EXP[Expense\ndraft · submitted] -->|submit triggers| CHAIN[Approval Chain\nbuilt from ApprovalRule matrix]
        CHAIN -->|verified → approved| COMM[Committed Expense\nverified/approved/paid/locked]
        COMM -->|counted in| TCOM
    end

    subgraph PettyCash["Petty Cash Module"]
        PCR[Petty Cash Report\ndraft · posted] --> LINES[Report Lines\nreceipts · amounts]
        PCR -->|post action\nauto-creates| EXP
    end

    subgraph Legal["Legal Module"]
        LD[Legal Document\ndraft · submitted] -->|MD or PM signs| SIGNED[Signed Document\nPDF generated]
    end

    subgraph Inventory["Inventory Module"]
        INV[Inventory Item\nqty_on_hand · min_stock] --> TXN[Transaction\nin · out · adjustment]
        TXN -.->|linked to| PROJECT
    end

    subgraph Projects["Project"]
        PROJECT[Project\ncode · name · currency · status]
    end

    PROJECT --> AR
    PROJECT --> EXP
    PROJECT --> PCR
    PROJECT -.->|optional| LD
    PROJECT --> TXN

    style Budget fill:#f0f9ff,stroke:#0369a1
    style Revenue fill:#f0fdf4,stroke:#16a34a
    style Spending fill:#fff7ed,stroke:#ea580c
    style PettyCash fill:#fdf4ff,stroke:#9333ea
```

---

## Budget Calculation Detail

```mermaid
flowchart LR
    subgraph Inputs
        AR1[AR #1\nconfirmed\n₱500,000]
        AR2[AR #2\nconfirmed\n₱300,000]
        AR3[AR #3\ndraft\n₱200,000]
    end

    subgraph Calculation
        TREV["total_revenue\n= ₱500,000 + ₱300,000\n= ₱800,000\n(draft ARs excluded)"]
        TCOM["total_committed\n= Σ expenses at\nverified/approved/paid/locked\ne.g. ₱350,000"]
        BUD["project.budget\n= ₱800,000 − ₱350,000\n= ₱450,000 available"]
    end

    AR1 --> TREV
    AR2 --> TREV
    AR3 -.->|excluded| TREV
    TREV --> BUD
    TCOM --> BUD
```

**Key rule:** Only **confirmed** ARs count toward revenue. Only expenses at `verified`, `approved`, `paid`, or `hard_locked` count toward committed spend. Draft/submitted/rejected expenses do NOT reduce the budget.

---

## Expense Approval Chain Resolution

```mermaid
flowchart TD
    SUB[User submits Expense\namount + cost_code_category] --> QUERY[Query approval_rules\nWHERE is_active=true\nORDER BY priority]
    QUERY --> MATCH{Rules matching\namount range &\ncategory?}
    MATCH -->|Yes| CHAIN[Build ordered chain\ne.g. COST_CONTROL → PM → MD]
    CHAIN -->|Store as JSONB| EXP[expense.approval_chain\napproval_step = 0\ncurrent_approver_role = COST_CONTROL]
    MATCH -->|No matching rules| AUTO[Default: COST_CONTROL only]

    EXP --> STEP1[Step 0: COST_CONTROL\nverifies → status = verified]
    STEP1 --> STEP2[Step 1: PM\napproves → step++]
    STEP2 --> STEP3[Step 2: MD\napproves → status = approved]
    STEP3 --> PAY[FINANCE marks paid\nstatus = paid]
    PAY --> LOCK[SUPER_ADMIN hard locks\nstatus = hard_locked]

    STEP1 -->|reject| BACK[status = rejected\nrejection_reason recorded\napproval_history appended]
```

---

## Petty Cash → Expense Pipeline

```mermaid
sequenceDiagram
    participant GA as GA User
    participant PC as PettyCashReport
    participant Lines as ReportLines
    participant E as Expense
    participant AP as Approval Workflow

    GA->>PC: Create report (draft)\nproject · month · cost_code
    GA->>Lines: Add line items\ndescription · amount · receipt
    GA->>PC: POST /petty-cash-reports/{id}/post
    PC->>PC: status = posted
    PC->>E: Auto-create Expense\nfor EACH line item\nstatus = draft
    Note over E: expense.petty_cash_line_id\nlinks back to source line
    GA->>E: Submit each expense
    E->>AP: Normal approval workflow begins
```

---

## Legal Document Lifecycle

```mermaid
stateDiagram-v2
    [*] --> draft : Any user creates
    draft --> submitted : User submits\n(awaiting signature)
    submitted --> signed : MD or PM signs\n(PDF generated with KOP SURAT)
    submitted --> rejected : MD or PM rejects\n(rejection_note recorded)
    rejected --> submitted : User edits & resubmits
    signed --> [*]
```

---

## Inventory ↔ Project Link

```mermaid
flowchart LR
    GA[GA User] -->|creates| TXN[InventoryTxn\ntxn_type: out\nquantity: 10]
    TXN -->|project_id FK optional| PROJECT[Project\ne.g. PRJ-001]
    TXN -->|item_id FK| ITEM[InventoryItem\nqty_on_hand auto-adjusted]
    ITEM -->|qty_on_hand < min_stock| ALERT[Low Stock Alert\nshown in UI]
```

Inventory transactions are **project-linkable but not project-required**. Items consumed on-site can reference a project; warehouse adjustments typically don't.

---

## Audit Trail Flow

```mermaid
flowchart LR
    ACTION[Any state change\ne.g. expense approved] --> AUDIT[audit.py service\nlog_action]
    AUDIT -->|captures| BEFORE[before_state JSONB\nsnapshot of old record]
    AUDIT -->|captures| AFTER[after_state JSONB\nsnapshot of new record]
    AUDIT -->|writes| LOG[AuditLog row\nentity_type · entity_id\naction · changed_by · ip_address]
    LOG -->|never updated or deleted| IMMUTABLE[Immutable append-only record]
```

The audit log is exposed read-only at `GET /vault/audit-log` and is only accessible to `SUPER_ADMIN` and `COST_CONTROL`.

---

## Cross-Module Data Summary

| Source | Feeds Into | How |
|---|---|---|
| `account_receivables` (confirmed) | `project.total_revenue` | Hybrid property sum |
| `expenses` (verified/approved/paid/locked) | `project.total_committed` | Hybrid property sum |
| `project.total_revenue − total_committed` | `project.budget` | Computed on every read |
| `petty_cash_report_lines` (when report posted) | `expenses` | Auto-created, one per line |
| `approval_rules` (at submit time) | `expense.approval_chain` | Resolved once, stored immutably |
| `inventory_txns` | `inventory_items.qty_on_hand` | Applied by router at transaction create |
| Any state change | `audit_logs` | Via `audit.py` service |
