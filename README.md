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
8. [Video Demonstration Guide](#8-video-demonstration-guide)

---

## Directory Structure

```text
.
├── conversation_history.md
├── demonstration.md
├── docker-compose.yml
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

## 8. Video Demonstration Guide

This section details exactly what to type in your terminal, which URLs to open, and the exact interface buttons to click during your video recording.

---

## Phase 0: Starting the Environment (Terminal)

Before you start recording your facecam, make sure the environment is running.

1. **Open your VS Code Terminal.**
2. **Start the server** by running this exact command:
   ```bash
   docker-compose up -d
   ```
3. **Open the Odoo Interface:**
   - If using your local PC: Open Chrome/Edge and go to `http://localhost:8069`
   - If using GitHub Codespaces: Go to the **PORTS** tab at the bottom of VS Code, right-click on port `8069`, select **Port Visibility -> Public**, and click the globe icon to open it.

---

## Phase 1: Initial Setup & Installation (UI Interface)

1. **Log in to Odoo:**
   - Email: `admin`
   - Password: `admin`
2. **Install the Module:**
   - Click the top-left icon (the 9 squares / App Drawer).
   - Click **Apps**.
   - In the top-right search bar, click the **'x'** next to the `Apps` filter to remove it.
   - Type `nn_fund_management` and hit Enter.
   - Click the **Activate** button. Wait for the page to reload.

---

## Phase 2: Security and Access Control (Section 9)

**Goal:** Show server-side security blocking unauthorized clicks.

1. **Create the Users:**
   - Click the top-left App Drawer -> **Settings**.
   - Under "Users & Companies", click **Users**.
   - Click **New** (or Create).
   - Name: `Mr. GM Approver`. Under the "Fund Management" dropdown, select **GM Approver**. Save.
   - Click **New**. Name: `Mr. Fund User`. Under "Fund Management", select **Fund User**. Save.
2. **Demonstrate the Block (Server-Side Security):**
   - Click the top right profile icon and **Log out**.
   - Log back in as `Mr. Fund User`.
   - Open the App Drawer -> Click **Fund Management**.
   - Go to the **Allocations** menu at the top. Click **New**.
   - Fill in any Project and Amount. Click the **Submit** button (this is allowed).
   - Now, explicitly click the **Approve** button.
   - **Video Action:** A red error window will pop up saying "Access Denied". 
   - **Say in video:** *"As you can see, hiding UI buttons is not enough. The Odoo server-side record rules actively block this Fund User from approving their own request."*
3. **Approve properly:**
   - Log out. Log in as `Mr. GM Approver`.
   - Go to **Fund Management -> Allocations**.
   - Open the pending allocation and click **Approve**. It will succeed.

---

## Phase 3: Audit History & Bonus Features (Sections 10 & 11)

1. **Audit History:**
   - While still looking at the approved Allocation, scroll down to the bottom of the page (the Chatter area).
   - **Video Action:** Highlight the logs.
   - **Say in video:** *"Here is the Audit History. It immutably records the exact timestamp, the user who clicked the button, the state change, and the financial amount. This cannot be deleted."*
2. **Configurable Approval Rules:**
   - On the top menu bar, click **Configuration -> Approval Rules**.
   - **Say in video:** *"This is the dynamic matrix. Instead of hardcoding rules, the company can configure that amounts between 50,000 and 200,000 require GM and Finance sequences."*
3. **Dashboard:**
   - Click **Dashboard** on the top menu.
   - **Video Action:** Show the tracking widgets displaying "Total Funds Received", "Unassigned Balance", and "Held Amount".

---

## Phase 4: The 13-Step Sample Demonstration (Section 13)

*Make sure you are logged in as Admin or a full Fund Administrator to do this smoothly.*

**Step 1. Receive BDT 1,000,000**
- Click **Fund Accounts** on the top menu. Click **New**.
- Name: `Main Corporate Fund`. Save.
- Click **Add Incoming Fund**. Amount: `1,000,000`. Confirm it.

**Step 2. Request BDT 600,000 for Project A**
- Go to **Allocations** menu. Click **New**.
- Source Fund: Select `Main Corporate Fund`.
- Target: Create a new project called `Project A`.
- Amount: `600,000`. Click **Submit**.

**Step 3. Show that BDT 600,000 remains on hold**
- Go back to **Fund Accounts** -> Open `Main Corporate Fund`.
- **Video Action:** Point your mouse at the "Held Amount" field showing `600,000`. 
- **Say in video:** *"The funds are dynamically locked and held while the request is pending."*

**Step 4. Reject the request & return money**
- Go back to **Allocations**. Open the pending request.
- Click **Reject**.
- Go to **Fund Accounts**. Show that the Held Amount is back to `0` and Unassigned is `1,000,000`.

**Step 5. Submit again and approve**
- Go back to the **Allocation**. Click **Reset to Draft**, then **Submit**, then **Approve**.

**Step 6. Transfer BDT 200,000 from Project A to Project B**
- Go to **Transfers** on the top menu. Click **New**.
- Source: `Project A`.
- Destination: Create `Project B`.
- Amount: `200,000`. Click **Submit**.

**Step 7. Show Transfer Hold**
- Go to **Project / Expense Heads** on the top menu. Open `Project A`.
- **Video Action:** Point out that `200,000` is currently in the Transfer Hold state.

**Step 8. Approve the transfer**
- Go back to **Transfers**. Click **Approve**. Project B now officially holds the funds.

**Step 9. Create a BDT 150,000 requisition for Project B**
- Go to **Requisitions** on the top menu. Click **New**.
- Source: `Project B`. Amount: `150,000`.
- Click **Submit** then **Approve**.

**Step 10. Create a BDT 100,000 partial bill**
- Go to **Vendor Bills** (under the Accounting section or via a Smart Button if visible).
- Select the `150,000` Requisition in the linked field.
- Enter bill amount: `100,000`. Click **Confirm/Post**.

**Step 11. Show that BDT 50,000 remains billable**
- Go back to the **Requisition** record for Project B.
- **Video Action:** Show the "Remaining Billable" field automatically calculated to `50,000`.

**Step 12. Try to create another bill for BDT 60,000 and block it**
- Go to **Vendor Bills**. Create a new bill.
- Link it to the SAME requisition.
- Enter amount: `60,000`. Click **Confirm**.
- **Video Action:** A red validation error pops up. 
- **Say in video:** *"The database constraint strictly blocks over-billing."*

**Step 13. Try to use Project B’s requisition for Project A and block it**
- Go to **Vendor Bills**. Create a new bill.
- Link it to Project B's requisition, but select Project A in the Expense Head field. Click Confirm.
- **Video Action:** Another red error pops up. 
- **Say in video:** *"Cross-project billing is strictly blocked to prevent fund mismanagement."*

---
*End of Video Recording.*
