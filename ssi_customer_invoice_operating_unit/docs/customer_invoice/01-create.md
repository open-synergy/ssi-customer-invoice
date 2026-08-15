# Create Customer Invoice

> **Module:** `ssi_customer_invoice_operating_unit`\
> **Extends:** `ssi_customer_invoice` — model `customer_invoice`, aksi `01-create`

## Additional Fields

When this module is installed, the create form gains one field:

- **Operating Unit**: The operating unit that owns this document. Editable while the
  record is in **Draft** status; becomes read-only once the document leaves draft. Only
  visible to users with multi-company operating unit access
  (`operating_unit.group_multi_operating_unit`).

## Modified Validation

- Saving fails with a `UserError` if **Journal** is restricted to a set of operating
  units (its **Operating Unit** list is not empty) and the document's **Operating Unit**
  is not one of them. Journals without any operating unit restriction accept any
  **Operating Unit**, including none.

## Modified — Record Visibility

- The Customer Invoice list is filtered by operating unit (record rule). A user in the
  `Operating Unit` group who has no operating unit assigned cannot read or write
  invoices owned by any operating unit.

## Additional Post-Condition

- When the invoice is opened (see the base IK's confirm/approve actions), the accounting
  entry (`account.move`) generated for it carries the same **Operating Unit** as this
  document. If **Operating Unit** was left empty, the generated entry has no operating
  unit either.
