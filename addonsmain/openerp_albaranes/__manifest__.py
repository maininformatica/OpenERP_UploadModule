# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- Albaranes",

    'summary': """
        Albaranes Valorados""",

    'description': """
        Albaranes Valorados en Pyme.
    """,

    'author': "MAIN INFORMÁTICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','stock','sale_stock'],

    # always loaded
    'data': [
        ## 'views/stock_move.xml',
        ## 'data/data.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': False,

}