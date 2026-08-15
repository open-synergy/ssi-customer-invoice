# Edit Customer Invoice

> **Module:** `ssi_customer_invoice_operating_unit`\
> **Extends:** `ssi_customer_invoice` — model `customer_invoice`, aksi `02-edit`

## Additional Fields

- **Operating Unit**: Editable while the record is in **Draft** status, same as on
  create. Becomes read-only once the document leaves draft.

## Modified Validation

- Saving fails with a `UserError` if **Journal** is restricted to a set of operating
  units and the document's **Operating Unit** is not one of them. See `01-create` for
  details.
