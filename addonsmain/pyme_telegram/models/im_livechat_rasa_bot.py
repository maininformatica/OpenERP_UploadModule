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


class LiveChatChannel(models.Model):
    _inherit = 'im_livechat.channel'

    tipochatbot = fields.Selection([('telegram', 'Telegram'),('odoobot', 'Charla en Vivo ODOO')], string="Tipo de BOT", related="bot.tipochatbot")
    
    @api.multi
    def quitar(self):
      idchannel = self.id
      iduser = self.users.id
      sqlrel = "DELETE FROM im_livechat_channel_im_user WHERE user_id='" + str(iduser) + "' and channel_id='" + str(idchannel) + "'"
      print("LA SQL es: " + str(sqlrel) +"")
      self.env.cr.execute(str(sqlrel))
      self.write({'bot': False,'users': False,'rasabot_online': False, 'users_ids': False})
      return {}