# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- Hotel",

    'summary': """
        Addons Extra a la Apliacion HOTEL MANAGEMENT""",

    'description': """
        Imágenes y Descripcion a Tipos de Habitaciones, Servicios y Comodidades.
        
        
        Se edita el fichero: addons/hotel_reservation/models/hotel_reservation.py LINEA 224
         Se comentan las comprobaciones de reservar bajo una condicion de numero inicial de personas
        
        
    """,

    'author': "MAIN INFORMÁTICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hotel', 'hotel_reservation','project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hotel_extra.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,

}