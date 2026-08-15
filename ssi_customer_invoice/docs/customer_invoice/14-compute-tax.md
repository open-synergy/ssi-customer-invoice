# Compute Tax — Customer Invoice

> **Module:** ssi_customer_invoice
> **Model:** `customer_invoice`
> **Menu:** Financial Accounting > Account Receivable > Customer Invoice
> **Actor:** user in group *Customer Invoice — User*
> **Requires:** `01-create`

## Pre-Condition

- Record is in **Draft** status.
- The **Detail** tab has one or more lines filled in.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Invoice** menu.
2. Open the record.
3. On the **Detail** tab, click the **Compute Tax** button below the detail lines.

## Post-Condition

- The **Taxes** table on the **Detail** tab is recomputed from the detail lines:
  existing tax lines are replaced by the tax(es) configured on each detail line.
- **Untaxed Amount**, **Tax**, and **Total** are updated accordingly.
