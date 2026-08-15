# Deactivate Customer Invoice Type

> **Module:** ssi_customer_invoice\
> **Model:** `customer_invoice_type`\
> **Menu:** Financial Accounting > Configuration > Customer Invoice Types\
> **Actor:** user in group `Customer Invoice Type`\
> **Active:** `true` → `false`\
> **Requires:** `01-create`

## Pre-Condition

- None.

## Flow

1. Open the **Financial Accounting > Configuration > Customer Invoice Types** menu.
2. Select one or more records to deactivate (check the checkbox).
3. Click **Action** > **Archive**.
4. Click **OK** to confirm.

## Post-Condition

- The records are archived and no longer appear in the default list view.
- Deactivated types cannot be selected as **Type** on new customer invoices.
- Existing customer invoices that already use this type are not affected.
