# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountAccount(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'account.account'

    # Añadir el estado Pedido a ventas
    debit  = fields.Float('Debe', readonly=True)
    credit  = fields.Float('Haber', readonly=True)
    balance  = fields.Float('Saldo', readonly=True)
    
    


