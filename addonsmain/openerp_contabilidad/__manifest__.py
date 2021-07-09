# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- Contabilidad",

    'summary': """
        Contabilidad de PYME""",

    'description': """
        Contabilidad más facil.
    """,

    'author': "MAIN INFORMÁTICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'l10n_es_vat_book','account_financial_report','l10n_es_mis_report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_account_form.xml',
        'data/data.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': False,

}