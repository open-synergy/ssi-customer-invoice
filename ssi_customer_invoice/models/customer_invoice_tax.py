# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CustomerInvoiceTax(models.Model):
    """
    Tax line of a customer invoice.

    Stores a single computed (or manually entered) tax entry associated
    with the detail lines of a customer invoice. Standard fields
    (``tax_id``, ``name``, ``account_id``, ``manual``, ``base_amount``,
    ``tax_amount``) are provided by ``mixin.tax_line``; this model only
    adds the link back to its parent ``customer_invoice`` and a handful
    of convenience fields mirrored from the header, following the
    pattern of ``employee_business_trip.tax``.
    """

    _name = "customer_invoice.tax"
    _description = "Customer Invoice - Tax"
    _inherit = [
        "mixin.tax_line",
    ]
    _order = "customer_invoice_id, id"

    # account.move.line
    _partner_id_field_name = "partner_id"
    _analytic_account_id_field_name = "analytic_account_id"
    _label_field_name = "name"
    _amount_currency_field_name = "tax_amount"
    _normal_amount = "credit"

    customer_invoice_id = fields.Many2one(
        string="# Customer Invoice",
        comodel_name="customer_invoice",
        required=True,
        ondelete="cascade",
    )

    # Convenience fields mirrored from the header.
    move_id = fields.Many2one(
        related="customer_invoice_id.move_id",
        compute_sudo=True,
    )
    account_move_line_id = fields.Many2one(
        string="Journal Item",
        comodel_name="account.move.line",
        copy=False,
    )
    currency_id = fields.Many2one(
        related="customer_invoice_id.currency_id",
        compute_sudo=True,
    )
    company_id = fields.Many2one(
        related="customer_invoice_id.company_id",
        compute_sudo=True,
    )
    company_currency_id = fields.Many2one(
        related="customer_invoice_id.company_currency_id",
        compute_sudo=True,
    )
    partner_id = fields.Many2one(
        related="customer_invoice_id.partner_id",
        compute_sudo=True,
    )
    date = fields.Date(
        related="customer_invoice_id.date",
        compute_sudo=True,
    )
