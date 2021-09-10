# -*- coding: utf-8 -*-
{
    'name': "OpenERP - Upload Module",

    'summary': """
        Modulo para subir ficheros ZIP paquetizados por ODOO
    """,

    'description': """
        <b>Modulo para subir ficheros ZIP paquetizados por ODOO. Module to upload ZIP files packaged by ODOO.</b>
    """,

    'author': "MAIN INFORMATICA GANDIA SL",
    'website': "https://www.main-informatica.com/magazine/openerp/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',
    'license': 'LGPL-3',

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
