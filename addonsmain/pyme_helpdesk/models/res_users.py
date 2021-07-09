# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    helpdesk_team_id = fields.Many2one(
        'helpdesk_lite.team', 'Ticket Team',
        help='Equipo de soporte del que es miembro el usuario. Se utiliza para calcular los miembros de un equipo de soporte a través de la inversa one2many')
