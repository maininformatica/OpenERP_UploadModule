# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models



class Stage(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Tickets will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "helpdesk_lite.stage"
    _description = "Stage of case"
    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char('Estado', required=True, translate=True)
    sequence = fields.Integer('Secuencia', default=1, help="Used to order stages. Lower is better.")
    requirements = fields.Text('Requisitos')
    fold = fields.Boolean('Doblado en Línea')
    legend_blocked = fields.Char(
        string='Kanban Blocked', translate=True)
    legend_done = fields.Char(
        string='Kanban Done', translate=True)
    legend_normal = fields.Char(
        string='Kanban Normal', translate=True)
    last = fields.Boolean('Último en LÍnea')
