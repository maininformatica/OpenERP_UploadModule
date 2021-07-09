# -*- coding: utf-8 -*-
import itertools
import random
import time
import asyncio

from odoo import models, fields, api, _
import pycurl, json, requests
from odoo.exceptions import UserError, AccessError, ValidationError, Warning

class RasaBot(models.AbstractModel):
    _inherit = 'project.task'

    @api.model
    @api.multi
    def linkartareaticket(self):
        print("Dummy def para linkar modelos")