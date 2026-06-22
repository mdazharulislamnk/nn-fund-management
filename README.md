# NN Fund Management Module

An expert-level Odoo 16 custom module designed for strict fund tracking, dynamic double-spending prevention, and multi-company financial approval workflows.

## Target Remote Git Repository
**Repository URL**: [https://github.com/mdazharulislamnk/nn-fund-management](https://github.com/mdazharulislamnk/nn-fund-management)

## Odoo Version
This module is built and tested for **Odoo 16.0** (Community / Enterprise). It relies on standard Odoo ORM methods and strict database constraints.

## Features Implemented
- **Strict Concurrency Control**: Prevents double-spending by dynamically isolating requested funds into a `hold` state upon submission.
- **Workflow State Machine**: `Draft -> Submitted -> GM Approval -> MD Approval -> Approved/Rejected/Cancelled`.
- **Multi-Company Isolation**: Standard `company_id` enforcement with `check_company=True`.
- **Automated Balances**: Financial balances are fully computed via ORM mapping; manual overriding is strictly prevented.
- **Comprehensive Testing**: Includes an automated suite verifying the mandatory 13-step business scenario.
- **Advanced Features**: Configurable approval matrices, bank email parsing integration (prototype), and a Kanban/XML Dashboard.

## Installation Instructions (Docker)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mdazharulislamnk/nn-fund-management.git
   cd nn-fund-management
   ```

2. **Run the stack using Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access Odoo:**
   Open your browser and navigate to `http://localhost:8069`.

4. **Install the Module:**
   - Log into Odoo as the administrator.
   - Go to Apps and click "Update Apps List".
   - Search for `NN Fund Management`.
   - Click "Install".

## Testing Instructions
To run the Phase 4 test suite validating the 13-step scenario:
```bash
docker exec -it <odoo_container_name> odoo -d <database_name> -i nn_fund_management --test-enable --stop-after-init
```

## Known Limitations & Assumptions
- **Bank Integration Prototype**: The `bank_email_integration` model currently uses regex heuristics assuming a static email body format (e.g., "Ref: TXN9999"). In a production scenario, integration directly via bank APIs or standardized MT940/CAMT.053 files is recommended.
- **Cross-Currency Support**: Currently, operations assume the standard company currency. Complex multi-currency tracking (real-time exchange rate adjustments for held amounts) is scoped for future iterations.
- **Performance**: Heavy reliance on `_compute_balances` spanning multiple relationships may have minor performance implications on databases with millions of rows; utilizing Odoo's `store=True` and optimized batch computing mitigates this risk significantly.
