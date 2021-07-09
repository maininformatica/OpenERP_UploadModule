# Copyright 2015 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015-2016 Oihane Crucelaegui <oihane@avanzosc.com>
# Copyright 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Lorenzo Battistini
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Order Type",
    "version": "11.0.1.1.0",
    "category": "Purchase Management",
    "author": "Grupo Vermon,"
              "AvanzOSC,"
              "Tecnativa,"
              "Agile Business Group,"
              "Niboo,"
              "Odoo Community Association (OCA),"
			  "Main Informatica Gandia, S.L.",
    "website": "https://main-informatica.com",
    "license": "AGPL-3",
    "depends": [
        'account',
        'purchase',
    ],
    ## "demo": [
    ##     "demo/purchase_order_demo.xml",
    ## ],
    "data": [
       "security/ir.model.access.csv",
       ## "security/security.xml",
        "views/purchase_order_view.xml",
        "views/purchase_order_type_view.xml",
        "views/account_invoice_view.xml",
        "views/res_partner_view.xml",
        "data/default_type.xml",
    ],
    'installable': True,
}
