# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError, Warning

import subprocess
import pycurl, json, requests
from io import StringIO
import datetime
import json as simplejson

class NotifGruposChannel(models.Model):

    _inherit = "im_livechat.channel"

    users_ids = fields.Many2many('res.users', string='Usuarios a Notificar')