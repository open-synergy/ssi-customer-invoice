# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCustomerInvoice(YamlTransactionCase):
    """Cover Operating Unit (OU) behavior on ``customer_invoice``.

    Exercises the ``operating_unit_id`` field, the journal-vs-OU
    constraint, and OU propagation to the generated ``account.move``.
    """

    def test_customer_invoice(self):
        """Run the operating unit scenarios for ``customer_invoice``."""
        self.run_yaml_scenario("test_data_customer_invoice.yaml")
