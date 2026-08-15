# Auto Transition to Paid — Customer Invoice

> **Module:** ssi_customer_invoice
> **Model:** `customer_invoice`
> **Menu:** Financial Accounting > Account Receivable > Customer Invoice
> **Actor:** system (`base.automation`), triggered when the receivable move line becomes reconciled
> **State:** `open` → `done`
> **Requires:** `05-approve`

## Pre-Condition

- Record is in **Unpaid** status.
- The document has a receivable journal item (**Receivable Move Line**) linked to its
  accounting entry.

## Flow

This transition is not triggered by a user action. It runs automatically
(`base.automation`) whenever the receivable journal item of the document is fully
reconciled — for example, after a customer payment is matched/ reconciled against this
invoice's receivable move line, so that the **Realized** field changes from unchecked to
checked.

## Post-Condition

- Status changes to **Paid**.
