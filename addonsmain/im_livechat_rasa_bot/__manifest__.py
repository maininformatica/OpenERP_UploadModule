# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'RasaBot for livechat',
    'version': '1.0',
    'category': 'Discuss',
    'summary': 'Add livechat support for RasaBot',
    'description': "",
    'website': 'https://www.odoo.com/page/discuss',
    'depends': ['rasa_bot', 'im_livechat', 'website'],
    'data': [
        ## 'security/ir.model.access.csv',
        'views/im_chat.xml',
        'views/im_chat_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
