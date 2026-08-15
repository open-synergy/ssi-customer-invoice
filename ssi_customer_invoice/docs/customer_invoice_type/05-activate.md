# Activate Customer Invoice Type

> **Module:** ssi_customer_invoice
> **Model:** `customer_invoice_type`
> **Menu:** Financial Accounting > Configuration > Customer Invoice Types
> **Actor:** user in group *Customer Invoice Type*
> **Active:** `false` → `true`
> **Requires:** `04-deactivate`

## Pre-Condition

- None.

## Flow

1. Open the **Financial Accounting > Configuration > Customer Invoice Types** menu.
2. Enable the **Archived** filter in the search bar.
3. Select one or more records to reactivate (check the checkbox).
4. Click **Action** > **Unarchive**.

## Post-Condition

- The records are restored and appear again in the default list view.
- The types can be selected as **Type** on new customer invoices.
