# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Customer Invoice + Operating Unit",
    "version": "14.0.1.0.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_customer_invoice",
        "ssi_operating_unit_mixin",
        "ssi_financial_accounting_operating_unit",
    ],
    "data": [
        "security/res_group/customer_invoice.xml",
        "security/ir_rule/customer_invoice.xml",
        "view/customer_invoice.xml",
    ],
    "demo": [],
}
