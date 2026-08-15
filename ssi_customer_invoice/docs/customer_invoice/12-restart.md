# Restart Customer Invoice

> **Module:** ssi_customer_invoice\
> **Model:** `customer_invoice`\
> **Menu:** Financial Accounting > Account Receivable > Customer Invoice\
> **Actor:** user in group `Customer Invoice / Validator`\
> **State:** `cancel`/`reject` → `draft`\
> **Requires:** `10-cancel`

## Pre-Condition

- Record is in **Cancelled** or **Rejected** status.
- User has _Can Restart_ access right (**Validator** access group).

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Invoice** menu.
2. Open the record to restart.
3. Click the **Restart** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status returns to **Draft**.
