from odoo import models, fields, api

class pickingValorado(models.Model):
    # Herencia de la tabla de ventas
     _inherit = 'stock.picking'
    
     
     amount_untaxed = fields.Float(string='Base Imponible', store=True, readonly=True)
     amount_tax = fields.Float(string='Impuestos', store=True, readonly=True)
     amount_total = fields.Float(string='Total', store=True, readonly=True)
     payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term')
     fiscal_position_id = fields.Many2one('account.fiscal.position', oldname='fiscal_position', string='Fiscal Position')
                          