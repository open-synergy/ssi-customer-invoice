# Cancel Customer Invoice

> **Module:** ssi_customer_invoice
> **Model:** `customer_invoice`
> **Menu:** Financial Accounting > Account Receivable > Customer Invoice
> **Actor:** user in group *Customer Invoice — Validator*
> **State:** `draft`/`confirm`/`open` → `cancel`
> **Requires:** `01-create`

## Pre-Condition

- Record is in **Draft**, **Waiting for Approval**, or **Unpaid** status.
- User has _Can Cancel_ access right (**Validator** access group).

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Invoice** menu.
2. Open the record to cancel.
3. Click the **Cancel** button.
4. In the wizard that appears, select the **Cancellation Reason**.
5. Click **Confirm**.

## Post-Condition

- Status changes to **Cancelled**.
- The accounting entry generated for this document (if any) is deleted.
