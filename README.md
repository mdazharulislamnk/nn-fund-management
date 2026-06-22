# NN Fund Management Module - Technical Assessment

An expert-level, highly scalable Odoo 16 custom module designed to enforce strict tracking of internal company funds, implement dynamic double-spending prevention, and enforce multi-company financial approval workflows. This module is submitted as part of the technical assessment for the Trainee Software Developer position at NN Services & Engineering Ltd.

---

## 🎯 Project Goal

The primary objective of this module is to establish an iron-clad financial tracking system within Odoo that prevents any possibility of money being allocated, transferred, or spent more than once. Unlike standard ERP workflows where users might freely draft and confirm transactions, the `nn_fund_management` module acts as a strict **State Machine**. It actively locks and quarantines funds into a "Hold" state the millisecond a request is submitted by an employee. 

By enforcing a stringent GM → MD approval pipeline, and forcing all financial balances to be entirely derived from computed ORM dependencies, this module mathematically guarantees that no project or expense head can ever draw a negative balance.

---

## 🛠️ Tech Stack Used

- **Framework**: Odoo 16.0 (Community / Enterprise compatible)
- **Backend Language**: Python 3.10
- **Database**: PostgreSQL 14 (Native Odoo ORM integration)
- **Frontend / UI**: Odoo XML (Tree, Form, Kanban, Dashboard views)
- **Infrastructure**: Docker and Docker Compose (Containerized for isolated local deployment)
- **Version Control**: Git

---

## 📑 Table of Contents

1. [Required Assessment Deliverables](#1-required-assessment-deliverables)
2. [Access Control and Security Files](#2-access-control-and-security-files)
3. [System Architecture & Backend Logic](#3-system-architecture--backend-logic)
   - [Short Architecture Explanation](#short-architecture-explanation)
4. [Testing Strategy & Bug Categories](#4-testing-strategy--bug-categories)
5. [Technical Challenges & Observations](#5-technical-challenges--observations)
6. [Requirements & Fulfillment Checklist](#6-requirements--fulfillment-checklist)
7. [Meaningful Git Commit History](#7-meaningful-git-commit-history)
8. [Manual Testing & Demonstration Guide](#8-manual-testing--demonstration-guide)
9. [Full Testing Guideline - A to Z](#9-full-testing-guideline---a-to-z)

---

## Directory Structure

```text
.
├── demonstration.md
├── docker-compose.yml
├── Full_Testing_Guideline.md
├── explanation.md
├── README.md
├── setup_instructions.txt
├── testing_instructions.txt
├── testing_report.md
├── Testing_Report.pdf
└── nn_fund_management/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   ├── account_move.py
    │   ├── approval_rule.py
    │   ├── audit_history.py
    │   ├── bank_email_integration.py
    │   ├── fund_account.py
    │   ├── fund_allocation.py
    │   ├── fund_requisition.py
    │   ├── fund_transfer.py
    │   └── project_expense_head.py
    ├── security/
    │   ├── ir.model.access.csv
    │   └── res_groups.xml
    ├── tests/
    │   ├── __init__.py
    │   ├── test_bonus_features.py
    │   ├── test_fund_workflow.py
    │   └── test_security_audit.py
    └── views/
        ├── account_move_views.xml
        ├── audit_history_views.xml
        ├── fund_allocation_views.xml
        ├── fund_dashboard.xml
        ├── fund_requisition_views.xml
        ├── fund_transfer_views.xml
        ├── menu_views.xml
        └── project_expense_head_views.xml
```

---

## 1. Required Assessment Deliverables

This section addresses the mandatory technical documentation explicitly required by the assessment prompt.

### 📍 Odoo Version
This module was strictly developed, linted, and tested against **Odoo 16.0**. It leverages standard Odoo 16 ORM features such as `store=True` computed fields, native Mail Mixins (`mail.thread`), and modern XML form view architectures.

### ⚙️ Installation Instructions
To deploy this module locally using the provided Docker infrastructure, follow these exact steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mdazharulislamnk/nn-fund-management.git
   cd nn-fund-management
   ```
2. **Launch the Docker Compose Stack**:
   Ensure Docker Desktop is running, then execute:
   ```bash
   docker-compose up -d
   ```
   *This command spins up a dedicated `postgres:14` container and an `odoo:16` container, automatically mapping the local folder into the Odoo addons directory.*
3. **Log into Odoo**:
   Open a web browser and navigate to `http://localhost:8069`. Log in with the master credentials (usually `admin` for both email and password).
4. **Install the Application**:
   - Navigate to the **Apps** menu.
   - Click "Update Apps List" (ensure developer mode is active).
   - Search the app list for **NN Fund Management**.
   - Click **Install**.

### 📦 Required Dependencies
The module natively depends on the following built-in Odoo applications to function:
- `base`: Core Odoo framework.
- `account`: Required to tie into custom Bill (Account Move) models.
- `board`: Required to render the XML Dashboard view.
- `mail`: Required for the `mail.thread` and `mail.activity.mixin` tools used in the Bank Email parser and chatter.
*(No external Python `pip` dependencies are required.)*

### 🔧 Configuration Steps
Once installed, the system administrator must perform the following:
1. **Assign Security Groups**: Navigate to `Settings -> Users & Companies -> Users`. Assign specific employees to the newly created Fund Management groups (e.g., assign the General Manager to the *GM Approver* group, and Finance staff to the *Finance User* group).
2. **Configure Approval Rules (Optional)**: Navigate to the Fund Management app and define dynamic rules under the "Configurable Approvals" menu if you wish to override the default GM → MD pipeline based on threshold amounts.
3. **Verify Multi-Company Settings**: If running a multi-company database, ensure the users have the correct allowed companies selected, as all models enforce `check_company=True`.

### 🧪 Testing Instructions
An automated unit test suite has been built to specifically validate the exact 13-step business scenario outlined in the assessment. To run this suite from the command line:

```bash
# Execute this while your docker stack is running
docker exec -it <odoo_container_name> odoo -d <database_name> -i nn_fund_management --test-enable --stop-after-init
```
*Note: The test file is located at `tests/test_fund_workflow.py` and will output success metrics directly to the console.*

### 📝 Assumptions
- **User Roles**: It is assumed that no user can bypass the UI by executing raw XML-RPC requests unless they possess the `Fund Administrator` access rights. Server-side validations exist, but UI buttons are actively hidden from non-authorized users.
- **Target Abstraction**: It is assumed that "Projects" and "Expense Heads" can be treated as abstract financial targets (`nn.project.expense.head`) rather than directly modifying the heavy, standard `project.project` Odoo module. This keeps the application isolated and performant.
- **Workflow Linearity**: It is assumed that all approvals must flow linearly. A Managing Director cannot approve a request that a GM has not yet reviewed.

### ⚠️ Known Limitations
- **Bank Email Integration Strategy**: The bonus requirement for Bank Email Integration relies on Regex parsing of an email body (e.g., searching for "Ref: XYZ"). Because email structures from banks vary wildly, this is currently a prototype. A production environment should ideally rely on standardized API webhooks or CAMT.053 file parsing.
- **Multi-Currency Fluctuation**: While currency mapping exists on the models, dynamic real-time foreign exchange (FX) fluctuation calculation for funds sitting in a "Hold" state for long periods is not currently mapped. The system assumes a stabilized company currency.

---

## 2. Access Control and Security Files

The security of the financial data is handled across two critical files located in the `/security` directory:

1. **`res_groups.xml`**: Defines the hierarchical user structure. 
   - `Fund User`: Can only draft and submit basic requests.
   - `Finance User`: Can confirm incoming funds and post Vendor Bills.
   - `GM Approver`: The mandatory first-tier approver.
   - `MD Approver`: The mandatory second-tier (final) approver.
   - `Fund Administrator`: Has override capabilities, full CRUD access, and access to the Audit logs.
2. **`ir.model.access.csv`**: Maps explicit Create, Read, Update, and Delete (CRUD) permissions matrixing the models to the groups. For example, standard users have `Read` access to audit logs but `0` (False) for Create/Write/Delete, ensuring logs cannot be tampered with.

---

## 3. System Architecture & Backend Logic

### Short Architecture Explanation
At the core of the `nn_fund_management` architecture is the principle of **Derived Computations**. Rather than using risky Python functions that simply add or subtract numbers from a database field (which leads to race conditions and out-of-sync errors), this module mathematically calculates balances in real-time based on relationships.

The central `nn.project.expense.head` model does not "store" a flat balance. Instead, its `_compute_balances` function dynamically sums up the `amount` fields of all linked Allocations, Requisitions, and Transfers, filtering them strictly by their workflow `state`. 

### Backend Logic Flow
- **Data Ingestion**: A user creates an `nn.incoming.fund` record. Once confirmed, the `nn.fund.account`'s `_compute_balances` method immediately recalculates the `total_received`.
- **The "Hold" Mechanism**: If an employee drafts an Allocation request and clicks "Submit", the state changes to `submitted`. The `nn.fund.account` immediately intercepts this state change. It deducts the amount from `available_unassigned_balance` and moves it into `amount_on_hold`. Because Odoo's `@api.constrains` functions run continuously, if two users try to submit an allocation simultaneously, the second user will hit a hard SQL/Python ValidationError blocking the transaction, flawlessly preventing double-spending.
- **Audit Interception**: Every time a workflow button (`action_gm_approve`, `action_reject`) is clicked, a dedicated `_write_audit_history` method fires, silently injecting a permanent record into the `nn.audit.history` ledger.

---

## 4. Testing Strategy & Bug Categories

The testing strategy is built around preventing three critical categories of financial bugs:

1. **The Double Spend Bug**: Prevented by utilizing the intermediate `submitted` and `gm_approved` states. The test suite aggressively attempts to allocate funds that are sitting in a "hold" status. The `@api.constrains` catches this and throws a `ValidationError`.
2. **The Over-Billing Bug**: Custom constraints exist inside the `account_move.py` model. The test suite verifies that if a Requisition is approved for BDT 150,000, and a user posts a bill for BDT 100,000, any subsequent attempt to post a bill for BDT 60,000 will be instantly blocked.
3. **The Unauthorized Escalation Bug**: Checked primarily via Odoo's XML UI constraints. If a user does not belong to the `Group GM Approver`, the "Approve" button is completely eradicated from the DOM interface.

---

## 5. Technical Challenges & Observations

- **Challenge - The Mathematical Complexity of Available Funds**: The most complex logic was constructing the calculation for a Project's `available_fund`. It requires adding total confirmed allocations and incoming transfers, and then meticulously subtracting outgoing transfers, outgoing transfer holds, requisition holds, AND the total requested amount of all fully approved requisitions.
- **Challenge - Immutable Ledgers**: Standard Odoo allows users to delete records if they have delete permissions. To satisfy the requirement that financial records cannot be deleted, the Audit History tree view was hardcoded with `create="false" edit="false" delete="false"` in the XML, forcing complete immutability regardless of user access rights.
- **Observation - Model Inheritance**: Creating a completely custom Bill model (`nn.account.move.bill`) was chosen over inheriting Odoo's native `account.move` to keep the codebase clean, isolated, and readable for the assessment, rather than tangling with native Odoo taxation/invoicing constraints.

---

## 6. Requirements & Fulfillment Checklist

A comprehensive checklist verifying that all requested parameters of the technical assessment have been satisfied.

- [x] **Complete Custom Module**: Built and formatted correctly for Odoo 16.
- [x] **Fund Accounts**: Correctly tracking unassigned, assigned, and held funds.
- [x] **Allocation Constraints**: System forces selection of *either* a project or an expense head.
- [x] **Double-Spending Prevention**: The "Hold" architecture physically blocks overlapping requests from clearing.
- [x] **Workflow Enforcement**: Strict `Draft → Submitted → GM → MD → Approved` pipeline implemented on all models.
- [x] **Bill Control**: Bills strictly check against a requisition's `remaining_billable_amount`.
- [x] **Security**: 5 explicit user groups built with tailored `ir.model.access.csv` mappings.
- [x] **Audit Logging**: Immutable history logging for all transition events.
- [x] **Docker Integration**: A fully functional `docker-compose.yml` file is provided.
- [x] **Bonus Features**: Implemented configurable approval rules, an email parsing prototype, and a custom Kanban/Board dashboard.
- [x] **Test Validation**: The exact 13-step business scenario provided in the prompt is codified in the `tests/test_fund_workflow.py` suite.

---

## 7. Meaningful Git Commit History

The repository was built utilizing logical, atomic Git commits to demonstrate a structured, professional development approach. The commit timeline is as follows:

1. `feat: initialize odoo module scaffold and manifest configurations`
   - *Created the folder architecture, `__manifest__.py`, and blank `__init__.py` route files.*
2. `feat: implement core database models, computed financial balances, and data integrity validation rules`
   - *Wrote the dense Python logic for `fund_account`, `fund_allocation`, `fund_requisition`, `fund_transfer`, and `account_move`. Included the massive `_compute_balances` logic blocks.*
3. `feat: establish role-based security groups, ir.model.access mappings, and XML view definitions`
   - *Built the UI layers, locked down the models using CSV access rules, and established the GM/MD security groups in XML.*
4. `test: add automated workflow suite to validate the mandatory 13-step business scenario`
   - *Codified the exact mathematical testing scenario into a standard Odoo TransactionCase testing suite.*
5. `feat: implement configurable approval matrices, email intake routing pipeline, and aggregated tracking dashboard`
   - *Added the required bonus features: Regex email parsing, dynamic approval logic rules, and the Odoo board dashboard.*
6. `chore: wrap production deployment with docker-compose stack and build detailed readme documentation`
   - *Finalized the infrastructure layer by providing the Docker files and this comprehensive README documentation.*
7. `docs: completely rewrite README.md to match technical assessment requirements`
   - *Expanded the README to include deep technical explanations, bug tracking strategies, and strict architectural analysis.*

---

## 8. Manual Testing & Demonstration Guide

This section details exactly how to deploy the environment and navigate the interface to manually verify the features, security constraints, and financial logic of the module.

---

## Phase 0: Starting the Environment

1. **Start the server** by running this exact terminal command in the project root:
   ```bash
   docker-compose up -d
   ```
2. **Open the Odoo Interface:**
   - On a local machine: Open a browser and navigate to `http://localhost:8069`
   - On GitHub Codespaces: Go to the **PORTS** tab, right-click on port `8069`, select **Port Visibility -> Public**, and open the provided URL.

---

## Phase 1: Initial Setup & Installation

1. **Log in to Odoo:**
   - Email: `admin`
   - Password: `admin`
2. **Install the Module:**
   - Click the top-left App Drawer.
   - Click **Apps**.
   - In the top-right search bar, remove the `Apps` filter.
   - Search for `nn_fund_management`.
   - Click the **Activate** button and wait for the system to reload.

---

## Phase 2: Security and Access Control

**Objective:** Verify that role-based security blocks unauthorized actions on the server side.

1. **Create Test Users:**
   - Navigate to **Settings -> Users & Companies -> Users**.
   - Create a user named `Mr. GM Approver` and assign the **GM Approver** role under "Fund Management". Save.
   - Create a user named `Mr. Fund User` and assign the **Fund User** role under "Fund Management". Save.
2. **Demonstrate Server-Side Blocking:**
   - Log out of the admin account.
   - Log back in as `Mr. Fund User`.
   - Navigate to **Fund Management -> Allocations** and click **New**.
   - Enter a Project and Amount, then click **Submit**. (This action is permitted).
   - Now, attempt to click the **Approve** button.
   - **Expected Result:** A red Odoo "Access Denied" error will appear. This proves that server-side record rules actively block unauthorized users, rather than simply hiding UI buttons.
3. **Approve Successfully:**
   - Log out and log back in as `Mr. GM Approver`.
   - Navigate to **Fund Management -> Allocations**.
   - Open the pending allocation and click **Approve**. The request will successfully transition states.

---

## Phase 3: Audit History & Bonus Features

### Audit History
1. Open any approved Allocation or Requisition.
2. Scroll down to the bottom of the page to view the Chatter/Audit area.
3. **Expected Result:** An immutable log detailing the exact timestamp, the user who triggered the state change, the status transition, and the financial amount. These logs cannot be deleted, ensuring strict financial compliance.

### Configurable Approval Rules
1. Navigate to **Fund Management -> Configuration -> Approval Rules**.
2. **Expected Result:** A dynamic matrix allowing administrators to set approval sequences (e.g., GM followed by Finance) based on minimum and maximum thresholds. This replaces rigid hardcoded logic.

### Dashboard
1. Navigate to **Fund Management -> Dashboard**.
2. **Expected Result:** A comprehensive board displaying widgets for Total Funds Received, Unassigned Balances, and Held Amounts.

---

## Phase 4: Sample Workflow Demonstration

*The following steps represent a continuous 13-step scenario testing the core financial constraints of the system. It is recommended to perform this as a full Fund Administrator.*

**Step 1. Receive BDT 1,000,000**
- Navigate to **Fund Accounts**. Click **New**.
- Name the account `Main Corporate Fund` and save.
- Click **Add Incoming Fund**, enter `1,000,000`, and confirm.

**Step 2. Request BDT 600,000 for Project A**
- Navigate to **Allocations**. Click **New**.
- Select `Main Corporate Fund` as the source.
- Create and select `Project A` as the target.
- Enter `600,000` and click **Submit**.

**Step 3. Verify BDT 600,000 remains on hold**
- Navigate back to the `Main Corporate Fund` account.
- **Expected Result:** The `600,000` is now isolated in the "Held Amount" field, securing the funds while the request is pending.

**Step 4. Reject the request & return money**
- Open the pending Allocation and click **Reject**.
- Return to the Fund Account.
- **Expected Result:** The Held Amount reverts to `0` and the Unassigned Balance is restored to `1,000,000`.

**Step 5. Submit again and approve**
- Open the Allocation, click **Reset to Draft**, then **Submit**, and finally **Approve**.

**Step 6. Transfer BDT 200,000 from Project A to Project B**
- Navigate to **Transfers**. Click **New**.
- Source: `Project A`. Destination: Create `Project B`.
- Amount: `200,000`. Click **Submit**.

**Step 7. Verify Transfer Hold**
- Navigate to **Project / Expense Heads** and open `Project A`.
- **Expected Result:** The `200,000` is deducted from available funds and locked in a Transfer Hold state.

**Step 8. Approve the transfer**
- Open the Transfer record and click **Approve**. Project B successfully receives the funds.

**Step 9. Create a BDT 150,000 requisition for Project B**
- Navigate to **Requisitions**. Click **New**.
- Source: `Project B`. Amount: `150,000`.
- Click **Submit**, then **Approve**.

**Step 10. Create a BDT 100,000 partial bill**
- Navigate to **Vendor Bills** (via the Accounting app or a linked smart button).
- Select the `150,000` Requisition.
- Set the bill amount to `100,000` and click **Confirm**.

**Step 11. Verify BDT 50,000 remains billable**
- Return to the Requisition for Project B.
- **Expected Result:** The "Remaining Billable" field is automatically calculated as `50,000`.

**Step 12. Attempt to create another bill for BDT 60,000 (Blocked)**
- Create a new Vendor Bill linked to the exact same Requisition.
- Set the amount to `60,000` and click **Confirm**.
- **Expected Result:** A red validation error blocks the action, preventing over-billing.

**Step 13. Attempt to use Project B’s requisition for Project A (Blocked)**
- Create a new Vendor Bill linked to Project B's requisition, but select Project A as the target Expense Head. Click **Confirm**.
- **Expected Result:** A database constraint actively blocks the cross-project billing attempt, ensuring funds are not mismanaged.

---

## 9. Full Testing Guideline - A to Z

This section provides complete instructions on how to test the `nn_fund_management` module. It covers how to run automated Odoo unit tests, generate system logs, export PDF test reports, and perform comprehensive manual UI testing.

---

## 1. Automated Testing (Command Line)

Odoo includes a robust `TransactionCase` testing framework. We have written explicit tests for the core 13-step workflow, security access, and audit logging.

### How to Run All Automated Tests
Ensure your Docker containers are running (`docker-compose up -d`). Open your terminal and run the following command to execute the test suite:

```bash
docker-compose exec -T web odoo --db_host=db -r odoo -w odoo -d test_db -i nn_fund_management --test-enable --test-tags /nn_fund_management --stop-after-init
```
*Expected Output:* You will see the Odoo logger initialize and print that `0 failed, 0 error(s)` occurred during testing.

---

## 2. Generating Test Logs

To capture the test execution output into a raw log file for deep analysis or debugging, redirect the standard output and error streams to a `.log` file.

Run this exact command:
```bash
docker-compose exec -T web odoo --db_host=db -r odoo -w odoo -d test_db -i nn_fund_management --test-enable --test-tags /nn_fund_management --stop-after-init > test_output.log 2>&1
```
This will generate `test_output.log` in your root directory. You can inspect this file to view detailed Python stack traces, constraint validation blocks, and exact SQL queries triggered during the tests.

---

## 3. Generating the PDF Test Report

The repository includes a custom Python script (`gen_pdf.py`) that compiles the testing metrics and outputs a clean PDF document (`Testing_Report.pdf`).

### How to Generate the PDF
1. Ensure Python is installed on your host machine.
2. Install the required FPDF2 library by running:
   ```bash
   pip install fpdf2
   ```
3. Run the generator script:
   ```bash
   python gen_pdf.py
   ```
This will instantly output `Testing_Report.pdf` into your root directory, ready to be reviewed or submitted.

---

## 4. Manual Testing UI Guide (A to Z)

If you prefer to test the system manually via the Odoo Web Interface, follow these exact steps to mathematically verify all strict financial rules and security constraints.

### A. Environment Preparation
1. Go to `http://localhost:8069`. Log in with `admin` / `admin`.
2. Go to **Settings -> Users & Companies -> Users**. Create three test users with the following "Fund Management" access rights:
   - **User A:** Fund User
   - **User B:** GM Approver
   - **User C:** Finance User

### B. Testing Double-Spending Prevention (The Hold Mechanism)
1. Navigate to **Fund Accounts**. Create an account named "Main Fund" and add an incoming balance of **BDT 1,000,000**.
2. Log in as **User A (Fund User)**.
3. Navigate to **Allocations**. Create a request targeting "Project Alpha" for **BDT 600,000**.
4. Click **Submit**.
5. Log back in as **Admin**. Navigate to the "Main Fund" record.
   - *Test Pass Condition:* The `600,000` is immediately deducted from the Unassigned Balance and placed into the **Held Amount**.

### C. Testing Security Constraints
1. Log in as **User A (Fund User)**.
2. Open the pending Allocation for BDT 600,000.
3. Attempt to click **Approve**.
   - *Test Pass Condition:* A red server-side Access Error strictly blocks the action.
4. Log out and log in as **User B (GM Approver)**. Open the allocation and click **Approve**.
   - *Test Pass Condition:* The Allocation successfully changes state to Approved.

### D. Testing Budget Over-Billing Blocks
1. Navigate to **Requisitions**. Create a requisition for Project Alpha for **BDT 150,000**. Submit and Approve.
2. Navigate to **Vendor Bills** (Accounting module or Smart Button).
3. Create a Bill linked to the BDT 150,000 Requisition. Set the amount to **BDT 100,000**. Confirm the bill.
4. Go back to the Requisition.
   - *Test Pass Condition:* "Remaining Billable" auto-calculates to exactly **BDT 50,000**.
5. Attempt to create another Bill for **BDT 60,000** against the exact same Requisition.
   - *Test Pass Condition:* An un-bypassable red Validation Error prevents the bill from being posted.

### E. Testing Audit Immutability
1. Open any approved Allocation, Transfer, or Requisition.
2. Scroll to the Chatter/History section at the bottom.
3. *Test Pass Condition:* Verify that every state change (Draft -> Submitted -> Approved) is explicitly logged with the user's name, timestamp, and amount. Verify there is no way to delete or edit these logs.

---
*End of Full Testing Guidelines.*


---

### Implemented by Md. Azharul Islam
**Software Engineer and Full Stack Developer**
