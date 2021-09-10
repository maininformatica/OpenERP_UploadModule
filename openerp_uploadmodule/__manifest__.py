# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- Upload Module",

    'summary': """
        Modulo para subir ficheros ZIP paquetizados por ODOO
    """,

    'description': """
        Modulo para subir ficheros ZIP paquetizados por ODOO
    """,

    'author': "MAIN INFORMATICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': False,       
}