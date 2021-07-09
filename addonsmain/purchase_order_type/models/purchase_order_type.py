# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderTypology(models.Model):
    _name = 'purchase.order.type'
    _description = 'Type of purchase order'

    @api.model
    def _get_domain_sequence_id(self):
        seq_type = self.env.ref('purchase.seq_purchase_order')
        return [('code', '=', seq_type.code)]


    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence', string='Entry Sequence', copy=False,
        domain=_get_domain_sequence_id)
    journal_id = fields.Many2one(
        comodel_name='account.journal', string='Billing Journal',
        domain=[('type', '=', 'purchase')])
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string='Warehouse')
    
    company_id = fields.Many2one(
        'res.company',
        related='warehouse_id.company_id', store=True, readonly=True)
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Term')
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist')
    incoterm_id = fields.Many2one('stock.incoterms', 'Incoterm')
    type_doc = fields.Selection([('Presupuesto','Presupuesto'),('Pedido','Pedido'),('Albaran','Albaran'),],string='Tipo Documento')
