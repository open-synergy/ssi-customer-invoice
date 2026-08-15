# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2 import IntegrityError

from odoo import tools
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCustomerInvoiceType(YamlTransactionCase):
    """Test the ``customer_invoice_type`` master data model.

    Covers the YAML scenario plus the Python-pure test below that
    asserts a database-level ``NOT NULL`` violation, which YAML's
    ``expect_error`` cannot express.
    """

    def test_customer_invoice_type(self):
        """Run the ``customer_invoice_type`` create/activate YAML scenario."""
        self.run_yaml_scenario("test_data_customer_invoice_type.yaml")

    def test_create_without_journal_id_is_rejected(self):
        """Python murni -- pemicu P5 (L-22: exception di luar 12 tipe
        `expect_error`).

        `journal_id` is a required Many2one without a Python-level
        `@api.constrains`, so a missing value only fails at the database
        NOT NULL constraint (``psycopg2.errors.NotNullViolation``, a
        subclass of ``psycopg2.IntegrityError``). That exception type is
        not among the 12 supported by YAML's `expect_error`, so this
        negative path cannot be expressed in
        test_data_customer_invoice_type.yaml.
        """
        account_type = self.env.ref("account.data_account_type_receivable")
        receivable_account = self.env["account.account"].create(
            {
                "code": "CITRC%d" % self.env["account.account"].search_count([]),
                "name": "Customer Invoice Type Python Test Receivable",
                "user_type_id": account_type.id,
                "reconcile": True,
            }
        )
        with self.assertRaises(IntegrityError), tools.mute_logger("odoo.sql_db"):
            self.env["customer_invoice_type"].create(
                {
                    "name": "No Journal Type",
                    "code": "CITPY001",
                    "receivable_account_id": receivable_account.id,
                }
            )
