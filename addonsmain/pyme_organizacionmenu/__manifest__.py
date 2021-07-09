# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- HELP DESK",

    'summary': """
        Aplicación HELP DESK OPENERP
    """,

    'description': """
        Aplicación HELP DESK OPENERP
    """,

    'author': "MAIN INFORMATICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','intero_reload_form', 'pyme_emails', 'pyme_helpdesk', 'pyme_productividad', 'pyme_rasa', 'pyme_telegram', 'pyme_notificaciones','muk_web_theme'],

    # always loaded
    'data': [
        'views/menu.xml',
        'views/views.xml',

    ],
    # only loaded in demonstration mode


    'installable': True,
    'auto_install': False,
    'application': True,       
}