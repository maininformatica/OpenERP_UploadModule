# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

class PartnerNews(models.Model):
     # Herencia de la tabla de ventas
     ## _name = 'res.partner.noticias'
     _inherit = 'res.partner'

     # Añadir el estado Pedido a ventas
     
     
     noticiasrel  = fields.One2many('blog.post', 'author_id', string='Noticias')
     googleimageurl  = fields.Char(string='Google URL Image')
     descripcion = fields.Char(store=True, readonly=False, string='Descripcion')
     googleurl  = fields.Char(store=True, readonly=False, string='Google URL Maps')



     