# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class Users(models.Model):
    _inherit = 'res.users'
    rasabot_state = fields.Selection(
        [
            ('not_initialized', 'No Inicializado'),
            ('onboarding_command', 'Online'),
            ('disabled', 'Disabled'),
        ], string="Estado RasaBot", readonly=True, required=True, default="not_initialized")  # keep track of the state: correspond to the code of the last message sent
