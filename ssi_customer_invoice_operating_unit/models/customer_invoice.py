# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CustomerInvoice(models.Model):
    """
    Adds Operating Unit (OU) support to ``customer_invoice``.

    Extends the document with ``operating_unit_id`` (single OU, via
    ``mixin.single_operating_unit``), propagates it to the ``account.move``
    generated on ``action_open``, and guards against selecting a journal
    that does not allow the chosen OU.
    """

    _name = "customer_invoice"
    _inherit = [
        "customer_invoice",
        "mixin.single_operating_unit",
    ]

    operating_unit_id = fields.Many2one(
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.constrains("operating_unit_id", "journal_id")
    def _check_journal_operating_unit(self):
        """Validate ``operating_unit_id`` against the selected journal.

        Business rule: when ``journal_id.operating_unit_ids`` is set (the
        journal is restricted to specific operating units), the document's
        ``operating_unit_id`` must be one of them. Journals without any
        ``operating_unit_ids`` restriction are not checked.

        :raises UserError: if ``operating_unit_id`` is set and is not
            included in ``journal_id.operating_unit_ids``.
        """
        for record in self:
            if (
                record.journal_id.operating_unit_ids
                and record.operating_unit_id
                and record.operating_unit_id.id
                not in record.journal_id.operating_unit_ids.ids
            ):
                error_message = _(
                    """
Context: Check journal against operating unit
Database ID: %s
Problem: Journal %s is not allowed for operating unit %s
Solution: Select a journal that allows this operating unit, or select a \
different operating unit
"""
                    % (
                        record.id,
                        record.journal_id.name,
                        record.operating_unit_id.name,
                    )
                )
                raise UserError(error_message)

    def _prepare_standard_move(self):
        """Build the ``account.move`` values for this document.

        Extension point: adds ``operating_unit_id`` to the values
        prepared by ``customer_invoice``, so the ``account.move``
        generated on ``action_open`` carries the same operating unit
        as this document.

        :return: dict of ``account.move`` values
        """
        self.ensure_one()
        result = super()._prepare_standard_move()
        result["operating_unit_id"] = self.operating_unit_id.id
        return result
