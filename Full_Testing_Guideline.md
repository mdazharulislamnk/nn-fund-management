# Full Testing Guideline - A to Z

This document provides complete instructions on how to test the `nn_fund_management` module. It covers how to run automated Odoo unit tests, generate system logs, export PDF test reports, and perform comprehensive manual UI testing.

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
