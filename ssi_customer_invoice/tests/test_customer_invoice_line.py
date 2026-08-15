# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2.errors import NotNullViolation

from odoo.tests import tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestCustomerInvoiceLine(YamlTransactionCase):
    """Test the ``customer_invoice.line`` model create/compute flow.

    Covers the YAML scenario plus the Python-pure test below that
    asserts float-exact monetary amounts across untaxed and taxed
    lines, which the YAML DSL cannot express.
    """

    def test_customer_invoice_line(self):
        """Run the ``customer_invoice.line`` create/compute YAML scenario."""
        self.run_yaml_scenario("test_data_customer_invoice_line.yaml")

    def _create_invoice(self):
        """Create a bare ``customer_invoice`` header for line fixtures.

        Shared fixture for the P2/P5 python-pure tests below. Built
        fresh here (not taken from the YAML registry, which only
        lives during ``run_yaml_scenario``).

        :return: tuple of ``(customer_invoice, account.account)``
        """
        receivable_acc_type = self.env.ref("account.data_account_type_receivable")
        income_acc_type = self.env.ref("account.data_account_type_revenue")
        account = self.env["account.account"].create(
            {
                "code": "CILR%d" % self.env["account.account"].search_count([]),
                "name": "P2 Customer Invoice Line Receivable",
                "user_type_id": receivable_acc_type.id,
                "reconcile": True,
            }
        )
        line_account = self.env["account.account"].create(
            {
                "code": "CILE%d" % self.env["account.account"].search_count([]),
                "name": "P2 Customer Invoice Line Income",
                "user_type_id": income_acc_type.id,
            }
        )
        journal = self.env["account.journal"].create(
            {
                "name": "P2 Customer Invoice Line Journal",
                "code": "CILJ%d" % self.env["account.journal"].search_count([]),
                "type": "sale",
            }
        )
        invoice_type = self.env["customer_invoice_type"].create(
            {
                "name": "P2 Customer Invoice Line Type",
                "code": "/",
                "journal_id": journal.id,
                "receivable_account_id": account.id,
            }
        )
        customer = self.env["res.partner"].create(
            {"name": "P2 Customer Invoice Line Partner", "is_company": True}
        )
        invoice = self.env["customer_invoice"].create(
            {
                "type_id": invoice_type.id,
                "partner_id": customer.id,
                "date": "2024-01-15",
                "date_due": "2024-02-15",
                "currency_id": self.env.ref("base.USD").id,
                "pricelist_id": self.env.ref("product.list0").id,
                "journal_id": journal.id,
                "receivable_account_id": account.id,
            }
        )
        return invoice, line_account

    def test_compute_amount_with_and_without_tax(self):
        """Python murni -- pemicu P2 (L-04: tidak ada toleransi float di YAML
        untuk nilai moneter).

        Menguji dua skenario sekaligus, keduanya sama-sama soal presisi
        nilai moneter:
        1. ``amount_untaxed``/``amount_tax``/``amount_total`` dari 2 baris
           tanpa pajak (350.000 = 100.000 + 250.000, tax 0).
        2. Menambah 1 baris berpajak 11% lalu memanggil ``action_compute_tax``
           -- ``amount_tax`` harus sama persis dengan hasil
           ``account.tax.compute_all`` (bisa mengandung pembulatan mata uang)
           dan ``amount_total`` = untaxed + tax.
        """
        invoice, line_account = self._create_invoice()
        Line = self.env["customer_invoice.line"]
        line_1 = Line.create(
            {
                "customer_invoice_id": invoice.id,
                "name": "Line 1",
                "account_id": line_account.id,
                "uom_quantity": 1,
                "price_unit": 100000.0,
            }
        )
        line_2 = Line.create(
            {
                "customer_invoice_id": invoice.id,
                "name": "Line 2",
                "account_id": line_account.id,
                "uom_quantity": 1,
                "price_unit": 250000.0,
            }
        )
        self.assertEqual(invoice.amount_untaxed, 350000.0)
        self.assertEqual(invoice.amount_tax, 0.0)
        self.assertEqual(invoice.amount_total, 350000.0)

        # `account_id` on the "tax" repartition line is what ends up on
        # `customer_invoice.tax.account_id` (required=True) once
        # `action_compute_tax` recomputes the tax lines automatically --
        # without it, `compute_all()` returns no account for the tax
        # portion and the auto-created line violates NOT NULL.
        tax = self.env["account.tax"].create(
            {
                "name": "P2 VAT 11%",
                "amount_type": "percent",
                "amount": 11.0,
                "type_tax_use": "sale",
                "invoice_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": line_account.id,
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": line_account.id,
                        },
                    ),
                ],
            }
        )
        line_3 = Line.create(
            {
                "customer_invoice_id": invoice.id,
                "name": "Line 3 (taxed)",
                "account_id": line_account.id,
                "uom_quantity": 1,
                "price_unit": 100000.0,
                "tax_ids": [(6, 0, [tax.id])],
            }
        )
        invoice.action_compute_tax()

        expected_untaxed = (
            line_1.price_subtotal + line_2.price_subtotal + line_3.price_subtotal
        )
        taxes = tax.compute_all(
            line_3.price_unit,
            invoice.currency_id,
            line_3.uom_quantity,
            product=line_3.product_id,
            partner=False,
        )
        expected_tax = sum(t.get("amount", 0.0) for t in taxes.get("taxes", []))

        self.assertEqual(invoice.amount_untaxed, expected_untaxed)
        self.assertEqual(invoice.amount_tax, expected_tax)
        self.assertEqual(invoice.amount_total, expected_untaxed + expected_tax)

    @mute_logger("odoo.sql_db")
    def test_create_line_without_customer_invoice_id_violates_not_null_constraint(
        self,
    ):
        """Python murni -- pemicu P5 (L-22: `NotNullViolation` di luar 12
        tipe `expect_error`).

        ``customer_invoice_id`` wajib (`required=True`) tapi -- seperti
        sudah dibuktikan untuk `type_id` pada header `customer_invoice` di
        `test_customer_invoice.py` -- Odoo tidak menegakkan field wajib di
        layer Python saat `create()`; constraint NOT NULL di kolom
        database yang menolaknya sebagai `psycopg2.errors.NotNullViolation`.
        `mute_logger` membungkam baris ERROR NORMAL dari PostgreSQL di sini
        agar `oca_checklog_odoo` tidak menggagalkan CI walau test-nya lulus.
        """
        line_account = self.env["account.account"].create(
            {
                "code": "CILE5%d" % self.env["account.account"].search_count([]),
                "name": "P5 Customer Invoice Line Income",
                "user_type_id": self.env.ref("account.data_account_type_revenue").id,
            }
        )
        with self.assertRaises(NotNullViolation):
            self.env["customer_invoice.line"].create(
                {
                    "name": "Orphan Line",
                    "account_id": line_account.id,
                    "uom_quantity": 1,
                    "price_unit": 100000.0,
                }
            )
