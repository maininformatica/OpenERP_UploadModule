# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- Gestion de Correo Electrónico",

    'summary': """
        Modulo Extendido de WEBMAIL
    """,

    'description': """
        Modulo Extendido de WEBMAIL
    """,

    'author': "MAIN INFORMATICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/mail_templates.xml',
        'views/mails_data.xml',
    ],
    'qweb': [
        'static/src/xml/butonbusca.xml',
    ],

    # only loaded in demonstration mode


    'installable': True,
    'auto_install': False,
    'application': False,       
}