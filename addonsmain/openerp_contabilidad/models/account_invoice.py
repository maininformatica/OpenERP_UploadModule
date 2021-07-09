# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'account.invoice'


    ## def _get_order_type(self):
    ##     return self.env['ir.sequence'].get('seq.seq').search([], limit=1)
    
    # Añadir el estado Pedido a ventas
    sequence_id  = fields.Char('Sequence', readonly=False)
    sequence_type = fields.Many2one('ir.sequence', string="Serie")
    
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('seq.seq')
        vals['sequence_id'] = seq
        return super(AccountInvoice, self).create(vals)

