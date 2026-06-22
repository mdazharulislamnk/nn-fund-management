# Odoo Fund Management - Facecam Demonstration Guide

This document is your **exact script** for your screen recording. It provides step-by-step manual UI instructions to visually demonstrate every required feature, proving that your code fulfills sections 9, 10, 11, and 13 of the assessment.

---

## Part 1: Security and Access Control (Section 9)

**Goal:** Show that role-based security works strictly on the server-side.

1. **Create Test Users:**
   - Go to **Settings -> Users & Companies -> Users**.
   - Create users and assign them specific roles from the "Fund Management" category in their access rights:
     - User A: `Fund User`
     - User B: `GM Approver`
     - User C: `Finance User`
2. **Demonstrate Restriction (Server-Side Check):**
   - **Log in as User A (Fund User).**
   - Go to **Fund Management -> Allocations** and create a draft allocation.
   - Click **Submit**. (It works).
   - Now, as User A, try to click **Approve**. 
   - **Video Action:** Show the red Odoo Access Error (Access Denied) popping up. State: *"As you can see, hiding UI buttons is not enough; the server-side Record Rules actively block unauthorized users from executing approval methods."*
3. **Demonstrate Authorization:**
   - **Log out and Log in as User B (GM Approver).**
   - Open the exact same allocation and click **Approve**.
   - **Video Action:** Show it successfully moving to the Approved state.

---

## Part 2: Audit History (Section 10)

**Goal:** Show that financial actions leave an immutable, detailed trace.

1. **Navigate to an Approved Record:**
   - Go to **Fund Management -> Allocations** (or Requisitions).
   - Open the record you just approved.
2. **Show the Audit Trail:**
   - Look at the bottom of the form view (or a dedicated "Audit History" tab if placed there).
   - **Video Action:** Highlight the grid showing the exact history. Point out:
     - Record Creator
     - Approver name
     - Status change (Draft -> Submitted -> Approved)
     - Timestamp
     - Amount and Project Head.
   - State: *"These audit records are read-only and cannot be deleted by any user, ensuring complete financial compliance."*

---

## Part 3: Bonus Features (Section 11)

### 3.1 Configurable Approval Rules
1. Navigate to **Fund Management -> Configuration -> Approval Rules**.
2. **Video Action:** Show the list of rules you can create. Create a rule stating:
   - Request Type: `Allocation`
   - Min Amount: `50001`, Max Amount: `200000`
   - Sequence: 1 for `GM`, 2 for `Finance`.
3. State: *"This dynamic matrix replaces hardcoded logic, allowing companies to change approval chains on the fly."*

### 3.2 Bank Email Integration (Prototype)
1. Navigate to **Fund Management -> Bank Emails / Incoming Integrations**.
2. **Video Action:** Open a mock Email Record in the system. Show how the Python prototype extracted the:
   - Bank Name
   - Transaction Reference
   - Amount
3. Highlight the State field: Show it is in **"Pending Verification"**.
4. State: *"The system parses emails via Regex, checks for duplicate transaction references to prevent double entry, and keeps the fund pending until Finance manually confirms it."*

### 3.3 Dashboard and Notifications
1. Navigate to **Fund Management -> Dashboard**.
2. **Video Action:** Show the beautiful board displaying:
   - Total funds received
   - Unassigned balances vs Held amounts
   - Project-specific expenses.
3. Show the **Chatter** (right side or bottom of records) displaying automated Odoo notifications for approvals and rejections.

---

## Part 4: The 13-Step Sample Demonstration (Section 13)

*Note: For the best video, follow these exact steps consecutively.*

1. **Receive BDT 1,000,000:**
   - Go to **Fund Accounts**, create an account, and add an incoming fund of `1,000,000`.
   - Confirm it.
2. **Request BDT 600,000 for Project A:**
   - Go to **Allocations**. Create new.
   - Target: `Project A`. Amount: `600,000`.
   - Click **Submit**.
3. **Show the Hold:**
   - Go back to your Fund Account.
   - **Video Action:** Point out that `600,000` is now sitting in the **Held Amount** field, preventing anyone else from spending it.
4. **Reject Request & Return Money:**
   - Open the Allocation. Click **Reject**.
   - Go back to Fund Account.
   - **Video Action:** Show the Held Amount is back to `0`, and Unassigned Balance is back to `1,000,000`.
5. **Re-submit and Approve:**
   - Go to the Allocation. Set to Draft -> Submit -> **Approve**.
6. **Transfer BDT 200,000 from A to B:**
   - Go to **Transfers**. Create new.
   - Source: `Project A`. Destination: `Project B`. Amount: `200,000`.
   - Click **Submit**.
7. **Show Transfer Hold:**
   - Go to Project A's record.
   - **Video Action:** Show that its available balance has dropped, and the `200,000` is locked in transfer-hold pending approval.
8. **Approve Transfer:**
   - Click **Approve** on the Transfer. Project B now officially has the `200,000`.
9. **Create Requisition for Project B:**
   - Go to **Requisitions**. Create new.
   - Target: `Project B`. Amount: `150,000`.
   - Submit and Approve.
10. **Create Partial Bill:**
    - From the Requisition, click **Create Bill** (or go to Vendor Bills and link the requisition).
    - Amount: `100,000`. Post the bill.
11. **Show Remaining Billable:**
    - Go back to the Requisition.
    - **Video Action:** Show the system automatically calculated the Remaining Billable Amount as `50,000`.
12. **Block Over-Billing:**
    - Try to create another bill against this requisition for `60,000`.
    - **Video Action:** Click Post. Show the red Validation Error stating the amount exceeds the remaining `50,000`.
13. **Block Cross-Project Billing:**
    - Try to create a bill linking Project B's requisition, but select Project A's expense head or account.
    - **Video Action:** Show the system actively blocking the mismatch via strict database validation.

---
*End of Demonstration.*
