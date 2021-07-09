# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- RASA Integration",

    'summary': """
        Conector RASA y RASA X""",

    'description': """
        Habilita la conectividad API entre Odoo y Rasa.
        Necesita estos PIP para poder instalar "pip install rasa-host googletrans"
    """,

    'author': "MAIN INFORMÁTICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'partner_autocomplete', 'pyme_partner_extra','rasa_bot','im_livechat_rasa_bot'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/rasa.xml',
        ## 'data/partner.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': False,

}