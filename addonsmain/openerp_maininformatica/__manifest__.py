# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- PYME Base",

    'summary': """
        Creación de la Base PYME""",

    'description': """
        Metapaquete de instalacion de la adaptacion a PYME Española de ODOO11.
    """,

    'author': "MAIN INFORMÁTICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock', 'sale','purchase','purchase_order_type','sale_order_type','openerp_menus','openerp_contabilidad'],

    'data': [
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}