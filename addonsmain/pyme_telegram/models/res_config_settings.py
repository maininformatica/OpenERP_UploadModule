# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Website(models.Model):
    _inherit = "website"

    activate_share_buttons = fields.Boolean(string="Activar Botón TELEGRAM", default=True)
    target_url = fields.Selection([
        ('default', 'Url of the webpage where icons are located (default)'),
        ('home', 'Url of the homepage of your website'),
        ('custom_url', 'Custom url')], string="Target Url ")

    alignment_floating = fields.Selection([('left', 'Izquierda'), ('right', 'Derecha')], default="left", string="Ajuste Horizontal")
    left_bar_floating = fields.Integer(string="Margen Izquierdo px", default="-15")
    right_bar_floating = fields.Integer(string="Margen Derecho px", default="-15")
    top_bar_floating = fields.Integer(string="Margen Superior px", default="90")
    size_icon_bar = fields.Integer(string="Tamaño Icono px", default="18")
    icon_shape = fields.Selection([('square', 'Cuadrado'), ('circle', 'Círculo')], default="square", help="Tipo de Icono")
    more_buttons = fields.Boolean(string="Activar Más Botones", default=True)
    buttons_color = fields.Selection([('classic', 'Color Original'), ('theme_odoo', 'Color Dependiente Tema Odoo')], default="classic",
                                       string="Tipo de Color")

    buttons_share_ids = fields.Many2many(
        'share.social.list',
        'share_buttons_list_rel',
        'website_id',
        'share_social_list_id',
        string='Main Bar List',
        )

    @api.model
    def share_buttons(self, *args):
        t = request.httprequest.url
        url = args[2]
        split = re.split('; |, |\#|\?', url)[0]
        host_url = http.request.httprequest
        base_url = http.Response

        return url

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    activate_share_buttons = fields.Boolean(related="website_id.activate_share_buttons", readonly=False)
    more_buttons = fields.Boolean(related="website_id.more_buttons", readonly=False)

    alignment_floating = fields.Selection(related="website_id.alignment_floating", default="left", readonly=False)
    left_bar_floating = fields.Integer(related="website_id.left_bar_floating", readonly=False)
    right_bar_floating = fields.Integer(related="website_id.right_bar_floating", readonly=False)
    top_bar_floating = fields.Integer(related="website_id.top_bar_floating", readonly=False)
    size_icon_bar = fields.Integer(related="website_id.size_icon_bar", readonly=False)
    icon_shape = fields.Selection(related="website_id.icon_shape", readonly=False)
    buttons_share_ids = fields.Many2many(related="website_id.buttons_share_ids", readonly=False)
    buttons_color = fields.Selection(related="website_id.buttons_color", readonly=False)

    def execute(self):
        for row in self:
            if not row.alignment_floating:
                row.alignment_floating = 'left'
            if row.left_bar_floating == 0:
                row.left_bar_floating = int(-15)
            if row.right_bar_floating == 0:
                row.right_bar_floating = int(-15)
            if row.top_bar_floating == 0:
                row.top_bar_floating = int(90)
            if row.size_icon_bar == 0:
                row.size_icon_bar = int(18)
            if not row.icon_shape:
                row.icon_shape = 'square'
            if not row.buttons_color:
                row.buttons_color = 'classic'

            return super(ResConfigSettings, self).execute()
