# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError, Warning

import subprocess
import pycurl, json, requests
from io import StringIO
import datetime
import json as simplejson
import sys
import fileinput
import os
import time
from shutil import copyfile
import socket
import shutil
import html2text
import telebot
import config
import xmlrpc.client
import time
from datetime import timedelta
from unidecode import unidecode
from telebot import types
from telebot.types import ReplyKeyboardMarkup,KeyboardButton,KeyboardButtonPollType,ReplyKeyboardRemove



class linficheronlu(models.Model):
  _inherit = "res.partner"



  @api.multi
  def envia_telegram(self):
      ## res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'send_telegram', 'view_stock_return_picking_form')
      ## res_id = res and res[1] or False
      partid = self.id
      telegramid = self.rasa_telegramid
      context = {'default_recipients': telegramid,'default_name': partid}
      return {
        'name': _('Enviar Telegram'),
        'view_type': 'form',
        'view_mode': 'form',
        ## 'view_id': [res_id],
        'res_model': 'send_telegram',
        'type': 'ir.actions.act_window',
        'target': 'new',
        'context':context} 