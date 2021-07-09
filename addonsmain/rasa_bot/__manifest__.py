# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'OPENERP -- Bots',
    'version': '1.0',
    'category': 'Discuss',
    'summary': 'Metapaquete Para BOTS',
    'description': "",
    'website': 'https://www.odoo.com/page/discuss',
    'depends': ['mail'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'data': [
        'views/assets.xml',
        'views/res_users_views.xml',
        'data/mailbot_data.xml',
    ],
    'demo': [
        'data/mailbot_demo.xml',
    ],
    'qweb': [
        'views/discuss.xml',
    ],
}
