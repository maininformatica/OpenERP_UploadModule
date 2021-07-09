# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval

class PartnerAvisos(models.Model):
    _inherit = 'res.partner'

    notifica_telegram =  fields.Selection([('False', 'NO'),('telegram', 'SI')], 'Telegram', required=True, default='telegram')
    notifica_bot = fields.Selection([('False', 'NO'),('bot', 'SI')], 'Interno', required=True, default='bot')     
    notifica_mail = fields.Selection([('False', 'NO'),('email', 'SI')], 'Via E-Mail', required=True, default='email')        
    horario = fields.Many2one('pyme.notificaciones.gc', string='Horario')
    ## notification_type = fields.Selection([('no', 'NO'),('inbox', 'SI')], 'Notificaciones Internas', required=True, default='inbox')
