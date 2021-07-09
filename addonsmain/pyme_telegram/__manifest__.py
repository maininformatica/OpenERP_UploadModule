# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'OPENERP -- TELEGRAM',
    'category': 'Website/Website',
    'sequence': 141,
    'website': 'https://main-informatica.com',
    'summary': 'Red Social telegram en PYME',
    'version': '1.1',
    'description': "",
    'depends': ['website_mail', 'website_partner'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/view_share_buttons_list.xml',
        'views/res_config_settings.xml',
        'views/floating_telegram_share_buttons_assets.xml',
        'views/floating_telegram_share_buttons_templates.xml',
        'views/conftelegram.xml',
        'views/views.xml',
        'views/im_livechat_rasa_bot.xml',
        'views/partner.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'qweb': [
        'static/src/xml/website_share_buttons.xml'
    ],
    'installable': True,
    'application': False,
}