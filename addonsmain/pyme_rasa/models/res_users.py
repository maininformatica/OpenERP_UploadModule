from odoo import models, fields, api

class AddBotState(models.Model):
    _inherit = "res.users"

    odoobot_state = fields.Selection(selection_add=[('rasa', 'RasaBot')])
    esunbot = fields.Boolean(string='Es un BOT')    


   
