# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- Notificaciones",

    'summary': """
        Modulo Notificaciones Modelos PYME
    """,

    'description': """
        Modulo Notificaciones Modelos PYME
    """,

    'author': "MAIN INFORMATICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','pyme_emails', 'calendar', 'project', 'pyme_partner_extra', 'pyme_rasa','pyme_productividad','pyme_helpdesk','im_livechat'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_partner.xml',
        'views/res_users.xml',
        'views/mail_channel.xml',
        'views/im_livechat.xml',
        'views/ir_model.xml',
        'views/notificaciones_data.xml',
    ],
    # only loaded in demonstration mode


    'installable': True,
    'auto_install': False,
    'application': False,       
}