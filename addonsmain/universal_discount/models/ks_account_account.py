from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    ks_enable_discount = fields.Boolean(string="Activar Descuento Global")
    ks_sales_discount_account = fields.Many2one('account.account', string="Cuenta Contable Descuento Global en VENTAS")
    ks_purchase_discount_account = fields.Many2one('account.account', string="Cuenta Contable Descuento Global en COMPRAS")


class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_enable_discount = fields.Boolean(string="Activar Descuento Global", related='company_id.ks_enable_discount', readonly=False)
    ks_sales_discount_account = fields.Many2one('account.account', string="Cuenta Contable Descuento Global en VENTAS", related='company_id.ks_sales_discount_account', readonly=False)
    ks_purchase_discount_account = fields.Many2one('account.account', string="Cuenta Contable Descuento Global en COMPRAS", related='company_id.ks_purchase_discount_account', readonly=False)
