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


class NotificacionesIrModel(models.Model):
    _inherit = "ir.model"

    modelonotificado = fields.Boolean(default=False, string="Este Modelo puede Ser Notificado")