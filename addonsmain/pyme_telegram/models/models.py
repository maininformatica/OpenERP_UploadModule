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



class BotTelegram(models.Model):
  _name = "pyme.telegram"
  _description = "Bots Telegram"
  _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
  _order = "create_date desc"

  name = fields.Char(string='Nombre Bot Telegram', track_visibility='always', required=True)
  description = fields.Text('Notas Internas')
  inteligencia = fields.Many2one('pyme.telegrambot', string='Bot')
  tipochatbot = fields.Selection([('telegram', 'Telegram'),('odoobot', 'Charla en Vivo ODOO')], string="Servicio de Chat", related='inteligencia.tipochatbot')  
  token_telegram = fields.Char(string='Token Bot Telegram')
  activo = fields.Boolean(string='Activo para Recibir')
  idproceso = fields.Char(string='Proceso WEBHOOK')
  mensajestart = fields.Char(string='Mensaje Bienvenida')
  mensajehelp = fields.Char(string='Mensaje de Ayuda')
  usuariosnotificados = fields.Many2many('res.users', string='Usuarios a Notificar')
  telegramm2o = fields.One2many('pyme.bot.botonestelgram', 'telegramm2o', string='Botones')


  @api.multi
  def unlink(self):
        tareastxt=""
        for ticket in self:
          if ticket.activo == True: 
            raise UserError("El Bot figura como activo y este no puede ser Eliminado")
          if str(ticket.idproceso) != "False": 
            raise UserError("Espera a que el Proceso del WebHook se pare")

          self.env.cr.execute("select count(*) from pyme_notificaciones_configuracion where botutilizado=" + str(ticket.id) + " and enviabot='t'")
          result = self.env.cr.fetchone()
          seutiliza = result[0]
          if str(seutiliza) != "0": 
            raise UserError("El Bot está configurado " + str(seutiliza) + " vez/es en las configuraciones de Notificaciones. Debes desasociarlo de estas previamente")



        return super(BotTelegram, self).unlink()


  @api.multi
  def quitar(self):
      self.write({'inteligencia': False})
      return {}



class conftelegram(models.Model):
  _name = "pyme.telegrambot"
  _description = "Configiuracion I.A."
  _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
  _order = "create_date desc"

  name = fields.Char(string='Nombre Bot', track_visibility='always', required=True)
  description = fields.Text('Notas Internas')
  modo = fields.Selection([('lin', 'Respuestas Personalizadas'),('python', 'Python')], string="Responde", default='lin')
  tipochatbot = fields.Selection([('telegram', 'Telegram'),('odoobot', 'Charla en Vivo')], string="Servicio de Chat")
  tiponlu = fields.Selection([('usuario', 'Definido por Usuario'),('rasa', 'Rasa Server'),('python', 'Python')], string="NLU")
  servidor_rasa = fields.Char(string='URL WebHook RASA')
  servidor_rasam2o = fields.Many2one('rasa.server', string='RASA Server')
  token_telegram = fields.Char(string='Token Bot Telegram')
  usuarioasignado = fields.Many2one('res.users', string='Usuario BOT')
  channels = fields.One2many('im_livechat.channel','bot', string='Charla en Vivo')
  telegrambots = fields.One2many('pyme.telegram','inteligencia', string='Bots de Telegram')
  rasaserver = fields.Many2one('rasa.server', string='Rasa Server')
  logicapython = fields.Many2one('pyme.ficheronlu', string='Lógica Python')
  salidavacia = fields.Text('Salida Vacia')
  salidanoentiendo = fields.Text('Salida No Entiendo')
  linnlu = fields.One2many('pyme.linnlu', 'nlu', string='Lineas NLU')
  eligetelegram = fields.Many2one('pyme.telegram', string="Bot Telegram")  
  eligeimlivechat = fields.Many2one('im_livechat.channel', string="Charla en Vivo")



  @api.multi
  def anyadebott(self):
           iddocumento = self.id
           userid = self.usuarioasignado.id
           if str(userid) == "False":
              raise AccessError("No Hay usuario Bot Creado. Debes crear uno antes de asignarlo a un Canal de Entrada")
           tipochatbot = self.tipochatbot
           existen = ""
           eligetelegramid = self.eligetelegram.id
           eligetelegram = self.eligetelegram
           for bots in self.telegrambots:
              existen += str(bots.id) + ","
           if str(eligetelegramid) in str(existen):
              raise AccessError("El Bot que has escogido ya existe en la Ficha actual.")
           else:
              restb = self.env['pyme.telegram'].browse(eligetelegramid)
              restbw = restb.write({'inteligencia': iddocumento})
              self.write({'eligetelegram': False})
              return {}

  @api.multi
  def anyadeboto(self):
           iddocumento = self.id
           tipochatbot = self.tipochatbot
           existen = ""
           eligeimlivechatid = self.eligeimlivechat.id
           eligeimlivechatname = self.eligeimlivechat.name
           eligeimlivechat = self.eligeimlivechat
           userid = self.usuarioasignado.id
           if str(userid) == "False":
              raise AccessError("No Hay usuario Bot Creado. Debes crear uno antes de asignarlo a un Canal de Entrada")
           for bots in self.channels:
              existen += str(bots.id) + ","
           if str(eligeimlivechatid) in str(existen):
              raise AccessError("El Bot que has escogido ya existe en la Ficha actual.")
           else:

              self.env.cr.execute("SELECT count(*) FROM im_livechat_channel_im_user WHERE channel_id='" + str(eligeimlivechatid) + "'")
              resultv = self.env.cr.fetchone()
              contador = resultv[0]
              print("COntador: " + str(contador) + "")
              if str(contador) == "0":
                 restb = self.env['im_livechat.channel'].browse(eligeimlivechatid)
                 restbw = restb.write({'bot': iddocumento,'rasabot_online': True, 'users': userid})
                 joinb = restb.action_joinbot()
                 self.write({'eligeimlivechat': False})
              else:
                 raise AccessError("La Charla En Vivo: " + str(eligeimlivechatname) + " ya tiene asignado algún Usuario. Debe estar Vacía para poder Agregar un Sistema de Autocontestación por BOT.")
              return {}




  @api.onchange('servidor_rasam2o')
  def _onchange_servidor_rasam2o(self):
      idactual = self.servidor_rasam2o.id
      if str(idactual) != "False":
        srvrasa = self.servidor_rasam2o.id
        estadosrvrasa = self.servidor_rasam2o.state
        if str(estadosrvrasa) != "connected":
           raise UserError("El Servidor Rasa Seleccionado no está conectado o no puedo establecer conexión con el.")
        idnlurasa = self.env['pyme.nlu'].search([('rasaserver', '=', True )]).id
        if str(idnlurasa) == "False":
           raise UserError("No hay definido un Motor NLU Que acepte RASA. Debes generar uno y marchar el Check de Servidor Rasa")
        ip = self.servidor_rasam2o.url
        port = self.servidor_rasam2o.puertorasa
        self.servidor_rasa = str(ip) + ":" + str(port)
        self.motor_nlu = idnlurasa

  @api.multi
  def generausuario(self, record, command=None):
           iddocumento = self.id
           iddocumento = self.name
           orderline_obj = self.env['res.users']
           nameuser = "Bot " + str(iddocumento) + ""
           user_vals = {
              'name': nameuser,
              'login': nameuser,
              'share': False,
              'esunbot': True,
              'odoobot_state': 'disabled',
              'rasabot_state': 'disabled',
              'share': False,
              'sel_groups_1_9_10': 1,}
           user_id = self.env['res.users'].create(user_vals)
           self.write({'usuarioasignado': user_id.id})
           return {}



  def telegram_bot_sendtext(self,bot_message,chatid,token,buttonstelegram):
    bot_token = str(token)
    bot_chatID = str(chatid)
    ### if "(False) a enviado un correo" in bot_message: 
    ###   print("Esto NO lo debo enviar: " + str(bot_message))
    ###   return {}
    ### else:
    ### send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    ### response = requests.get(send_text)
    ### r = requests.get("https://api.telegram.org/bot" + str(bot_token) + "/deleteWebhook")
    ### r.json()

    mensaje = bot_message.replace('<p>','').replace('</p>','')
    h = html2text.HTML2Text()
    mensajetxt = h.handle(bot_message)
    token = str(bot_token)
    bot = telebot.TeleBot(bot_token, threaded=False)
    markup = telebot.types.InlineKeyboardMarkup()
    partner_id = self.env['res.partner'].search([('rasa_telegramid', '=', str(chatid))], limit=1).id
    #### print("\n\n *************** BOTONES ***********")
    if buttonstelegram != []:
      for botones in buttonstelegram:
        print("-- El Botón Relegram es: " + str(botones) + "")
        botontexto = botones[0]
        botontipo = botones[1]
        botondata = botones[2]
        botondoc = botones[3]
        botonnum = botones[4]
        iddoc = self.env[str(botondoc)].search([('id', '=', int(botonnum))], limit=1).id
        botondata = botondata.replace('$idcliente',str(partner_id))
        botontexto = botontexto.replace('$idcliente',str(partner_id))
        botondata = botondata.replace('$docid',str(iddoc))
        botontexto = botontexto.replace('$docid',str(iddoc))

        if str(botontipo) == "url":
           markup.add(telebot.types.InlineKeyboardButton(text=str(botontexto), url=str(botondata)))
        else:
           markup.add(telebot.types.InlineKeyboardButton(text=str(botontexto), callback_data=str(botondata)))
    ### print("\n\n")
    ### try: 
    ###   if buttonstelegram != []:
    ###     btn1 = markup.add(types.InlineKeyboardButton('Link a Main', url ='https://main-informatica.com'))
    ###   bot.send_message(bot_chatID, mensaje, reply_markup=markup, parse_mode='HTML')
    ### except: 
    ###   bot.send_message(bot_chatID, mensajetxt, reply_markup=markup, parse_mode='HTML')
    
    bot.send_message(bot_chatID, mensaje, reply_markup=markup, parse_mode='HTML')
    ### mensajetxt = "Hola"
    print("ESTOY ENVIANDO TELEGRAM: " + str(mensajetxt) + "")
    return {}
    ## return response.json()



class linnlu(models.Model):
  _name = "pyme.linnlu"
  _description = "Respuestas Personalizadas"
  _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
  _order = "create_date desc"

  name = fields.Char(string='Nombre', track_visibility='always', required=True)
  entradas = fields.Many2many('pyme.bot.entradasnlu', string='Intenciones')
  entidades = fields.Many2many('pyme.bot.entidadesnlu', string='Entidades')
  contestacion = fields.Text('Respuestas')
  nlu = fields.Many2one('pyme.telegrambot', string='Asociado a: ')
  tipochatbot = fields.Selection([('telegram', 'Telegram'),('odoobot', 'Charla en Vivo ODOO')], string="Servicio de Chat", related='nlu.tipochatbot') 
  preguntaslin = fields.One2many('pyme.bot.botonestelgram', 'preguntaslin', string='Botones')
  entorno = fields.Selection([('contacto', 'CONTACTO'),('user', 'USUARIO'), ('guest', 'INVITADO')], string='Entorno de Usuario', required=True, default='user')


  @api.depends('nlu')
  def _compute_token(self):
        for test in self:
            token_telegram = self.env['pyme.telegrambot'].search([('motor_nlu', '=', test.nlu.id )]).token_telegram
            test.token = str(token_telegram)


class linficheronlu(models.Model):
  _name = "pyme.ficheronlu"
  _description = "Respuestas Lógica Python"
  _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
  _order = "create_date desc"


  name = fields.Char(string='Nombre', track_visibility='always', required=True)
  contestacion = fields.Text('Archivo Python')
  nlu = fields.Many2one('pyme.telegrambot', string='Asociado a: ')
  preguntas = fields.One2many('pyme.bot.botonestelgram', 'preguntas', string='Botones')
  entorno = fields.Selection([('contacto', 'CONTACTO'),('user', 'USUARIO'), ('guest', 'INVITADO')], string='Entorno de Usuario', required=True, default='user')



class BotonesTelegram(models.Model):
  _name = "pyme.bot.botonestelgram"
  _description = "Botones Telegram"
  _order = "create_date desc"


  name = fields.Char(string='Texto')
  telegramm2o = fields.Many2one('pyme.telegram', string='Bot')
  preguntas = fields.Many2one('pyme.ficheronlu', string='Bot')
  preguntaslin = fields.Many2one('pyme.linnlu', string='Bot')
  nlu = fields.Many2one('pyme.telegrambot', string='Asociado a: ', related='preguntaslin.nlu')
  tipoi = fields.Selection([('start', 'Comando Inicio'), ('help', 'Comando Ayuda')], string='Acción Enlazada', required=True, default='start')
  tipo = fields.Selection([('url', 'Link URL'), ('datos', 'Datos')], string='Tipo Botón', required=True, default='url')
  datos = fields.Char(string='Contenido')
  datos2 = fields.Char(string='Contenido LINK OdooBot')
  entorno = fields.Selection([('contacto', 'CONTACTO'),('user', 'USUARIO'), ('guest', 'INVITADO')], string='Entorno de Usuario', related='preguntas.entorno')
  tipochatbot = fields.Selection([('telegram', 'Telegram'),('odoobot', 'Charla en Vivo ODOO')], string="Servicio de Chat", related='nlu.tipochatbot')  

  
  
class BotonesTelegramEntradasNlu(models.Model):
  _name = "pyme.bot.entradasnlu"
  _description = "Intenciones NLU"
  _order = "create_date desc"
  
  name = fields.Char(string='Texto / Comando')

class BotonesTelegramEntidadesNlu(models.Model):
  _name = "pyme.bot.entidadesnlu"
  _description = "Entidades NLU"
  _order = "create_date desc"
  
  name = fields.Char(string='Entidad')
  
  
  
class herenciasMailChannel(models.Model):
  
    _inherit = 'mail.channel'

    channel_type = fields.Selection(selection_add=[('telegram', 'Telegram')])
    
    
class EnviaTelegramPart(models.Model):
  _name = "send_telegram"
  _description = "Bots Telegram"
  ### _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
  _order = "create_date desc"
  
  name = fields.Many2one('res.partner', string='Contacto Destino')
  recipients = fields.Char(string='Destinatario')
  message = fields.Text(string='Mensaje')
 

  def action_send_telegram(self):
      buttonstelegram = []
      telegramid = self.recipients
      texto = self.message
      telegrambot_token = "1054416532:AAHjhZy3_VnTmJRuMw2aZSxzMZv9HKB8Qjo"
      parner_name = self.env['res.partner'].search([('id', '=',int(self.name.id))], limit=1).name
      self.env['mail.message'].create({'message_type':"comment",
                  'subtype_id': self.env.ref("mail.mt_comment").id, # subject type
                  'body': "Telegram Enviado: " + str(texto) + "",
                  'subject': "Telegram Enviado",
                  'model': 'res.partner',
                  'author_id': 7,
                 'record_name': parner_name,
                  'res_id': self.name.id})
      try: 
         self.pool.get('pyme.telegrambot').telegram_bot_sendtext(self, str(texto), str(telegramid), str(telegrambot_token),buttonstelegram)
      except:
         raise AccessError("Error al enviar el Telegram. Compruebe que el Usuario Exista y el Token sea correcto")

      message_id = self.env['mymodule.message.wizard'].create({'message': 'Mensaje Enviado'})
      return {
        'name': 'Mensaje',
        'type': 'ir.actions.act_window',
        'view_mode': 'form',
        'res_model': 'mymodule.message.wizard',
        'res_id': message_id.id,
        'target': 'new'}

