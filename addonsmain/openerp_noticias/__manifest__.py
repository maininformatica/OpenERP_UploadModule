# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- Contactos y Noticias",

    'summary': """
        Modulo Extendido de Noticias para Contactos
    """,

    'description': """
        Modulo Extendido de Llamadas para Contacto y Relacion de DialogFlow
    """,

    'author': "MAIN INFORMATICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'website_blog'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': False,       
}