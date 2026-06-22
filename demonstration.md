# Complete Demonstration Script & Commands

This guide details exactly what to type in your terminal, which URLs to open, and the exact interface buttons to click during your video recording.

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
