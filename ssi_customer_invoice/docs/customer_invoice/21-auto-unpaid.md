# Auto Transition to Unpaid — Customer Invoice

> **Module:** ssi_customer_invoice\
> **Model:** `customer_invoice`\
> **Menu:** Financial Accounting > Account Receivable > Customer Invoice\
> **Actor:** system (`base.automation`), when the receivable move line becomes unreconciled\
> **State:** `done` → `open`\
> **Requires:** `20-auto-paid`

## Pre-Condition

- Record is in **Paid** status.
- The document has a receivable journal item (**Receivable Move Line**) linked to its
  accounting entry.

## Flow

This transition is not triggered by a user action. It runs automatically
(`base.automation`) whenever the receivable journal item of the document becomes no
longer fully reconciled — for example, after the reconciled customer payment is
undone/unreconciled, so that the **Realized** field changes from checked to unchecked.

## Post-Condition

- Status changes to **Unpaid**.
