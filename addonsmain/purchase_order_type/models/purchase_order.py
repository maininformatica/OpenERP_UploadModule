# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _get_order_type(self):
        return self.env['purchase.order.type'].search([], limit=1)

    type_id = fields.Many2one(
        comodel_name='purchase.order.type', string='Type', default=_get_order_type)

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(PurchaseOrder, self).onchange_partner_id()
        if self.partner_id.purchase_type:
            self.type_id = self.partner_id.purchase_type

    @api.multi
    @api.onchange('type_id')
    def onchange_type_id(self):
        for order in self:
            if order.type_id.warehouse_id:
                order.warehouse_id = order.type_id.warehouse_id
           
            if order.type_id.payment_term_id:
                order.payment_term_id = order.type_id.payment_term_id.id
            if order.type_id.pricelist_id:
                order.pricelist_id = order.type_id.pricelist_id.id
            if order.type_id.incoterm_id:
                order.incoterm = order.type_id.incoterm_id.id

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/'and vals.get('type_id'):
            purchase_type = self.env['purchase.order.type'].browse(vals['type_id'])
            if purchase_type.sequence_id:
                vals['name'] = purchase_type.sequence_id.next_by_id()
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        if self.type_id.journal_id:
            res['journal_id'] = self.type_id.journal_id.id
        if self.type_id:
            res['purchase_type_id'] = self.type_id.id
        return res
