# NN Fund Management Module

An expert-level Odoo 16 custom module designed for strict fund tracking, dynamic double-spending prevention, and multi-company financial approval workflows. Built as an assessment for the Trainee Software Developer position at NN Services & Engineering Ltd.

## Project Goal
The goal of this project is to develop an installable Odoo custom module that meticulously manages incoming funds, unassigned balances, project and expense head allocations, fund requisitions, bills against approved requisitions, and transfers. The system ensures an absolute lock against double-spending money using strict concurrency controls, "Hold" mechanisms, and a multi-level approval pipeline (GM → MD).

## Tech Stack Used
- **Backend**: Python 3.10+, Odoo 16.0 ORM, PostgreSQL 14
- **Frontend**: Odoo XML Views (Tree, Form, Kanban), Odoo Web Dashboard
- **Infrastructure**: Docker, Docker Compose
- **Version Control**: Git

---

## Table of Contents
1. [Required Module Information](#required-module-information)
2. [Requirements & Fulfillment Checklist](#requirements--fulfillment-checklist)
3. [System Architecture & Backend Logic](#system-architecture--backend-logic)
4. [Access Control and Security Files](#access-control-and-security-files)
5. [Testing Strategy & Bug Categories](#testing-strategy--bug-categories)
6. [Technical Challenges & Observations](#technical-challenges--observations)
7. [Meaningful Git Commit History](#meaningful-git-commit-history)

---

## Required Module Information

### Odoo Version
- **Target OS/Environment:** Dockerized Linux container
- **Odoo Version:** `16.0` (Community or Enterprise)

### Installation Instructions
1. **Clone the repository:**
   ```bash
   git clone https://github.com/mdazharulislamnk/nn-fund-management.git
   cd nn-fund-management
   ```
2. **Start the Docker Stack:**
   ```bash
   docker-compose up -d
   ```
3. **Access Odoo:**
   Open your browser and navigate to `http://localhost:8069`. Use the default credentials (usually `admin` / `admin`) to log in.
4. **Install the Module:**
   - Go to Apps and click "Update Apps List".
   - Search for `NN Fund Management`.
   - Click "Install".

### Required Dependencies
- **Odoo Base Apps**: `base`, `account` (Invoicing), `board` (Dashboards), `mail` (Messaging & Threading).
- **Python libraries**: Standard library (`re`, `logging`). No external pip dependencies are required.

### Configuration Steps
1. Navigate to **Settings → Users & Companies**.
2. Create or assign users to the new Fund Management groups (e.g., *Fund User*, *GM Approver*, *MD Approver*, *Finance User*, *Fund Administrator*).
3. Ensure the multi-company setting is enabled if testing across different company environments.

### Testing Instructions
To execute the automated 13-step business scenario test, run the following command against the running docker container:
```bash
docker exec -it <odoo_container_name> odoo -d <database_name> -i nn_fund_management --test-enable --stop-after-init
```
*(Replace `<odoo_container_name>` and `<database_name>` with your actual running container ID and database name.)*

### Assumptions
- A user must have an active session and proper access rights to trigger any state transitions.
- "Project A" and "Project B" are abstracted into a simplified `nn.project.expense.head` model to maintain strict module decoupling from the standard heavy Odoo Project app, ensuring pure financial tracking.
- Approvals always follow a linear sequence: Submitted → GM → MD → Approved.

### Known Limitations
- **Bank Email Integration (Prototype)**: The `bank_email_integration.py` utilizes regex patterns to parse text. In real production, standardized bank APIs or MT940 XML parsing is much safer.
- **Cross-Currency Exchange**: While multi-currency fields are mapped (`currency_id`), complex real-time FX rate conversions for held amounts are not fully fleshed out and assume a normalized company currency.

---

## Requirements & Fulfillment Checklist
- [x] **Core Logic**: Incoming funds, allocations, requisitions, bills, and transfers managed.
- [x] **Double Spend Prevention**: Amount dynamically locked into a 'hold' state when submitted.
- [x] **Fund Accounts**: Tracking unassigned balance, amount on hold, assigned amount.
- [x] **Workflow Pipeline**: GM and MD tiered approvals enforced.
- [x] **Balance Calculations**: 100% automated; manual edits blocked.
- [x] **Bill Control**: Custom bill limits based on remaining billable requisition limits.
- [x] **Audit History**: Deep tracking of state changes, users, and timestamps.
- [x] **Security**: Groups, ir.model.access.csv, and server-side model checks.
- [x] **Bonus**: Configurable approval matrices, Email prototype, and Dashboard implemented.

---

## System Architecture & Backend Logic

### Short Architecture Explanation
The architecture relies entirely on **Server-Side Computed Dependencies**. Instead of manually passing numbers between tables (which causes race conditions), the core entity `nn.project.expense.head` computes its available balance *on-the-fly* by dynamically aggregating the `amount` fields of all related Allocations, Requisitions, and Transfers based on their exact `state`.

1. **`nn.fund.account`**: The financial entry point. Confirmed funds go here.
2. **`nn.project.expense.head`**: The financial endpoint. Balances are derived mathematically from related transactions.
3. **Transaction Models** (`allocation`, `requisition`, `transfer`): Acts as the routing layer. When they shift to the `submitted` state, the parent models deduct the amount from `available_unassigned` and move it into `amount_on_hold`.
4. **`nn.audit.history`**: An asynchronous logging layer that intercepts state change methods (`action_submit`, `action_gm_approve`) and writes an immutable ledger entry.

---

## Access Control and Security Files
All security configurations are stored in the `security/` directory:
- **`res_groups.xml`**: Defines the hierarchical user groups (`Fund User` → `Finance User` → `GM Approver` → `MD Approver` → `Fund Administrator`).
- **`ir.model.access.csv`**: Maps exactly which groups can Create, Read, Update, or Delete (CRUD) specific models. 
  - *Example*: Only `Finance User` can confirm incoming funds. Only `GM/MD` can write state changes for approvals.

---

## Testing Strategy & Bug Categories
- **Unit Testing**: Focused on the `_compute_balances` logic to ensure mathematically impossible scenarios (e.g. `Available Fund < 0`) trigger Odoo `ValidationErrors`.
- **Workflow Testing**: The `test_fund_workflow.py` script mimics the exact 13-step scenario provided in the assessment prompt.
- **Bug Prevention (Double Spending)**: By utilizing strict ORM `store=True` computations tied to specific status strings, it is impossible for a user to allocate funds that are sitting in a "submitted" (pending) state for someone else. 

---

## Technical Challenges & Observations
- **Concurrency & Holds**: The primary challenge was ensuring money didn't "disappear" during the GM → MD approval latency. By mapping intermediate states (`submitted`, `gm_approved`) to specific `_compute` methods targeting the `hold` field, funds remain visible but mathematically locked out of `available_balance`.
- **Multi-Company Data Leaks**: Mitigated natively by attaching `company_id` to all models, relating it to the parent Fund Account, and appending `_check_company_auto = True`.
- **Custom Vendor Bills**: Decoupled from Odoo's core `account.move` to keep the assessment strictly within the isolated `nn_fund_management` logic, ensuring pure constraint tracking.

---

## Meaningful Git Commit History
The repository was built using structured, atomic commits reflecting logical development phases:
1. `feat: initialize odoo module scaffold and manifest configurations`
2. `feat: implement core database models, computed financial balances, and data integrity validation rules`
3. `feat: establish role-based security groups, ir.model.access mappings, and XML view definitions`
4. `test: add automated workflow suite to validate the mandatory 13-step business scenario`
5. `feat: implement configurable approval matrices, email intake routing pipeline, and aggregated tracking dashboard`
6. `chore: wrap production deployment with docker-compose stack and build detailed readme documentation`
