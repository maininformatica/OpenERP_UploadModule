# -*- coding: utf-8 -*-
{
    'name': "WebSite Main Informatica BLOCK",

    'summary': """
        Modulo para Crear OBJETOS HTML en el WEBSITE Editor""",

    'description': """
        Modulo para Crear OBJETOS HTML en el WEBSITE Editor
    """,

    'author': "Main Informatica Gandia, S.L.",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # The website module has to be installed and is needed to add a building block
    'depends': ['website'],

    # always loaded
    'data': [
        # Load the snippets (building block code) when installing
        'views/snippets.xml',
		'views/templates.xml',
    ]
}