# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase
from psycopg2.errors import NotNullViolation

from odoo.tests import tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestCustomerInvoice(YamlTransactionCase):
    def test_customer_invoice(self):
        self.run_yaml_scenario("test_data_customer_invoice.yaml")

    def _create_invoice_with_lines(self):
        """Shared fixture for the P2/P3 python-pure tests below. Built fresh
        here (not taken from the YAML registry, which only lives during
        ``run_yaml_scenario``).
        """
        receivable_acc_type = self.env.ref("account.data_account_type_receivable")
        income_acc_type = self.env.ref("account.data_account_type_revenue")
        account = self.env["account.account"].create(
            {
                "code": "CIP2%d" % self.env["account.account"].search_count([]),
                "name": "P2/P3 Customer Invoice Receivable",
                "user_type_id": receivable_acc_type.id,
                "reconcile": True,
            }
        )
        income_account_1 = self.env["account.account"].create(
            {
                "code": "CIE2%d" % self.env["account.account"].search_count([]),
                "name": "P2/P3 Customer Invoice Income 1",
                "user_type_id": income_acc_type.id,
            }
        )
        income_account_2 = self.env["account.account"].create(
            {
                "code": "CIE3%d" % self.env["account.account"].search_count([]),
                "name": "P2/P3 Customer Invoice Income 2",
                "user_type_id": income_acc_type.id,
            }
        )
        journal = self.env["account.journal"].create(
            {
                "name": "P2/P3 Customer Invoice Journal",
                "code": "CIJ2%d" % self.env["account.journal"].search_count([]),
                "type": "sale",
            }
        )
        invoice_type = self.env["customer_invoice_type"].create(
            {
                "name": "P2/P3 Customer Invoice Type",
                "code": "/",
                "journal_id": journal.id,
                "receivable_account_id": account.id,
            }
        )
        customer = self.env["res.partner"].create(
            {"name": "P2/P3 Customer Invoice Partner", "is_company": True}
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
        Line = self.env["customer_invoice.line"]
        line_1 = Line.create(
            {
                "customer_invoice_id": invoice.id,
                "name": "Line 1",
                "account_id": income_account_1.id,
                "uom_quantity": 1,
                "price_unit": 100000.0,
            }
        )
        line_2 = Line.create(
            {
                "customer_invoice_id": invoice.id,
                "name": "Line 2",
                "account_id": income_account_2.id,
                "uom_quantity": 2,
                "price_unit": 75000.0,
            }
        )
        return invoice, line_1, line_2

    def test_journal_entry_has_one_receivable_line_and_matching_credit_lines(self):
        """Python murni -- pemicu P3 (L-06: isi/urutan baris x2m tak bisa
        di-assert dari YAML -- `type: o2m`/`m2m` hanya mendukung
        count/contains/exact terhadap satu field relasional secara
        keseluruhan, bukan filter per akun atau per debit/kredit).

        Setelah ``action_open``, ``move_id.line_ids`` harus berisi tepat
        satu baris pada ``receivable_account_id`` (debit > 0, credit == 0)
        dan satu baris credit > 0 pada masing-masing ``account_id`` milik
        setiap ``customer_invoice.line``.
        """
        invoice, line_1, line_2 = self._create_invoice_with_lines()
        invoice.with_context(bypass_policy_check=True).action_open()

        self.assertEqual(invoice.state, "open")
        self.assertTrue(invoice.move_id)
        self.assertEqual(invoice.move_id.state, "posted")

        receivable_lines = invoice.move_id.line_ids.filtered(
            lambda ml: ml.account_id == invoice.receivable_account_id
        )
        self.assertEqual(len(receivable_lines), 1)
        self.assertGreater(receivable_lines.debit, 0.0)
        self.assertEqual(receivable_lines.credit, 0.0)

        for line in (line_1, line_2):
            income_lines = invoice.move_id.line_ids.filtered(
                lambda ml: ml.account_id == line.account_id
            )
            self.assertEqual(len(income_lines), 1)
            self.assertEqual(income_lines.debit, 0.0)
            self.assertGreater(income_lines.credit, 0.0)

    def test_receivable_line_debit_equals_amount_total(self):
        """Python murni -- pemicu P2 (L-04: tidak ada toleransi float di
        YAML untuk nilai moneter; ``equals`` adalah ``!=`` mentah).

        ``debit`` baris piutang pada ``move_id`` harus tepat sama dengan
        ``amount_total`` dokumen.
        """
        invoice, _line_1, _line_2 = self._create_invoice_with_lines()
        invoice.with_context(bypass_policy_check=True).action_open()

        receivable_line = invoice.move_id.line_ids.filtered(
            lambda ml: ml.account_id == invoice.receivable_account_id
        )
        self.assertEqual(receivable_line.debit, invoice.amount_total)

    @mute_logger("odoo.sql_db")
    def test_create_without_type_id_violates_not_null_constraint(self):
        """Python murni -- pemicu P5 (L-22: NotNullViolation di luar 12 tipe
        `expect_error`).

        ``type_id`` wajib (`required=True`) tapi Odoo tidak menegakkan field
        wajib di layer Python saat `create()` -- baris INSERT dikirim apa
        adanya dan constraint NOT NULL di kolom database yang menolaknya,
        sehingga exception yang muncul adalah
        `psycopg2.errors.NotNullViolation` (turunan `psycopg2.IntegrityError`),
        bukan salah satu dari 12 tipe yang didukung `expect_error` YAML.
        `mute_logger` membungkam baris ERROR yang NORMAL dituliskan
        PostgreSQL di sini agar `oca_checklog_odoo` tidak menggagalkan CI
        walau test-nya sendiri lulus.
        """
        customer = self.env["res.partner"].create(
            {"name": "P5 Customer Invoice Partner", "is_company": True}
        )
        journal = self.env["account.journal"].create(
            {"name": "P5 Customer Invoice Journal", "code": "CIP5J", "type": "sale"}
        )
        account = self.env["account.account"].create(
            {
                "name": "P5 Customer Invoice Receivable",
                "code": "CIP5001",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        with self.assertRaises(NotNullViolation):
            self.env["customer_invoice"].create(
                {
                    "partner_id": customer.id,
                    "date": "2024-01-15",
                    "date_due": "2024-02-15",
                    "currency_id": self.env.ref("base.USD").id,
                    "pricelist_id": self.env.ref("product.list0").id,
                    "journal_id": journal.id,
                    "receivable_account_id": account.id,
                }
            )
