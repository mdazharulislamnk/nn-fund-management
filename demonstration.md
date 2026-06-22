# Odoo Fund Management - Demonstration Guide By Azhar

This guide details exactly how to deploy the environment and navigate the interface to manually verify the features, security constraints, and financial logic of the module.

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
