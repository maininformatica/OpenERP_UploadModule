# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _
import re
from odoo.exceptions import AccessError, UserError
import pycurl, json, requests
import itertools
import random
import time
import asyncio
import html2text
from datetime import datetime


class MyModuleMessageWizard(models.TransientModel):
    _name = 'mymodule.message.wizard'
    _description = "Muestra mensaje"

    message = fields.Text('Mensaje', required=True)

    @api.multi
    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}