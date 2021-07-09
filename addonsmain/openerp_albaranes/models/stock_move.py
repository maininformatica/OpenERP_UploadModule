from odoo import models, fields, api

class pedidoVenta(models.Model):
    # Herencia de la tabla de ventas
     _inherit = 'stock.move'
    
     @api.multi
     def _compute_amount(self):
       """
       Compute the amounts of the Move line.
       """
       for line in self:
         ## price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
         ## taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
         line.update({
         ##   'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
         'price_total': 0,
         ##   'price_subtotal': taxes['total_excluded'],
         })
                                                                                                                                            
      
     # Total a la linea de Albaran
     price_total = fields.Float(compute='_compute_amount', string='Subtotal', readonly=True, store=True)            
     discount = fields.Float(string='Descuento (%)', default=0.0)
     tax_id = fields.Many2many('account.tax', string='Impuestos')
     

     