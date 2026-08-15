# Reject Customer Invoice

> **Module:** ssi_customer_invoice
> **Model:** `customer_invoice`
> **Menu:** Financial Accounting > Account Receivable > Customer Invoice
> **Actor:** user in group *Customer Invoice — Validator* registered as an active approver on the record
> **State:** `confirm` → `reject`
> **Requires:** `04-confirm`

## Pre-Condition

- Record is in **Waiting for Approval** status.
- User is registered as an active approver on the record (in **Approvers**).
- User has _Can Reject_ access right.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Invoice** menu.
2. Open the record to reject.
3. Click the **Reject** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Rejected**.
