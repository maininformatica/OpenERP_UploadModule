# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools import safe_eval
from odoo.exceptions import UserError, AccessError, ValidationError

class SupportTeam(models.Model):
    _name = "helpdesk_lite.team"
    _inherit = ['mail.alias.mixin', 'mail.thread']
    _description = "Support Team"
    _order = "name"

    name = fields.Char('Nombre Equipo', required=True, translate=True)
    user_id = fields.Many2one('res.users', string='Responsable de Grupo')
    member_ids = fields.One2many('res.users', 'helpdesk_team_id', string='Miembros')
    reply_to = fields.Char(string='Reply-To',
                           help="La dirección de correo electrónico incluida en la 'Reply-To' de todos los correos electrónicos enviados por Odoo sobre casos en este equipo de soporte")
    color = fields.Integer(string='Color Index', help="Color del Equipo")
    active = fields.Boolean(default=True, string="Inactivo / Archivado")
    nuevo = fields.Boolean(string='Grupo por Defecto',default=False)
    company_id = fields.Many2one('res.company', string='Compañia',
        default=lambda self: self.env['res.company']._company_default_get())



    ## _sql_constraints = [('helpdesk_lite_team_nuevo_unique', 'unique(nuevo)', 'Solo Puede haber un Grupo por Defecto. Para establecer uno nuevo debes quitar el otro previamente .')]


    @api.model
    def create(self, values):
        self.env.cr.execute("select count(*) from helpdesk_lite_team where nuevo='t'")
        result = self.env.cr.fetchone()
        contador = result[0]      
        nuevo = values['nuevo']
        if str(contador) != "0" and str(nuevo) == "True":
           raise UserError("Solo puede haber un Grupo por Defecto. Desactiva previamente el otro para poder elegir de nuevo")
        return super(SupportTeam, self.with_context(mail_create_nosubscribe=True)).create(values)



    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        if not user_id:
            user_id = self.env.uid
        team_id = None
        if 'default_team_id' in self.env.context:
            team_id = self.env['helpdesk_lite.team'].browse(self.env.context.get('default_team_id'))
        if not team_id or not team_id.exists():
            team_id = self.env['helpdesk_lite.team'].sudo().search(
                ['|', ('user_id', '=', user_id), ('member_ids', '=', user_id)],
                limit=1)
        if not team_id:
            team_id = self.env.ref('helpdesk_lite.team_alpha', raise_if_not_found=False)
        return team_id


    def get_alias_model_name(self, vals):
        return 'helpdesk_lite.ticket'

    def get_alias_values(self):
        values = super(SupportTeam, self).get_alias_values()
        defaults = safe_eval(self.alias_defaults or "{}")
        defaults['team_id'] = self.id
        values['alias_defaults'] = defaults
        return values
