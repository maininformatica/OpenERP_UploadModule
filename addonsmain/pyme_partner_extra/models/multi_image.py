# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MultiImages(models.Model):
    _name = "multi.images"

    image = fields.Binary('Imagen')
    description = fields.Char('Descripcion')
    title = fields.Char('Nombre')
    partner_id = fields.Many2one('res.partner')


class ProductTemplate(models.Model):
    _inherit = "res.partner"

    multi_images = fields.One2many('multi.images', 'partner_id',
                                   'Multi Images')
