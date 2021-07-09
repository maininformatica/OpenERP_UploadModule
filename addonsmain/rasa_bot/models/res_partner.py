# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models

class Partner(models.Model):
    _inherit = 'res.partner'

    def _compute_im_status(self):
        #we asume that mail_bot _compute_im_status will be executed after bus _compute_im_status
        super(Partner, self)._compute_im_status()
        rasabot_id = self.env['ir.model.data'].xmlid_to_res_id("user_rasa_bot")
        for partner in self:
            if partner.id == rasabot_id:
                partner.im_status = 'bot'

    @api.model
    def get_mention_suggestions(self, search, limit=8):
        #add rasabot in mention suggestion when pinging in mail_thread
        [users, partners] = super(Partner, self).get_mention_suggestions(search, limit=limit)
        if len(partners) + len(users) < limit and "rasabot".startswith(search.lower()):
            rasabot = self.env.ref("user_rasa_bot")
            if not any([elem['id'] == rasabot.id for elem in partners]):
                if rasabot:
                    partners.append({'id': rasabot.id, 'name': rasabot.name, 'email': rasabot.email})
        return [users, partners]

