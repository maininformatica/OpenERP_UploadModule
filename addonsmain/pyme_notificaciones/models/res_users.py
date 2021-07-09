# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval


class UsersAvisos(models.Model):
    _inherit = 'res.users'

    envia_telegram =  fields.Selection([('False', 'NO'),('telegram', 'SI')], 'Notificaciones via Telegram', required=True, default='telegram', related='partner_id.notifica_telegram')
    envia_bot = fields.Selection([('False', 'NO'),('bot', 'SI')], 'Notificaciones via Bot', required=True, default='bot', related='partner_id.notifica_bot')
    envia_mail = fields.Selection([('False', 'NO'),('email', 'SI')], 'Notificaciones via E-Mail', required=True, default='email', related='partner_id.notifica_mail')
    horario = fields.Many2one('pyme.notificaciones.gc', string='Horario', related='partner_id.horario')
    origencliente = fields.Char(string='Origen Registro')
    notification_type = fields.Selection([
        ('false', 'Sin Notificar'),
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in Odoo')],
        'Notification Management', required=True, default='false',
        help="Policy on how to handle Chatter notifications:\n"
             "- Handle by Emails: notifications are sent to your email address\n"
             "- Handle in Odoo: notifications appear in your Odoo Inbox")


    @api.model_create_multi
    def create(self, vals_list):
        users = super(UsersAvisos, self.with_context(default_customer=False)).create(vals_list)
        for user in users:
            user.partner_id.active = user.active
            if user.partner_id.company_id:
                user.partner_id.write({'company_id': user.company_id.id})

        mensajecliente = "Creacion de Nuevo Usuario"
        mensajeusuario = "Creacion de Nuevo Usuario"
        causa = "Nuevo Usuario / Contacto Creado"
        origen = "NUEVO"
        modo = "create"
        origencliente = users.origencliente
        iduser = users.id
        if str(origencliente) == "False":
            origencliente = "Odoo"
            users.write({'origencliente': origencliente})
        asunto = users.partner_id.name
        estado = origencliente
        asignado = False
        userid = 2
        print("\n\n ##################################################################       \n\n")
        self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), users.id ,mensajeusuario ,mensajecliente, users.partner_id.id, userid,causa,origen,modo,asignado,estado,asunto)
        return users