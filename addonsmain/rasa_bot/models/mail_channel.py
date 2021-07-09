# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError, Warning

class Channel(models.Model):
    _inherit = 'mail.channel'

    chatuser = fields.Many2one('res.partner', string='ID Channel')

    def _execute_command_help(self, **kwargs):
        super(Channel, self)._execute_command_help(**kwargs)
        self.env['rasa.bot']._apply_logic(self, kwargs, command="help")  # kwargs are not usefull but...

    @api.model
    def init_rasabot(self):
        
        if self.env.user.rasabot_state == 'not_initialized':
            partner = self.env.user.partner_id
            namebot = "RasaBot"
            ## rasabot_id = self.env['res.partner'].search([('name', 'ilike', namebot)], limit=1)
            rasabot_search = self.env['res.partner'].search([('name', 'ilike', namebot),"|", ("active", "=", True), ("active", "=", False),], limit=1)
            rasabot_id = int(rasabot_search.id)
            ## raise AccessError ("Partner: " + str(partner) + ". RasaBot: " + str(rasabot_id) + ".")
            channel = self.with_context(mail_create_nosubscribe=True).create({
                'channel_partner_ids': [(4, partner.id), (4, rasabot_id)],
                'public': 'private',
                'channel_type': 'chat',
                'email_send': False,
                'name': 'rasabot'
            })
            message = _("Hola. Bienvenido al Rasa Bot. Debes ir a Preferencias de tu Usuario para Inicializar el Bot de Rasa</b>")
            channel.sudo().message_post(body=message, author_id=rasabot_id, message_type="comment", subtype="mail.mt_comment")
            ## self.env.user.rasabot_state = 'onboarding_emoji'
            return channel

