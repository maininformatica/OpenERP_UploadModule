# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- PYME Relacion CRM Facturacion",

    'summary': """
        Genera las relaciones del CRM con Facturacion PYME
    """,

    'description': """
        enera las relaciones del CRM con Facturacion PYME
        
        - Ventas:    Presupuesto / Pedido / Albarán / Factura
        - Compras:   Presupuesto / Pedido / Albarán / Factura
        - Tareas        

    """,

    'author': "MAIN INFORMATICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    ## 'depends': ['base', 'mail', 'fetchmail', 'sale', 'project', 'stock', 'purchase', 'calendar'],
    'depends': ['base', 'sale', 'stock', 'purchase', 'project', 'calendar'],


    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
		'views/message.xml',
		## 'menu.xml',
			
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
		'data/data_user.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,        
}
