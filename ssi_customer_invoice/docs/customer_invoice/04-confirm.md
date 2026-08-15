# Confirm Customer Invoice

> **Module:** ssi_customer_invoice\
> **Model:** `customer_invoice`\
> **Menu:** Financial Accounting > Account Receivable > Customer Invoice\
> **Actor:** user in group `Customer Invoice / User`\
> **State:** `draft` → `confirm`\
> **Requires:** `01-create`

## Pre-Condition

- Record is in **Draft** status.
- User has _Can Confirm_ access right (**User** access group or higher).

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Invoice** menu.
2. Open the record to confirm.
3. Click the **Confirm** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Waiting for Approval**.
- The tax lines on the **Detail** tab are automatically recomputed from the detail lines
  as part of confirming the record.
