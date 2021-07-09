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


import paramiko
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException


class NotifChannel(models.Model):

    _inherit = "mail.channel"
    notificado = fields.Boolean(string='Notificado')
    notificado_cuando = fields.Datetime(string='Notificado Cuando')
    leido = fields.Boolean(string='Leído', default=True)
    leido_por = fields.Many2one('res.users', string='Leído Por')    
    leido_cuando = fields.Datetime(string='Leído Cuando')


    def marcarleido(self):
        idchannel = self.id
        usuario = self.env.user.id
        self.write({'leido':True,'leido_por':usuario,'leido_cuando':fields.Datetime.now()})
        return {}



    