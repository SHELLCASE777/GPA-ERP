# GPA-ERP — Entity Relationship Diagram

## ERD (Mermaid)

```mermaid
erDiagram

    %% ── Auth & Access ──────────────────────────────────────────────────────────
    roles {
        int id PK
        enum name "SUPER_ADMIN|MD|PM|COST_CONTROL|FINANCE|GA|STAFF"
    }

    users {
        int id PK
        string email UK
        string hashed_password
        string full_name
        int role_id FK
        bool is_active
        datetime created_at
        datetime updated_at
    }

    app_menus {
        int id PK
        string key UK
        string label
        string section
        string path
        string description
        int sort_order
        bool is_active
        datetime created_at
        datetime updated_at
    }

    user_menu_permissions {
        int id PK
        int user_id FK
        int menu_id FK
        bool can_access
        datetime created_at
        datetime updated_at
    }

    %% ── Projects & Cost Structure ──────────────────────────────────────────────
    projects {
        int id PK
        string code UK
        string name
        decimal contract_value
        string currency "IDR default"
        bool is_archived
        datetime start_date
        datetime end_date
        enum status "active|completed|on_hold|cancelled"
        datetime imported_at
        datetime created_at
        datetime updated_at
    }

    cost_codes {
        int id PK
        string code UK
        string name
        int parent_id FK "self-ref"
        enum category "Direct|Site|Personnel|Overhead|Other"
        bool is_active
        datetime created_at
        datetime updated_at
    }

    cost_centres {
        int id PK
        string code UK
        string name
        string description
        bool is_active
        datetime created_at
        datetime updated_at
    }

    approval_rules {
        int id PK
        decimal min_amount
        decimal max_amount "nullable = no upper bound"
        enum cost_code_category "nullable = any category"
        enum required_role
        int priority
        bool is_active
        datetime created_at
        datetime updated_at
    }

    project_documents {
        int id PK
        int project_id FK
        string doc_type
        string title
        string file_path
        string reference_no
        datetime created_at
        datetime updated_at
    }

    %% ── Revenue ────────────────────────────────────────────────────────────────
    account_receivables {
        int id PK
        int project_id FK
        decimal amount
        string description
        string invoice_no
        string customer_name
        datetime invoice_date
        datetime due_date
        decimal expected_payment
        decimal actual_payment
        decimal remaining_amount
        datetime paid_at
        enum status "draft|confirmed"
        int confirmed_by FK
        datetime confirmed_at
        datetime created_at
        datetime updated_at
    }

    %% ── Expenses ───────────────────────────────────────────────────────────────
    expenses {
        int id PK
        int project_id FK
        int cost_code_id FK
        int cost_centre_id FK "nullable"
        int petty_cash_line_id FK "nullable"
        decimal amount
        string description
        string receipt_url
        enum status "draft|submitted|verified|approved|paid|hard_locked|rejected"
        int submitted_by FK
        int verified_by FK
        int approved_by FK
        int paid_by FK
        string current_approver_role
        jsonb approval_chain "ordered list of RoleNames"
        int approval_step
        jsonb approval_history "list of action records"
        string rejection_reason
        datetime created_at
        datetime updated_at
    }

    %% ── Petty Cash ─────────────────────────────────────────────────────────────
    petty_cash_reports {
        int id PK
        string report_no UK
        string month "YYYY-MM"
        int project_id FK
        int cost_code_id FK
        int cost_centre_id FK "nullable"
        string title
        string notes
        enum status "draft|posted|void"
        decimal total_amount
        int created_by FK
        datetime posted_at
        datetime created_at
        datetime updated_at
    }

    petty_cash_report_lines {
        int id PK
        int report_id FK
        int line_no
        date spent_on
        string description
        decimal amount
        string receipt_url
        string source
        string ocr_text
        datetime created_at
        datetime updated_at
    }

    %% ── Legal Documents ────────────────────────────────────────────────────────
    legal_documents {
        int id PK
        string doc_number UK
        string reference_number
        enum doc_type "proposal|berita_acara|surat_jalan|other"
        enum status "draft|submitted|signed|rejected"
        string title
        string recipient_name
        string recipient_company
        string recipient_address
        string subject
        text body
        string closing
        decimal quoted_amount
        int project_id FK "nullable"
        string rejection_note
        int signed_by FK "nullable"
        datetime signed_at
        int created_by FK
        datetime created_at
        datetime updated_at
    }

    %% ── Inventory ──────────────────────────────────────────────────────────────
    inventory_items {
        int id PK
        string code UK
        string name
        enum category "materials|tools|consumables"
        string unit
        decimal qty_on_hand
        decimal min_stock
        decimal unit_cost
        string location
        string notes
        bool is_active
        datetime created_at
        datetime updated_at
    }

    inventory_txns {
        int id PK
        int item_id FK
        enum txn_type "in|out|adjustment"
        decimal quantity
        string reference
        string notes
        int project_id FK "nullable"
        int created_by FK
        datetime created_at
    }

    %% ── Audit ──────────────────────────────────────────────────────────────────
    audit_logs {
        int id PK
        string entity_type
        int entity_id
        string action
        jsonb before_state
        jsonb after_state
        int changed_by FK "nullable"
        string ip_address
        datetime created_at
    }

    %% ── Relationships ──────────────────────────────────────────────────────────

    roles                   ||--o{ users                    : "has"
    users                   ||--o{ user_menu_permissions    : "has"
    app_menus               ||--o{ user_menu_permissions    : "controls"

    projects                ||--o{ account_receivables      : "has"
    projects                ||--o{ expenses                 : "has"
    projects                ||--o{ project_documents        : "has"
    projects                ||--o{ petty_cash_reports       : "has"
    projects                ||--o{ inventory_txns           : "linked to"
    projects                }o--o| legal_documents          : "optionally linked"

    cost_codes              }o--o| cost_codes               : "parent/child (self-ref)"
    cost_codes              ||--o{ expenses                 : "categorises"
    cost_codes              ||--o{ petty_cash_reports       : "categorises"

    cost_centres            ||--o{ expenses                 : "groups"
    cost_centres            ||--o{ petty_cash_reports       : "groups"

    expenses                }o--o| petty_cash_report_lines  : "generated from"

    petty_cash_reports      ||--o{ petty_cash_report_lines  : "has"
    petty_cash_reports      }o--|| users                    : "created_by"

    inventory_items         ||--o{ inventory_txns           : "has"

    users                   ||--o{ expenses                 : "submitted_by"
    users                   ||--o{ expenses                 : "verified_by"
    users                   ||--o{ expenses                 : "approved_by"
    users                   ||--o{ expenses                 : "paid_by"
    users                   ||--o{ account_receivables      : "confirmed_by"
    users                   ||--o{ inventory_txns           : "created_by"
    users                   ||--o{ legal_documents          : "created_by"
    users                   ||--o{ legal_documents          : "signed_by"
    users                   }o--o| audit_logs               : "changed_by"
```

---

## Table Summary

| Table | Rows (expected) | Key Indices |
|---|---|---|
| `roles` | 7 (fixed enum) | `name` UK |
| `users` | Low (10–100) | `email` UK, `role_id` |
| `app_menus` | ~12 (fixed) | `key` UK, `section+sort_order` |
| `user_menu_permissions` | users × menus | `user_id+menu_id` UK |
| `projects` | Medium (10–500) | `code` UK, `status` |
| `cost_codes` | Low (20–200) | `code` UK, self-ref `parent_id` |
| `cost_centres` | Low (5–50) | `code` UK |
| `approval_rules` | Very low (4–20) | `priority`, `is_active` |
| `project_documents` | Medium | `project_id+doc_type` |
| `account_receivables` | Medium (100–10k) | `project_id+status`, `invoice_no` |
| `expenses` | High (1k–100k) | `project_id+status`, `current_approver_role`, `submitted_by` |
| `petty_cash_reports` | Medium | `project_id+month`, `status` |
| `petty_cash_report_lines` | High | `report_id+line_no` |
| `legal_documents` | Low-medium | `doc_number` UK, `status`, `doc_type` |
| `inventory_items` | Low (10–1000) | `code` UK, `category` |
| `inventory_txns` | High | `item_id`, `project_id` |
| `audit_logs` | Very high (append-only) | `entity_type+entity_id`, `changed_by`, `created_at` |
