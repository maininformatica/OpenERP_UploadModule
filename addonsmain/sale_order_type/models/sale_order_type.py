# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderTypology(models.Model):
    _name = 'sale.order.type'
    _description = 'Type of sale order'

    @api.model
    def _get_domain_sequence_id(self):
        seq_type = self.env.ref('sale.seq_sale_order')
        return [('code', '=', seq_type.code)]

    @api.model
    def _get_selection_picking_policy(self):
        return self.env['sale.order'].fields_get(
            allfields=['picking_policy'])['picking_policy']['selection']

    def default_picking_policy(self):
        default_dict = self.env['sale.order'].default_get(['picking_policy'])
        return default_dict.get('picking_policy')

    name = fields.Char(string='Prefijo', required=True, translate=True)
    description = fields.Text(string='Descripción', translate=True)
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence', string='Entry Sequence', copy=False,
        domain=_get_domain_sequence_id)
    nextnum = fields.Integer(string='Proximo Numero', store=True)
    journal_id = fields.Many2one(
        comodel_name='account.journal', string='Billing Journal',
        domain=[('type', '=', 'sale')])
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string='Warehouse')
    picking_policy = fields.Selection(
        selection='_get_selection_picking_policy', string='Shipping Policy',
        default=default_picking_policy)
    company_id = fields.Many2one(
        'res.company',
        related='warehouse_id.company_id', store=True, readonly=True)
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Term')
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist')
    incoterm_id = fields.Many2one('stock.incoterms', 'Incoterm')
    type_doc = fields.Selection([('Presupuesto','Presupuesto'),('Pedido','Pedido'),('Albaran','Albaran'),],string='Tipo Documento')
    habitual = fields.Boolean(string='Habitual')

    @api.multi
    def action_worflow_default_pr(self, default=None):
        ## Buscamos el tipo
        self.env.cr.execute("""UPDATE sale_order_type SET habitual='f' where type_doc='Presupuesto'""")
        self.write({'habitual': 't'})
    def action_worflow_default_pd(self, default=None):
        ## Buscamos el tipo
        self.env.cr.execute("""UPDATE sale_order_type SET habitual='f' where type_doc='Pedido'""")
        self.write({'habitual': 't'})
    def action_worflow_default_ab(self, default=None):
        ## Buscamos el tipo
        self.env.cr.execute("""UPDATE sale_order_type SET habitual='f' where type_doc='Albaran'""")
        self.write({'habitual': 't'})

 