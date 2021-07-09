# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- Gestion de Productividad",

    'summary': """
        Modulo Extendido de Productividad: Calendario, Tareas y Actividades
    """,

    'description': """
        Modulo Extendido de Productividad: Calendario, Tareas y Actividades
    """,

    'author': "MAIN INFORMATICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'calendar', 'project', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/portal_template.xml',

    ],
    # only loaded in demonstration mode


    'installable': True,
    'auto_install': False,
    'application': False,       
}