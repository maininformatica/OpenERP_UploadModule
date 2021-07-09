# Copyright 2018 QubiQ (http://www.qubiq.es)
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'OPENERP --  Pyme Descuentos 2',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'QubiQ,'
              'Tecnativa,'
              'Odoo Community Association (OCA)'
              'Main Informatica Gandia, S.L.',
    'website': 'https://github.com/OCA/account-invoicing',
    'license': 'AGPL-3',
    'summary': 'Admnistra Descuentos en Lineas y Globales',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    
}
