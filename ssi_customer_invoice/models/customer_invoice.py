# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


class CustomerInvoice(models.Model):
    """
    Represents a customer invoice as a standalone SSI transactional document.

    Tracks the full lifecycle of a sales invoice issued to a customer --
    draft, waiting for approval, unpaid (open), and paid (done) -- with
    its own sequence-based document number, multiple approval, and
    policy-controlled actions. This model owns its own table; it does not
    share storage with ``account.move``. Detail lines, taxes, and the
    generation of the accompanying ``account.move`` are handled by
    separate modules/items.
    """

    _name = "customer_invoice"
    _description = "Customer Invoice"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.transaction_date_due",
        "mixin.transaction_partner",
        "mixin.company_currency",
        "mixin.many2one_configurator",
        "mixin.transaction_pricelist",
        "mixin.account_move",
        "mixin.account_move_single_line",
    ]

    # A. Atribut Multiple Approval
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # B. Atribut Auto-insert View Element
    _automatically_insert_view_element = True
    _automatically_insert_multiple_approval_page = True
    # ``open`` -> ``done`` is driven by the reconciliation of the receivable
    # journal item (base.automation ``customer_invoice_open_2_done``), never
    # by a user. Both attributes below keep the Done button out of the form
    # and tree headers and keep ``done_ok`` off the Policy page.
    _automatically_insert_done_button = False
    _automatically_insert_done_policy_fields = False

    # C. Atribut Form View
    _statusbar_visible_label = "draft,confirm,open,done"
    _policy_field_order = [
        "confirm_ok",
        "open_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # D. Atribut Search View
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_open",
        "dom_done",
        "dom_reject",
        "dom_cancel",
    ]

    # E. Atribut Sequence
    _create_sequence_state = "open"

    # E2. Atribut Perhitungan Pajak (mixin.account_move)
    _tax_lines_field_name = "tax_ids"
    _tax_on_self = False
    _tax_source_recordset_field_name = "line_ids"
    _price_unit_field_name = "price_unit"
    _quantity_field_name = "uom_quantity"

    # E3. Atribut Accounting Entry (mixin.account_move_single_line -- receivable
    # journal item created on the header itself)
    _journal_id_field_name = "journal_id"
    _move_id_field_name = "move_id"
    _accounting_date_field_name = "date"
    _currency_id_field_name = "currency_id"
    _company_currency_id_field_name = "company_currency_id"
    _account_id_field_name = "receivable_account_id"
    _partner_id_field_name = "partner_id"
    # ``_analytic_account_id_field_name`` is deliberately left at the mixin
    # default (``False``): the analytic account belongs to the detail lines,
    # so only the income journal items carry one. The receivable journal item
    # created here stays free of any analytic account.
    _amount_currency_field_name = "amount_total"
    _date_field_name = "date"
    _label_field_name = "name"
    _date_due_field_name = "date_due"
    _need_date_due = True
    _normal_amount = "debit"

    # F. Definisi Field
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "Unpaid"),
            ("done", "Paid"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
        default="draft",
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="customer_invoice_type",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Customer invoice type that determines the default journal, "
        "receivable account, and the allowed currencies/pricelists for "
        "this document.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Currency used to express every monetary amount on this " "document.",
    )
    pricelist_id = fields.Many2one(
        string="Pricelist",
        comodel_name="product.pricelist",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Pricelist used to determine the customer price of the "
        "products sold on this document.",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Accounting journal in which the resulting accounting "
        "entry of this document will be posted.",
    )
    receivable_account_id = fields.Many2one(
        string="Receivable Account",
        comodel_name="account.account",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        help="Receivable account debited for the total amount owed by "
        "the customer when this document is posted.",
    )
    analytic_account_ids = fields.Many2many(
        string="Analytic Accounts",
        comodel_name="account.analytic.account",
        relation="rel_customer_invoice_2_analytic_account",
        column1="customer_invoice_id",
        column2="analytic_account_id",
        compute="_compute_analytic_account_ids",
        store=True,
        compute_sudo=True,
        help="Analytic accounts used by the detail lines of this document. "
        "Filled automatically from the detail lines and never entered "
        "directly on the header.",
    )
    customer_document_number = fields.Char(
        string="Customer Document Number",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
        help="Reference number of the original document requested by "
        "the customer (e.g. their own purchase order number), used to "
        "cross-check against the customer's own records.",
    )
    allowed_currency_ids = fields.Many2many(
        string="Allowed Currencies",
        comodel_name="res.currency",
        compute="_compute_allowed_currency_ids",
        store=False,
        compute_sudo=True,
        help="Currencies that may be selected on this document, "
        "determined by the currency selection method configured on "
        "the selected Type.",
    )
    allowed_pricelist_ids = fields.Many2many(
        string="Allowed Pricelists",
        comodel_name="product.pricelist",
        compute="_compute_allowed_pricelist_ids",
        store=False,
        compute_sudo=True,
        help="Pricelists that may be selected on this document, "
        "determined by the pricelist selection method configured on "
        "the selected Type.",
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed Products",
        comodel_name="product.product",
        compute="_compute_allowed_product_ids",
        store=False,
        compute_sudo=True,
        help="Products that may be selected on the detail lines of this "
        "document, determined by the product selection method "
        "configured on the selected Type.",
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name="customer_invoice.line",
        inverse_name="customer_invoice_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Product/service detail lines being invoiced on this "
        "document. Used to compute the untaxed amount and, together "
        "with the applicable taxes, the tax lines.",
    )
    tax_ids = fields.One2many(
        string="Taxes",
        comodel_name="customer_invoice.tax",
        inverse_name="customer_invoice_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Tax lines computed automatically from the detail lines "
        "(or entered manually).",
    )
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        compute="_compute_amount",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of the price subtotal of every detail line.",
    )
    amount_tax = fields.Monetary(
        string="Tax",
        compute="_compute_amount",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Sum of the tax amount of every tax line.",
    )
    amount_total = fields.Monetary(
        string="Total",
        compute="_compute_amount",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Untaxed amount plus tax amount.",
    )
    move_id = fields.Many2one(
        string="Move",
        comodel_name="account.move",
        readonly=True,
        copy=False,
        help="Journal entry generated when this document is opened. Left "
        "empty for documents without detail lines, which move directly "
        "to Paid without waiting for reconciliation.",
    )
    receivable_move_line_id = fields.Many2one(
        string="Receivable Move Line",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
        help="Journal item on the receivable account created together "
        "with ``move_id``. Its reconciliation status drives the "
        "automatic Unpaid/Paid transition.",
    )
    realized = fields.Boolean(
        string="Realized",
        related="receivable_move_line_id.reconciled",
        store=True,
        compute_sudo=True,
        help="Technical flag mirroring whether the receivable journal "
        "item has been fully reconciled. Drives the automatic "
        "done/open state transition through base.automation.",
    )
    amount_realized = fields.Monetary(
        string="Realized Amount",
        compute="_compute_realized",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Portion of the total amount already settled, derived from "
        "the receivable journal item's residual amount.",
    )
    amount_residual = fields.Monetary(
        string="Residual Amount",
        compute="_compute_realized",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Portion of the total amount still outstanding on the "
        "receivable journal item.",
    )

    # G. Compute Methods
    @api.depends("type_id")
    def _compute_allowed_currency_ids(self):
        """Compute the currencies selectable on this document.

        Delegates to the many2one configurator, resolving the
        selection method/manual list/domain/Python code configured on
        ``type_id.currency_*``. Empty when ``type_id`` is not set.
        """
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="res.currency",
                    method_selection=record.type_id.currency_selection_method,
                    manual_recordset=record.type_id.currency_ids,
                    domain=record.type_id.currency_domain,
                    python_code=record.type_id.currency_python_code,
                )
            record.allowed_currency_ids = result

    @api.depends("type_id")
    def _compute_allowed_pricelist_ids(self):
        """Compute the pricelists selectable on this document.

        Delegates to the many2one configurator, resolving the
        selection method/manual list/domain/Python code configured on
        ``type_id.pricelist_*``. Empty when ``type_id`` is not set.
        """
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="product.pricelist",
                    method_selection=record.type_id.pricelist_selection_method,
                    manual_recordset=record.type_id.pricelist_ids,
                    domain=record.type_id.pricelist_domain,
                    python_code=record.type_id.pricelist_python_code,
                )
            record.allowed_pricelist_ids = result

    @api.depends("type_id")
    def _compute_allowed_product_ids(self):
        """Compute the products selectable on this document's lines.

        Delegates to the many2one configurator, resolving the
        selection method/manual list/domain/Python code configured on
        ``type_id.product_*``. Empty when ``type_id`` is not set.
        """
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="product.product",
                    method_selection=record.type_id.product_selection_method,
                    manual_recordset=record.type_id.product_ids,
                    domain=record.type_id.product_domain,
                    python_code=record.type_id.product_python_code,
                )
            record.allowed_product_ids = result

    @api.depends(
        "line_ids.analytic_account_id",
    )
    def _compute_analytic_account_ids(self):
        """Compute the analytic accounts used by this document's lines.

        Collects ``analytic_account_id`` of every detail line into a
        duplicate-free set; lines without an analytic account
        contribute nothing, so the result is empty when no line carries
        one.
        """
        for record in self:
            result = record.line_ids.mapped("analytic_account_id")
            record.analytic_account_ids = result

    @api.depends(
        "line_ids.price_subtotal",
        "tax_ids.tax_amount",
    )
    def _compute_amount(self):
        """Compute the untaxed, tax, and total amounts of this document.

        ``amount_untaxed`` sums ``price_subtotal`` of every detail
        line; ``amount_tax`` sums ``tax_amount`` of every tax line;
        ``amount_total`` is their sum.
        """
        for record in self:
            amount_untaxed = sum(record.line_ids.mapped("price_subtotal"))
            amount_tax = sum(record.tax_ids.mapped("tax_amount"))
            record.amount_untaxed = amount_untaxed
            record.amount_tax = amount_tax
            record.amount_total = amount_untaxed + amount_tax

    @api.depends(
        "receivable_move_line_id.amount_residual_currency",
        "receivable_move_line_id.reconciled",
        "amount_total",
    )
    def _compute_realized(self):
        """Compute the realized and residual amounts of this document.

        Derived from ``receivable_move_line_id``'s residual amount in
        document currency; both stay zero when there is no receivable
        journal item yet (e.g. document without detail lines).
        """
        for record in self:
            amount_realized = 0.0
            amount_residual = 0.0

            if record.receivable_move_line_id:
                amount_residual = (
                    record.receivable_move_line_id.amount_residual_currency
                )
                amount_realized = record.amount_total - amount_residual

            record.amount_realized = amount_realized
            record.amount_residual = amount_residual

    # H. Onchange Methods
    @api.onchange("type_id")
    def onchange_journal_id(self):
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.journal_id

    @api.onchange("type_id")
    def onchange_receivable_account_id(self):
        self.receivable_account_id = False
        if self.type_id:
            self.receivable_account_id = self.type_id.receivable_account_id

    # I. Action Methods
    def action_compute_tax(self):
        """Recompute the tax lines from the current detail lines.

        User-triggered button available while the document is still
        editable. Runs with ``sudo()`` so the recomputation is not
        blocked by tax line access rights.
        """
        for record in self.sudo():
            record._compute_tax()

    def _compute_tax(self):
        """Recompute the standard tax lines of this document.

        Thin wrapper around ``mixin.account_move``'s
        ``_recompute_standard_tax`` so both the button
        (``action_compute_tax``) and the pre-confirm hook
        (``_01_compute_tax``) share the same implementation.
        """
        self.ensure_one()
        self._recompute_standard_tax()

    # I2. Pre-confirm Hook: Recompute Tax
    @ssi_decorator.pre_confirm_action()
    def _01_compute_tax(self):
        """Recompute the tax lines before the document is confirmed.

        Runs on the ``pre_confirm_action`` slot, i.e. right before the
        document leaves ``draft`` for ``confirm``, so the tax lines
        reflect the final detail lines even if the user never clicked
        ``action_compute_tax`` manually.
        """
        self.ensure_one()
        self._recompute_standard_tax()

    # I3. Post-open Hooks: Create Accounting Entry / Skip Straight to Done
    @ssi_decorator.post_open_action()
    def _10_create_accounting_entry(self):
        """Create the accounting entry when the document is opened.

        Runs on the ``post_open_action`` slot, i.e. right after the
        document transitions to ``open``. Skipped when there are no
        detail lines (nothing to invoice) or when ``move_id`` is
        already set (idempotent on repeated open). Creates the
        ``account.move`` header, the receivable journal item on the
        header, one journal item per detail line and per tax line,
        then posts the move.
        """
        self.ensure_one()

        if not self.line_ids or self.move_id:
            return True

        self._create_standard_move()  # Mixin
        ml = self._create_standard_ml()  # Mixin
        self.write(
            {
                "receivable_move_line_id": ml.id,
            }
        )

        for line in self.line_ids:
            line._create_standard_ml()  # Mixin

        for tax in self.tax_ids:
            tax._create_standard_ml()  # Mixin

        self._post_standard_move()  # Mixin

    # I3a. Override: Add Partner to Standard Move Header
    def _prepare_standard_move(self):
        """Add the document partner to the ``account.move`` header.

        Extends the ``mixin.account_move`` values (``name``,
        ``journal_id``, ``date``) with ``partner_id``, reusing the
        existing ``_partner_id_field_name`` attribute already consumed
        by ``mixin.account_move_single_line`` for the receivable line,
        so the generated ``account.move`` carries the same partner as
        this document.

        :return: dict of ``account.move`` values
        """
        res = super()._prepare_standard_move()
        res["partner_id"] = getattr(self, self._partner_id_field_name).id
        return res

    @ssi_decorator.post_open_action()
    def _20_skip_open(self):
        """Skip straight from ``open`` to ``done`` when unbilled.

        Runs on the ``post_open_action`` slot, after
        ``_10_create_accounting_entry``. Documents without detail
        lines never get an accounting entry (``move_id`` stays
        empty), so there is nothing to reconcile before moving on to
        ``done``.
        """
        self.ensure_one()
        if not self.move_id:
            self.action_done()

    # I4. Post-cancel Hook: Delete Accounting Entry
    @ssi_decorator.post_cancel_action()
    def _30_delete_accounting_entry(self):
        """Delete the accounting entry when the document is cancelled.

        Runs on the ``post_cancel_action`` slot, i.e. right after the
        document transitions to ``cancel``, reverting the accounting
        entry created by ``_10_create_accounting_entry``.
        """
        self.ensure_one()
        self._delete_standard_move()  # Mixin

    # I5. Pre-cancel Hook: Reject Cancellation of a Paid Document
    @ssi_decorator.pre_cancel_check()
    def _40_check_no_payment(self):
        """Reject the cancellation of a document already partly paid.

        Runs on the ``pre_cancel_check`` slot, i.e. before the document
        leaves its current state for ``cancel``. Cancelling deletes the
        accounting entry (``_30_delete_accounting_entry``), which would
        strip the receivable journal item a customer payment is already
        reconciled against, so any settled amount forbids cancelling.

        :raises UserError: when ``amount_realized`` is above zero
        """
        self.ensure_one()

        if self.amount_realized > 0.0:
            error_message = """
                Document Type: %s
                Context: Cancel document
                Database ID: %s
                Problem: Document has already received payment
                Solution: Undo the reconciliation of the receivable journal
                item before cancelling this document
                """ % (
                self._description.lower(),
                self.id,
            )
            raise UserError(_(error_message))

    # I6. Pre-done Hook: Only the Machine May Finish the Document
    @ssi_decorator.pre_done_check()
    def _50_check_realized(self):
        """Reject finishing a document that is not fully reconciled.

        Runs on the ``pre_done_check`` slot, i.e. before the document
        moves to ``done``. This replaces the policy guard dropped along
        with the Done button (``_automatically_insert_done_button`` is
        ``False``, so ``_check_done_policy`` returns early): ``done`` is
        reachable only from ``open``, and only once the receivable
        journal item is reconciled -- or when there is no accounting
        entry at all, which is the ``_20_skip_open`` path for documents
        without detail lines.

        :raises UserError: when the document is not in ``open``, or has
            an accounting entry that is not fully reconciled yet
        """
        self.ensure_one()

        if self.state != "open" or (self.move_id and not self.realized):
            error_message = """
                Document Type: %s
                Context: Finish document
                Database ID: %s
                Problem: Document is not an unpaid document whose receivable
                journal item has been fully reconciled
                Solution: Reconcile the receivable journal item of this
                document; the transition to Paid then happens automatically
                """ % (
                self._description.lower(),
                self.id,
            )
            raise UserError(_(error_message))

    # J. Decorator: Insert Form Element
    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch

    # K. Override _get_policy_field
    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
            "cancel_ok",
            "restart_ok",
            "open_ok",
            "done_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res
