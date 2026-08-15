# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiCustomerInvoiceType(HttpSavepointCase):
    """UI/UX tour tests for ``customer_invoice_type``.

    Every ``test_*`` method below runs the tour pairing with the IK file
    named in its docstring (``docs/customer_invoice_type/NN-*.md``).
    Pre-Condition data required by each IK is prepared here in Python --
    never through UI steps -- following the tour authoring doctrine:
    prerequisite/background data belongs to ``setUpClass``, the tour itself
    only exercises the click-flow documented in the IK.
    """

    @classmethod
    def setUpClass(cls):
        """Prepare Pre-Condition data shared by every tour in this class.

        Creates the accounting master data (journal, receivable
        account) and one ``customer_invoice_type`` record per tour
        that needs a record already in a given state
        (edit/delete/deactivate/activate).
        """
        super().setUpClass()

        receivable_acc_type = cls.env.ref("account.data_account_type_receivable")

        cls.journal = cls.env["account.journal"].create(
            {
                "name": "TOUR Customer Invoice Type Journal",
                "code": "TOURCITJ",
                "type": "sale",
            }
        )
        cls.receivable_account = cls.env["account.account"].create(
            {
                "code": "TOURCITR",
                "name": "TOUR Customer Invoice Type Receivable",
                "user_type_id": receivable_acc_type.id,
                "reconcile": True,
            }
        )

        cls.type_edit = cls._create_type("TOUR CIT Edit")
        cls.type_delete = cls._create_type("TOUR CIT Delete")
        cls.type_deactivate = cls._create_type("TOUR CIT Deactivate")
        cls.type_activate = cls._create_type("TOUR CIT Activate", active=False)

    @classmethod
    def _create_type(cls, name, active=True):
        """Pre-Condition helper: create a draft ``customer_invoice_type``
        record.

        Journal and Receivable Account are set explicitly since Python
        ``create()`` does not trigger onchange. ``code`` is left as ``"/"``
        (per Flow step 3 of ``docs/customer_invoice_type/01-create.md``,
        the allow-list-of-values later than a unique code is not needed
        here) so several records can share it without violating the
        unique-code constraint
        (``mixin.master_data._check_duplicate_code`` explicitly excludes
        ``code == "/"`` from the duplicate check).
        """
        return cls.env["customer_invoice_type"].create(
            {
                "name": name,
                "code": "/",
                "journal_id": cls.journal.id,
                "receivable_account_id": cls.receivable_account.id,
                "active": active,
            }
        )

    def test_create(self):
        """IK: docs/customer_invoice_type/01-create.md"""
        self.start_tour(
            "/web",
            "ssi_customer_invoice_customer_invoice_type_create",
            login="admin",
        )

    def test_edit(self):
        """IK: docs/customer_invoice_type/02-edit.md"""
        self.start_tour(
            "/web", "ssi_customer_invoice_customer_invoice_type_edit", login="admin"
        )

    def test_delete(self):
        """IK: docs/customer_invoice_type/03-delete.md"""
        self.start_tour(
            "/web",
            "ssi_customer_invoice_customer_invoice_type_delete",
            login="admin",
        )

    def test_deactivate(self):
        """IK: docs/customer_invoice_type/04-deactivate.md"""
        self.start_tour(
            "/web",
            "ssi_customer_invoice_customer_invoice_type_deactivate",
            login="admin",
        )

    def test_activate(self):
        """IK: docs/customer_invoice_type/05-activate.md"""
        self.start_tour(
            "/web",
            "ssi_customer_invoice_customer_invoice_type_activate",
            login="admin",
        )
