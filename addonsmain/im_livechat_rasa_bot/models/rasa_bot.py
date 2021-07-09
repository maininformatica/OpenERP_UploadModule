# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, modules, tools, models, fields, _
from odoo.exceptions import AccessError, UserError

class RasaBot(models.AbstractModel):
    _inherit = 'rasa.bot'

    def _get_answer(self, record, body, values, command):
        odoobot_state = self.env.user.odoobot_state
        if self._is_bot_in_private_channel(record):
            if odoobot_state == "onboarding_ping" and self._is_bot_pinged(values):
                self.env.user.odoobot_state = "onboarding_canned"
                return _("Respuestas Prediseñadas por RASA")
            elif odoobot_state == "onboarding_canned" and values.get("canned_response_ids"):
                self.env.user.odoobot_state = "idle"
                return _("OJO !!! El OdooBot y el Rasa BOT estan en Marcha. Debes desconectar el ODOO-BOT")
            #repeat question if needed
            elif odoobot_state == 'onboarding_canned':
                return _("Aqui hay demasiada gente contestando. EL Rasa BOT esta activo y las Respuestas Prediseñadas Tambien. Debes desactivar uno de los dos")
        return super(RasaBot, self)._get_answer(record, body, values, command)


class LivechatRasaBot(models.AbstractModel):
    _inherit = 'im_livechat.channel'

    rasabot_online = fields.Boolean(string='Autocontestación Rasa Bot')
    canaltelegram = fields.Boolean(string='Canal de Telegram')
    users = fields.Many2one('res.users', string='Usuario Asignado', domain=[('esunbot','=',True)])
    bot = fields.Many2one('pyme.telegrambot', string='Inteligencia')


    @api.depends('users')
    def _compute_bot(self):
        for test in self:
            if test.rasabot_online == True and test.users.id != False:
               print("Es esto: " + str(test.users.id) + ".")
               test.bot = test.users.id
            else:
               test.bot = False
    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(LivechatRasaBot, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(LivechatRasaBot, self).write(vals)


    @api.multi
    def action_join(self):
        self.ensure_one()
        if self.rasabot_online == True:
           raise AccessError("NO puedes añadirte al CHAT Ya que es un Grupo Gestionado por un BOT")
        return self.write({'user_ids': [(4, self._uid)]})


    @api.multi
    def action_joinbot(self):
        self.ensure_one()
        iddoc = self.id
        userid = self.users.id
        self.env.cr.execute(""" DELETE FROM im_livechat_channel_im_user WHERE channel_id='%s'""" % (iddoc))
        bot = self.env['pyme.telegrambot'].search([('usuarioasignado', '=', self.users.id )]).id   
        return self.write({'bot': bot,'user_ids': [(4, userid)]})

    @api.multi
    def action_eliminabot(self):
        self.ensure_one()
        iddoc = self.id
        userid = self.users.id
        self.env.cr.execute(""" DELETE FROM im_livechat_channel_im_user WHERE channel_id='%s'""" % (iddoc))
        return {self.write({'bot': False, 'users': False, })}



class MailChannelRasaBot(models.Model):
    _inherit = 'mail.channel'

    chatcerrado = fields.Boolean(string='Chat Cerrado')
    chatiniciado = fields.Boolean(string='Primer contacto')


class LivechatRasaBotUserOnline(models.Model):
    
	_inherit = 'im_livechat.channel'
	# --------------------------
	# Channel Methods :: Reescribe im_livechat_channel.py de im_livechat
	# --------------------------
	@api.multi
	def get_available_users(self):
	    cosas = str(self.id)
	    self.env.cr.execute(""" select rasabot_online from im_livechat_channel where id='%s'""" % (cosas))
	    result = self.env.cr.fetchone()
	    if str(result[0]) == "True":
	        return self.sudo().user_ids.filtered(lambda user: 6)
	    else:
	        self.ensure_one()
	        return self.sudo().user_ids.filtered(lambda user: user.im_status == 'online')   