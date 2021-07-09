# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_order_type(self):
        return self.env['purchase.order.type'].search([], limit=1)

    purchase_type_id = fields.Many2one(
        comodel_name='purchase.order.type',
        string='Purchase Type', default=_get_order_type)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id:
            if self.partner_id.purchase_type:
                self.purchase_type_id = self.partner_id.purchase_type.id

    @api.onchange('purchase_type_id')
    def onchange_purchase_type_id(self):
        if self.purchase_type_id.payment_term_id:
            self.payment_term = self.purchase_type_id.payment_term_id.id
        if self.purchase_type_id.journal_id:
            self.journal_id = self.purchase_type_id.journal_id.id
