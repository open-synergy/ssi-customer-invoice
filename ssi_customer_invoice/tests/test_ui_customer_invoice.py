# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestUiCustomerInvoice(HttpCase):
    """UI/UX tour tests for ``customer_invoice``.

    Every ``test_*`` method below runs the tour pairing with the IK file
    named in its docstring (``docs/customer_invoice/NN-*.md``).
    Pre-Condition data required by each IK is prepared here in Python --
    never through UI steps -- following the tour authoring doctrine:
    prerequisite/background data belongs to ``setUpClass``, the tour itself
    only exercises the click-flow documented in the IK.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        receivable_acc_type = cls.env.ref("account.data_account_type_receivable")
        income_acc_type = cls.env.ref("account.data_account_type_revenue")

        cls.receivable_account = cls.env["account.account"].create(
            {
                "code": "TOURCIP",
                "name": "TOUR Customer Invoice Receivable",
                "user_type_id": receivable_acc_type.id,
                "reconcile": True,
            }
        )
        cls.income_account = cls.env["account.account"].create(
            {
                "code": "TOURCIE",
                "name": "TOUR Customer Invoice Income",
                "user_type_id": income_acc_type.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Customer Invoice Journal",
                "code": "TOURCIJ",
                "type": "sale",
            }
        )
        # Selection methods are left at their "domain" default with an
        # empty domain ("[]"), which resolves to "every record allowed" --
        # simplest configuration so the tour can freely pick any
        # currency/pricelist/product without fighting an allow-list.
        cls.invoice_type = cls.env["customer_invoice_type"].create(
            {
                "name": "TOUR Customer Invoice Type",
                "code": "TOURCIT",
                "journal_id": cls.journal.id,
                "receivable_account_id": cls.receivable_account.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "TOUR Customer Invoice Product"}
        )
        cls.currency = cls.env.ref("base.USD")
        cls.pricelist = cls.env.ref("product.list0")
        cls.cancel_reason = cls.env["base.cancel_reason"].create(
            {
                "name": "TOUR Customer Invoice Cancel Reason",
                "code": "TOURCICR",
                "global_use": True,
            }
        )

        cls.partner_create = cls.env["res.partner"].create(
            {"name": "TOUR Create Customer", "is_company": True}
        )
        cls.partner_edit = cls.env["res.partner"].create(
            {"name": "TOUR Edit Customer", "is_company": True}
        )
        cls.partner_delete = cls.env["res.partner"].create(
            {"name": "TOUR Delete Customer", "is_company": True}
        )
        cls.partner_confirm = cls.env["res.partner"].create(
            {"name": "TOUR Confirm Customer", "is_company": True}
        )
        cls.partner_approve = cls.env["res.partner"].create(
            {"name": "TOUR Approve Customer", "is_company": True}
        )
        cls.partner_reject = cls.env["res.partner"].create(
            {"name": "TOUR Reject Customer", "is_company": True}
        )
        cls.partner_cancel = cls.env["res.partner"].create(
            {"name": "TOUR Cancel Customer", "is_company": True}
        )
        cls.partner_restart = cls.env["res.partner"].create(
            {"name": "TOUR Restart Customer", "is_company": True}
        )
        cls.partner_compute_tax = cls.env["res.partner"].create(
            {"name": "TOUR Compute Tax Customer", "is_company": True}
        )

        cls.invoice_edit = cls._create_invoice(cls.partner_edit)
        cls.invoice_delete = cls._create_invoice(cls.partner_delete)
        cls.invoice_confirm = cls._create_invoice(cls.partner_confirm)

        cls.invoice_approve = cls._create_invoice(cls.partner_approve, with_line=True)
        cls.invoice_approve.with_context(bypass_policy_check=True).action_confirm()

        cls.invoice_reject = cls._create_invoice(cls.partner_reject)
        cls.invoice_reject.with_context(bypass_policy_check=True).action_confirm()

        cls.invoice_cancel = cls._create_invoice(cls.partner_cancel)

        cls.invoice_restart = cls._create_invoice(cls.partner_restart)
        cls.invoice_restart.with_context(bypass_policy_check=True).action_cancel(
            cls.cancel_reason
        )

        cls.invoice_compute_tax = cls._create_invoice(
            cls.partner_compute_tax, with_line=True
        )

    @classmethod
    def _create_invoice(cls, partner, with_line=False):
        """Pre-Condition helper: create a draft ``customer_invoice`` for
        ``partner``.

        Header fields normally auto-filled by onchange in the UI (journal,
        receivable account) are set explicitly here since Python
        ``create()`` does not trigger onchange.
        """
        invoice = cls.env["customer_invoice"].create(
            {
                "type_id": cls.invoice_type.id,
                "partner_id": partner.id,
                "date": "2026-01-15",
                "date_due": "2026-02-15",
                "currency_id": cls.currency.id,
                "pricelist_id": cls.pricelist.id,
                "journal_id": cls.journal.id,
                "receivable_account_id": cls.receivable_account.id,
            }
        )
        if with_line:
            cls.env["customer_invoice.line"].create(
                {
                    "customer_invoice_id": invoice.id,
                    "product_id": cls.product.id,
                    "name": cls.product.name,
                    "account_id": cls.income_account.id,
                    "uom_quantity": 1,
                    "price_unit": 100000.0,
                }
            )
        return invoice

    def test_create(self):
        """IK: docs/customer_invoice/01-create.md"""
        self.start_tour(
            "/web", "ssi_customer_invoice_customer_invoice_create", login="admin"
        )

    def test_edit(self):
        """IK: docs/customer_invoice/02-edit.md"""
        self.start_tour(
            "/web", "ssi_customer_invoice_customer_invoice_edit", login="admin"
        )

    def test_delete(self):
        """IK: docs/customer_invoice/03-delete.md"""
        self.start_tour(
            "/web", "ssi_customer_invoice_customer_invoice_delete", login="admin"
        )

    def test_confirm(self):
        """IK: docs/customer_invoice/04-confirm.md"""
        self.start_tour(
            "/web", "ssi_customer_invoice_customer_invoice_confirm", login="admin"
        )

    def test_approve(self):
        """IK: docs/customer_invoice/05-approve.md"""
        self.start_tour(
            "/web", "ssi_customer_invoice_customer_invoice_approve", login="admin"
        )

    def test_reject(self):
        """IK: docs/customer_invoice/06-reject.md"""
        self.start_tour(
            "/web", "ssi_customer_invoice_customer_invoice_reject", login="admin"
        )

    def test_cancel(self):
        """IK: docs/customer_invoice/10-cancel.md"""
        self.start_tour(
            "/web", "ssi_customer_invoice_customer_invoice_cancel", login="admin"
        )

    def test_restart(self):
        """IK: docs/customer_invoice/12-restart.md"""
        self.start_tour(
            "/web", "ssi_customer_invoice_customer_invoice_restart", login="admin"
        )

    def test_compute_tax(self):
        """IK: docs/customer_invoice/14-compute-tax.md"""
        self.start_tour(
            "/web",
            "ssi_customer_invoice_customer_invoice_compute_tax",
            login="admin",
        )
