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
from datetime import datetime, timedelta

class Notificaciones(models.Model):
  _name = "pyme.notificaciones"
  _description = "Notificaciones Documentos"
  _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
  _order = "sequence, create_date desc"

  name = fields.Char(string='Nombre', track_visibility='always', required=True)
  tiponotificaicon = fields.Char(string='Tipo Notificación')
  modo = fields.Char(string='Causa Notificación', required=True)
  destino = fields.Char('Objeto Destino')
  description = fields.Text('Notas Internas')
  modelid = fields.Many2one('ir.model', string='Modelo Afcetado', track_visibility='onchange', index=True)
  user_ids = fields.Many2many('res.users', string='Usuarios Afectados', track_visibility='onchange', index=True, default=False)
  partner_ids = fields.Many2many('res.partner', string='Clientes Afectados', track_visibility='onchange', index=True, default=False)
  sequence = fields.Integer(string='Sequencia', default=10)
  aviso_utelegram = fields.Boolean(string='Telegram Usuario')
  aviso_uemail = fields.Boolean(string='Email Usuario')
  aviso_ubot = fields.Boolean(string='Bot Usuario')
  aviso_ptelegram = fields.Boolean(string='Telegram Partner')
  aviso_pemail = fields.Boolean(string='Email Partner')
  aviso_pbot = fields.Boolean(string='Bot Partner')
  plantilla_utelegram = fields.Char(string='Plantilla Telegram Usuario')
  plantilla_ptelegram = fields.Char(string='Plantilla Telegram Partner')
  mensaje_usuario = fields.Char(string='Mensaje Enviado al Usuario')
  mensaje_cliente = fields.Char(string='Mensaje Enviado al Partner / Seguidor')
  enviado = fields.Boolean(string='Enviada')
  enviado_cuando = fields.Datetime(string='Cuando')
  idconfnotif = fields.Many2one('pyme.notificaciones.configuracion', string='Relgla Utilizada')
  aquien = fields.One2many('pyme.notificaciones.aquien','name', string='Contactos Notificados')
  pendiente = fields.Boolean(string='Pendiente')
  quienfh = fields.Many2one('pyme.notificaciones.gc', string='Horario')


        
        
  @api.multi
  def enviabot(self):
       partid = 86
       maemodel = self.modelid.name
       resmodel = self.modelid.model
       if str(resmodel) == "fetchmail.server":
          actionl="169"
          modell="mail.message"
       if str(resmodel) == "helpdesk_lite.ticket":
          actionl="145"
          modell=resmodel
       if str(resmodel) == "project.task":
          actionl="227"
          modell=resmodel
       if str(resmodel) == "mail.channel":
          actionl="140"
          modell=resmodel

       mensaje_usuario = self.mensaje_usuario
       datetime = fields.Datetime.now()
       res_name = 'Aviso: ' + str(maemodel)
       body = "Aviso: " + str(maemodel) + " " + str(datetime) + "<br><br>Mensaje: <p> " + str(mensaje_usuario) + "</p>.<br> Puede consultarlo pinchando <a href=\"/web?#action=" + str(actionl) + "&model=" + str(modell) + "&view_type=list\">aquí</a>"
       message_id = self.id
       activity_obj = self.env['mail.message']
       mail_activity = activity_obj.create({
          'author_id': 1,
          'model': 'pyme.notificaciones',
          'subtype_id': 2,
          'res_id': message_id, 
          'subject': res_name,
          'body': body,
          'needaction_partner_ids': [(4, partid, 1)],
          'record_name': res_name,
          'message_type': 'notification'})
       ## self.message_post(subject=res_name, body=body, partner_ids=[(4, partid, 1)])



  @api.multi
  def enviamail(self,emailnotif,subject,causatxt,causa,servidorsaliente,modelo):
      mail_obj = self.env['mail.mail']
      mail_server_id = servidorsaliente
      email_from = self.env['ir.mail_server'].search([('id', '=', str(mail_server_id))], limit=1).smtp_user
      subject = "Notificación desde: " + str(modelo) + "."
      body_html = "<body><p>" + str(causa) + "</p><br><br><p> Enviado por ODOO - Main Informàtica Gandia, S.L.</body>"
      mail = mail_obj.create({'mail_server_id':servidorsaliente,'reply-to': email_from, 'email_from': email_from,'subject': subject,'body_html': body_html,'email_to': emailnotif,})
      mail.send()
      ### print("\n\n ********************************************   INCIDENCIA:  Enviando MAIL a: " + str(emailnotif))

  @api.multi
  def enviabotodoo(self,linecontactid,modelname,model,causatxt,notificacion_id):
       ### print("NOTIFICACION:  Enviando INTERNO a: " + str(linecontactid))
       partid = linecontactid
       maemodel = str(modelname)
       resmodel = str(model)
       if str(resmodel) == "fetchmail.server":
          actionl="169"
          modell="mail.message"
       if str(resmodel) == "helpdesk_lite.ticket":
          actionl="145"
          modell=resmodel
       if str(resmodel) == "project.task":
          actionl="227"
          modell=resmodel
       if str(resmodel) == "res.users":
          actionl="68"
          modell=resmodel
       if str(resmodel) == "mail.channel":
          actionl="140"
          modell=resmodel
       mensaje_usuario = causatxt
       datetime = fields.Datetime.now()
       res_name = 'Aviso: ' + str(maemodel)
       body = "Aviso: " + str(maemodel) + " " + str(datetime) + "<br><br>Mensaje: <p> " + str(mensaje_usuario) + "</p>.<br> Puede consultarlo pinchando <a href=\"/web?#action=" + str(actionl) + "&model=" + str(modell) + "&view_type=list\">aquí</a>"
       message_id = notificacion_id.id
       activity_obj = self.env['mail.message']
       if str(partid) != "False":
          mail_activity = activity_obj.create({'author_id': 2,'model': 'pyme.notificaciones','subtype_id': 2,'res_id': message_id,'subject': res_name,'body': body,'needaction_partner_ids': [(4, partid)],'record_name': res_name,'message_type': 'comment'})



  @api.multi
  def horario(self,idconfnotif,linecontactid):
       if linecontactid != False:
          is_between = True
          horariocontacto = self.env['res.partner'].search([('id', '=', int(linecontactid))], limit=1).horario.id
          print("\n\nSELF: " + str(self) + " Conf: " + str(idconfnotif) + " Partner: " + str(linecontactid) + " Horario: " + str(horariocontacto) + "")
          if horariocontacto != False:
             now = datetime.now()
             dateahora = datetime.now() + timedelta(hours=2)
             diasemana = datetime.today().strftime('%A')
             if str(diasemana) == "Monday": diasemana = "lunes" 
             if str(diasemana) == "Tuesday": diasemana = "martes" 
             if str(diasemana) == "Wednesday": diasemana = "miercoles" 
             if str(diasemana) == "Thursday": diasemana = "jueves" 
             if str(diasemana) == "Friday": diasemana = "viernes" 
             if str(diasemana) == "Saturday": diasemana = "sabado" 
             if str(diasemana) == "Sunday": diasemana = "domingo" 
             fechayhora = str(dateahora).split(' ')
             fecha = fechayhora[0]
             hora = fechayhora[1]
             horario_data_ids = self.env['pyme.notificaciones.gc'].search([('id', '=', int(horariocontacto))], limit=1)
             ### print("Dia Semana: " + str(diasemana) + "")
             ### print("Fecha -- Hora HOY: " + str(fecha) + " -- " + str(hora) + "")
             diaok = ""
             for horariodata in horario_data_ids:
                 lunes = horariodata.lunes
                 martes = horariodata.martes
                 miercoles = horariodata.miercoles
                 jueves = horariodata.jueves
                 viernes = horariodata.viernes
                 sabado = horariodata.sabado
                 domingo = horariodata.domingo
                 if str(lunes) == "True" and str(diasemana) == "lunes": diaok = "lunes"
                 if str(martes) == "True" and str(diasemana) == "martes": diaok = "martes"
                 if str(miercoles) == "True" and str(diasemana) == "miercoles": diaok = "miercoles"
                 if str(jueves) == "True" and str(diasemana) == "jueves":  diaok = "jueves"
                 if str(viernes) == "True" and str(diasemana) == "viernes":  diaok = "viernes"
                 if str(sabado) == "True" and str(diasemana) == "sabado":  diaok = "sabado"
                 if str(domingo) == "True" and str(diasemana) == "domingo":  diaok = "domingo"
                 if diaok != "":
                    hora = hora.split('.')
                    hora = hora[0]
                    self.env.cr.execute("SELECT " + str(diaok) + "hi," + str(diaok) + "mi  FROM pyme_notificaciones_gc WHERE id='" + str(horariocontacto) + "' LIMIT 1")
                    resultv = self.env.cr.fetchone()
                    horaini = resultv[0]
                    minini = resultv[1]
                    self.env.cr.execute("SELECT " + str(diaok) + "hf," + str(diaok) + "mf  FROM pyme_notificaciones_gc WHERE id='" + str(horariocontacto) + "' LIMIT 1")
                    resultv = self.env.cr.fetchone()
                    horafin = resultv[0]
                    minfin = resultv[1]
                    hstart = horaini + ":" + minini
                    hend = horafin + ":" + minfin
                    ## between = is_hour_between(hstart,hend,hora)
                    is_between = False
                    is_between |= hstart <= hora <= hend
                    is_between |= hend < hstart and (hstart <= hora or hora <= hend)
                    print("Validado: " + str(diaok) + ". Miramos si " + str(hora) + " esta dentro del horario: " + str(hstart) + " y " + str(hend) + ".")
          ### print("Enviamos: " + str(is_between) + "\n\n")
       return is_between




  @api.multi
  def colanotificaciones(self,idconfnotif,linecontactid):

        ## Montamos El Texto a enviar
        idnuevanotificacion = notificacion_id.id or False
        ## print("\n\n *-******* Nueva Notificación: " + str(idnuevanotificacion) + "")
        causa = str(plantillausuario)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        partner_name = self.env['res.partner'].search([('id', '=', int(partner_id))], limit=1).name
        if str(origen2) == "CONVERSACIONCHANNEL" and partner_id == False:
           partner_name = partner_nameconv
        user_name = self.env['res.users'].search([('id', '=', int(user_id))], limit=1).partner_id.name

        causa = causa.replace('$id',str(num))
        causa = causa.replace('$cliente',str(partner_name))
        causa = causa.replace('$usuario',str(user_name))
        causa = causa.replace('$fecha',str(dt_string))
        causa = causa.replace('$estado',str(estado))
        causa = causa.replace('$asignado',str(asignado))
        causa = causa.replace('$mensaje',str(mensaje))
        causa = causa.replace('$from',str(estado))
        causa = causa.replace('$asunto',str(asunto))

        ## h = html2text.HTML2Text()
        ## causatxt = h.handle(causa)

        causatxt = causa
        urltelegram = "192.168.50.242:5005"
        notificacionespendientes_ids = self.env['pyme.notificaciones'].search([('enviado', '!=', True),('pendiente', '!=', True)])
        for lines in notificacionespendientes_ids:
           notifid = lines.id
           notifenviado = lines.enviado
           notifname = lines.name



           ######
           ######  USUARIOS
           ######


           if str(conftipodestino) == "users" and str(user_id) != "False":
               ## Usuarios
               destinostr="USUARIOS"
               print("LA INCIDENCIA ENTRA EN NIVEL DE ENVIO USUARIO con ID:" + str(notifid) + ".")
               ## Miramos primero si estamos en la excepcion de grupos de HelpDesk
               notificauser = "True"
               if str(model) == "helpdesk_lite.ticket" and str(confbasenotif.notificaasignado) != "True": 
                   notificauser = "False"
               lineuser_id = self.env['res.users'].search([('id', '=', int(user_id) )])
               lineuserid = lineuser_id.id
               lineusername = lineuser_id.name
               lineuserenviatelegram = lineuser_id.notifica_telegram
               lineuserenviabot = lineuser_id.notifica_bot
               lineuserenviamail = lineuser_id.notifica_mail
               lineuseremail = lineuser_id.partner_id.email
               lineusertelegram = lineuser_id.partner_id.rasa_telegramid
               linecontactid = lineuser_id.partner_id.id
               linecontactname = lineuser_id.partner_id.name
               print("Comprobando Usuario: " + str(lineusername) + ". Email: " + str(lineuseremail) + " Notifica Email: " + str(lineuserenviamail) + " ID TELEGRAM: " + str(lineusertelegram) + ".")
               horario_partner_id = lineuser_id.partner_id.id
               idconfnotif = confbasenotif.id
               enviamoshorario = self.pool.get('pyme.notificaciones').horario(self,idconfnotif,linecontactid)
               print("\n\n ------------------------------------         ENVIAMOS: " + str(enviamoshorario) + "\n\n")
               if enviamoshorario == False:
                  lines.write({'destino': destinostr,'pendiente': True,'idconfnotif': confnotif,})
                  notificauser = False

               ## Enviamos EMAIL
               if str(lineuseremail) != "" and str(lineuserenviamail) == "email" and origen2 != "WEBMAIL" and str(enviamail) == "True" and str(notificauser) == "True":
                     aquien_obj = self.env['pyme.notificaciones.aquien']
                     aquiennot = aquien_obj.create({'name': idnuevanotificacion,'metodo': 'email','contacto': linecontactid,'como': 'Email a: ' + str(lineuseremail),})
                     subject = "ODOO: " + str(causatxt) + "."
                     body_html = "<body><p>" + str(causa) + "</p><br><br><p> Enviado por ODOO - Main Informàtica Gandia, S.L.</body>"
                     servidorsaliente = servidorsaliente
                     modelo = str(modelname)
                     self.pool.get('pyme.notificaciones').enviamail(self,lineuseremail,subject,causatxt,causa,servidorsaliente,modelo)
                     emailnotif=lineuseremail
               ## Enviamos TELEGRAM
               if  origenmail == True and str(lineusertelegram) != "" and str(enviabot) == "True" and str(notificauser) == "True":
                     print("INCIDENCIA:  Enviando BOT TELEGRAM a: " + str(lineusertelegram) + " Como Usuario Asignado")
                     chat_id = lineusertelegram
                     if str(chat_id) != "False":
                       aquien_obj = self.env['pyme.notificaciones.aquien']
                       aquiennot = aquien_obj.create({'name': idnuevanotificacion,'metodo': 'telegram','contacto': linecontactid,'como': 'Telegram a : ' + str(lineusername),})
                       causatxt = str(causatxt).replace('#',"")
                       ## buttonstelegram = CABECERA
                       self.pool.get('pyme.telegrambot').telegram_bot_sendtext(self, str(causatxt), str(chat_id), str(telegrambot_token),buttonstelegram)
               ## Enviamos NOTIFICACION
               if  origenmail == True and str(envianotifinterna) == "True" and str(notificauser) == "True":
                   partid = linecontactid
                   maemodel = str(modelname)
                   resmodel = str(model)
                   self.pool.get('pyme.notificaciones').enviabotodoo(self,partid,maemodel,resmodel,causatxt,notificacion_id)

           ## Procesamos las Excepciones de los Tickets por Grupos
           if str(model) == "helpdesk_lite.ticket" and str(conftipodestino) == "users": 
               print("LA INCIDENCIA ENTRA EN NIVEL DE ENVIO ADMIN GRUPO con ID:" + str(notifid) + ".")
               notificaadmin = confbasenotif.notificaadmin
               notificagroup = confbasenotif.notificagroup
               notificaasignado = confbasenotif.notificaasignado
               grupo = self.env['helpdesk_lite.ticket'].search([('id', '=', int(num))], limit=1).team_id.id
               admingroupid = self.env['helpdesk_lite.team'].search([('id', '=', int(grupo))], limit=1).user_id
               members_ids = self.env['helpdesk_lite.team'].search([('id', '=', int(grupo))], limit=1).member_ids
               adminuserid = admingroupid.id
               adminpartnerid = admingroupid.partner_id.id
               adminpartnermail = admingroupid.partner_id.email
               adminpartnerenviamail = admingroupid.partner_id.notifica_mail
               adminpartnerenviatelegram = admingroupid.partner_id.notifica_telegram
               adminpartnerenviabot = admingroupid.partner_id.notifica_bot
               adminpartnertelegram = admingroupid.partner_id.rasa_telegramid
               adminpartnername = admingroupid.partner_id.name
               ### faltadmin = "no"
               ### notificadoadmin = self.env['pyme.notificaciones.aquien'].search([('contacto','=',int(adminpartnerid)),('name', '=', int(idnuevanotificacion))], limit=1).id
               ### if str(notificadoadmin) == "False":
               faltadmin="si"
               print("Excepcion Notificaciones: Admin: " + str(notificaadmin) + ". Grupo: " + str(notificagroup) + ". Asignado: " + str(notificaasignado) + "")
               ## Enviamos Pendientes ADMIN
               if str(faltadmin) == "si" and str(notificaadmin) == "True":
                   print("Envio Admin Grupo: " + str(adminpartnername) + " y Notificación: " + str(idnuevanotificacion) + " Destino: " + str(adminpartnermail) + ".")
                   aquien_obj = self.env['pyme.notificaciones.aquien']
                   aquiennot = aquien_obj.create({'name': int(idnuevanotificacion),'metodo': 'notificacion','contacto': adminpartnerid,'como': 'Mensaje a : ' + str(adminpartnername)})
                   ## Enviamos EMAIL
                   if str(adminpartnermail) != "" and str(enviamail) == "True" and str(adminpartnerenviamail) == "email":
                         subject = "ODOO: " + str(causatxt) + "."
                         servidorsaliente = servidorsaliente
                         modelo = str(modelname)
                         self.pool.get('pyme.notificaciones').enviamail(self,adminpartnermail,subject,causatxt,causa,servidorsaliente,modelo)
                   ## Enviamos TELEGRAM
                   if  str(adminpartnertelegram) != "" and str(enviabot) == "True" and str(adminpartnerenviatelegram) == "telegram":
                         print("NOTIFICACION:  Enviando BOT TELEGRAM a: " + str(adminpartnertelegram) + " Como admin de grupo: " + str(adminpartnertelegram) + ".")
                         chat_id = adminpartnertelegram
                         if str(chat_id) != "False":
                           causatxt = str(causatxt).replace('#',"")
                           ## buttonstelegram = CABECERA
                           self.pool.get('pyme.telegrambot').telegram_bot_sendtext(self, str(causatxt), str(chat_id), str(telegrambot_token),buttonstelegram)
                   ## Enviamos NOTIFICACION
                   if  str(envianotifinterna) == "True" and str(adminpartnerenviabot) == "bot":
                       print("NOTIFICACION:  Enviando INTERNO a: " + str(envianotifinterna) + " Como admin de grupo: " + str(adminpartnertelegram) + ".")
                       partid = linecontactid
                       maemodel = str(modelname)
                       resmodel = str(model)
                       self.pool.get('pyme.notificaciones').enviabotodoo(self,partid,maemodel,resmodel,causatxt,notificacion_id)

               ## Enviamos GRUPOS HELPDESK
               if str(notificagroup) == "True":
                 print("LA INCIDENCIA ENTRA EN NIVEL DE ENVIO MIEMBROS GRUPO con ID:" + str(notifid) + ".")
                 for members in members_ids:
                   faltagroup="no"
                   miembroname = members.partner_id.name
                   miembroemail = members.partner_id.email
                   miebroidtelegram = members.partner_id.rasa_telegramid
                   miembroenviamail = members.partner_id.notifica_mail
                   miembroid = members.id
                   miembropartnerid = members.partner_id.id
                   notificadoadmin2 = self.env['pyme.notificaciones.aquien'].search([('contacto','=',int(miembropartnerid)),('name', '=', int(idnuevanotificacion))], limit=1).id
                   if str(notificadoadmin2) == "False":
                       faltagroup="si"
                   if str(faltagroup) == "si" and str(notificagroup) == "True":
                       print("Miembro: " + str(miembroname))
                       aquien_obj = self.env['pyme.notificaciones.aquien']
                       aquiennot = aquien_obj.create({'name': int(idnuevanotificacion),'metodo': 'notificacion','contacto': miembropartnerid,'como': 'Mensaje a : ' + str(miembroname)})
                       ## Enviamos EMAIL
                       if str(miembroemail) != "" and str(miembroenviamail) == "email" and origen2 != "WEBMAIL" and str(enviamail) == "True":
                             subject = "ODOO: " + str(causatxt) + "."
                             servidorsaliente = servidorsaliente
                             modelo = str(modelname)
                             self.pool.get('pyme.notificaciones').enviamail(self,miembroemail,subject,causatxt,causa,servidorsaliente,modelo)
                       ## Enviamos TELEGRAM
                       if  str(miebroidtelegram) != "" and str(telegrambot_modo) == "telegram" and str(enviabot) == "True":
                             print("INCIDENCIA:  Enviando BOT TELEGRAM a: " + str(miebroidtelegram))
                             chat_id = miebroidtelegram
                             if str(chat_id) != "False":
                               causatxt = str(causatxt).replace('#',"")
                               ## buttonstelegram = CABECERA
                               self.pool.get('pyme.telegrambot').telegram_bot_sendtext(self, str(causatxt), str(chat_id), str(telegrambot_token),buttonstelegram)
                       ## Enviamos NOTIFICACION
                       if  str(envianotifinterna) == "True":
                           partid = linecontactid
                           maemodel = str(modelname)
                           resmodel = str(model)
                           self.pool.get('pyme.notificaciones').enviabotodoo(self,partid,maemodel,resmodel,causatxt,notificacion_id)



           if str(conftipodestino) == "users" and origen2 == "CONVERSACIONCHANNEL":
               destinostr="USUARIOS"
               print("LA INCIDENCIA ENTRA EN NIVEL DE ENVIO MIEMBROS DEL CHATTER con ID:" + str(notifid) + ".")
               for lineuser_id in lines.partner_ids:
                   lineuserid = lineuser_id.id
                   lineusername = lineuser_id.name
                   lineuserenviatelegram = lineuser_id.notifica_telegram
                   lineuserenviabot = lineuser_id.notifica_bot
                   lineuserenviamail = lineuser_id.notifica_mail
                   lineuseremail = lineuser_id.email
                   lineusertelegram = lineuser_id.rasa_telegramid
                   print("Comprobando Usuario: " + str(lineusername) + ". Email: " + str(lineuseremail) + " Notifica Email: " + str(lineuserenviamail) + ".")
                   ## Enviamos EMAIL
                   if str(lineuseremail) != "" and str(lineuserenviamail) == "email" and str(enviamail) == "True":
                         aquien_obj = self.env['pyme.notificaciones.aquien']
                         aquiennot = aquien_obj.create({'name': idnuevanotificacion,'metodo': 'email','contacto': lineuserid,'como': 'Email a: ' + str(lineuseremail),})
                         subject = "ODOO: " + str(causatxt) + "."
                         servidorsaliente = servidorsaliente
                         modelo = str(modelname)
                         self.pool.get('pyme.notificaciones').enviamail(self,lineuseremail,subject,causatxt,causa,servidorsaliente,modelo)
                   ## Enviamos TELEGRAM
                   if  str(lineusertelegram) != "" and str(telegrambot_modo) == "telegram" and str(enviabot) == "True":
                         aquien_obj = self.env['pyme.notificaciones.aquien']
                         aquiennot = aquien_obj.create({'name': idnuevanotificacion,'metodo': 'telegram','contacto': lineuserid,'como': 'Telegram a : ' + str(lineusername),})
                         chat_id = lineusertelegram
                         if str(chat_id) != "False":
                           causatxt = str(causatxt).replace('#',"")
                           ## buttonstelegram = CABECERA
                           self.pool.get('pyme.telegrambot').telegram_bot_sendtext(self, str(causatxt), str(chat_id), str(telegrambot_token),buttonstelegram)



           ######
           ######  CONTACTOS
           ######

           if str(conftipodestino) == "partner" and origen2 == "CHATTER" and str(destinostr) != "USUARIOS":
               notificacontact = True
               ## PARTNERS
               destinostr="CONTACTOS"
               print("LA INCIDENCIA ENTRA EN NIVEL DE ENVIO MIEMBROS DEL CHATTER con ID:" + str(notifid) + ".")
               for lineuser_id in lines.partner_ids:
                   lineuserid = lineuser_id.id
                   lineusername = lineuser_id.name
                   lineuserenviatelegram = lineuser_id.notifica_telegram
                   lineuserenviabot = lineuser_id.notifica_bot
                   lineuserenviamail = lineuser_id.notifica_mail
                   lineuseremail = lineuser_id.email
                   lineusertelegram = lineuser_id.rasa_telegramid
                   print("Comprobando Usuario: " + str(lineusername) + ". Email: " + str(lineuseremail) + " Notifica Email: " + str(lineuserenviamail) + ".")
                   ## Enviamos EMAIL
                   if str(lineuseremail) != "" and str(lineuserenviamail) == "email" and str(enviamail) == "True":
                         aquien_obj = self.env['pyme.notificaciones.aquien']
                         aquiennot = aquien_obj.create({'name': idnuevanotificacion,'metodo': 'email','contacto': lineuserid,'como': 'Email a: ' + str(lineuseremail),})
                         subject = "ODOO: " + str(causatxt) + "."
                         servidorsaliente = servidorsaliente
                         modelo = str(modelname)
                         self.pool.get('pyme.notificaciones').enviamail(self,lineuseremail,subject,causatxt,causa,servidorsaliente,modelo)
                   ## Enviamos TELEGRAM
                   if  str(lineusertelegram) != "" and str(telegrambot_modo) == "telegram" and str(enviabot) == "True":
                         aquien_obj = self.env['pyme.notificaciones.aquien']
                         aquiennot = aquien_obj.create({'name': idnuevanotificacion,'metodo': 'telegram','contacto': lineuserid,'como': 'Telegram a : ' + str(lineusername),})
                         chat_id = lineusertelegram
                         if str(chat_id) != "False":
                           causatxt = str(causatxt).replace('#',"")
                           ## buttonstelegram = CABECERA
                           self.pool.get('pyme.telegrambot').telegram_bot_sendtext(self, str(causatxt), str(chat_id), str(telegrambot_token),buttonstelegram)




           if str(conftipodestino) == "partner" and origen2 != "CHATTER":
               ## PARTNERS
               notificacontact = True
               destinostr="CONTACTOS"
               print("LA INCIDENCIA ENTRA EN NIVEL DE ENVIO CONTACTOS con ID:" + str(notifid) + ". TIPO: " + str(destinostr))
               lineuser_id = self.env['res.partner'].search([('id', '=', int(partner_id) )])
               lineuserid = lineuser_id.id
               lineusername = lineuser_id.name
               lineuserenviatelegram = lineuser_id.notifica_telegram
               lineuserenviabot = lineuser_id.notifica_bot
               lineuserenviamail = lineuser_id.notifica_mail
               lineuseremail = lineuser_id.email
               lineusertelegram = lineuser_id.rasa_telegramid
               print("Comprobando Usuario: " + str(lineusername) + ". Email: " + str(lineuseremail) + " Notifica Email: " + str(lineuserenviamail) + ".")
               ## Enviamos EMAIL
               if str(lineuseremail) != "" and str(lineuserenviamail) == "email" and str(enviamail) == "True":
                     aquien_obj = self.env['pyme.notificaciones.aquien']
                     aquiennot = aquien_obj.create({'name': idnuevanotificacion,'metodo': 'email','contacto': lineuserid,'como': 'Email a: ' + str(lineuseremail),})
                     subject = "ODOO: " + str(causatxt) + "."
                     servidorsaliente = servidorsaliente
                     modelo = str(modelname)
                     self.pool.get('pyme.notificaciones').enviamail(self,lineuseremail,subject,causatxt,causa,servidorsaliente,modelo)
               ## Enviamos TELEGRAM
               if  str(lineusertelegram) != "" and str(telegrambot_modo) == "telegram" and str(enviabot) == "True":
                     aquien_obj = self.env['pyme.notificaciones.aquien']
                     aquiennot = aquien_obj.create({'name': idnuevanotificacion,'metodo': 'telegram','contacto': lineuserid,'como': 'Telegram a : ' + str(lineusername),})
                     chat_id = lineusertelegram
                     if str(chat_id) != "False":
                       causatxt = str(causatxt).replace('#',"")
                       ## buttonstelegram = CABECERA
                       print ("\n\n########################################################################\n\n")
                       self.pool.get('pyme.telegrambot').telegram_bot_sendtext(self, str(causatxt), str(chat_id), str(telegrambot_token),buttonstelegram)



           if notificauser == True:
              lines.write({'destino': destinostr,'enviado': True,'enviado_cuando': fields.Datetime.now(),'idconfnotif': confnotif,})
           if notificacontact == True:
              lines.write({'destino': destinostr,'enviado': True,'enviado_cuando': fields.Datetime.now(),'idconfnotif': confnotif,})

        return {}








  def envianotificaciones(self, model,num,mensajeusuario,mensajecliente, partner_id, user_id, causa, origen2,modo,asignado,estado,asunto):

    confnotif = False
    notificacontact = False
    notificauser = False
    telegrambot_modo = False
    telegrambot_rasa = False
    telegrambot_token = False    
    mensaje = False
    linecontactid = False
    linecontactname = False
    origenmail = True
    destinostr = ""
    datetime = fields.Datetime.now()
    ## Buscamos si Tenemos Configurada la Notificacion
    modelbid = self.env['ir.model'].search([('model', '=', str(model))], limit=1).id
    modelname = self.env['ir.model'].search([('model', '=', str(model))], limit=1).name
    cuando_id = self.env['pyme.notificaciones.cuando'].search([('conf', '=', str(modo))]).id
    confbasenotif_ids = self.env['pyme.notificaciones.configuracion'].search([('name', '=', int(modelbid)),('cuandonotifico','=',int(cuando_id))])
    enviamoshorario = True

    view = {}
    ## print("La Notificacion es: " + str(modelbid) + " en modo " + str(modo) + " >> " + str(cuando_id) + "")
    for confbasenotif in confbasenotif_ids:
      if str(confbasenotif.name.id) != "False":
        telegrambot_modo = "telegram"
        telegrambot_token = confbasenotif.botutilizado.token_telegram
        confnotif = confbasenotif.id
        conftipodestino = confbasenotif.tipodestino
        enviabot = confbasenotif.enviabot
        enviamail = confbasenotif.enviamail
        servidorsaliente = confbasenotif.mailutilizado.id
        envianotifinterna = confbasenotif.envianotifinterna
        plantillausuario = confbasenotif.plantillausuario
        plantillacliente = plantillausuario
        ### print("Destino: " + str(conftipodestino) + ". Enviabot: " + str(enviabot) + ". Enviamail: " + str(enviamail) + ". Telegram Modo: " + str(telegrambot_modo) + "\n")
        excepcion = "\n"
        envia_telegramu = self.env['res.users'].search([('id', '=', int(user_id))], limit=1).envia_telegram
        envia_botu = self.env['res.users'].search([('id', '=', int(user_id))], limit=1).envia_bot
        envia_mailu = self.env['res.users'].search([('id', '=', int(user_id))], limit=1).envia_mail
        envia_telegramc = self.env['res.users'].search([('partner_id', '=', int(partner_id))], limit=1).envia_telegram
        envia_botc = self.env['res.users'].search([('partner_id', '=', int(partner_id))], limit=1).envia_bot
        envia_mailc = self.env['res.users'].search([('partner_id', '=', int(partner_id))], limit=1).envia_mail


        buttonstelegram = []
        docboton = str(model)
        for botones in confbasenotif.botonestelgram:
           buttonstelegram += (str(botones.name),str(botones.tipo),str(botones.datos),docboton,num),
           ### buttonstelegram += ('TEXTO2','URL','https://connectate.com'),


        if str(model) == "helpdesk_lite.ticket":
           origen = self.env['helpdesk_lite.ticket'].search([('id', '=', int(num))], limit=1).origen
           if str(origen) == "telegram": 
               excepcion += "Se enviará de todas formas por " + str(origen) + " al cliente porque el " + str(model) + ":" + str(num) + " está generado por esa via."
        model_id = self.env['ir.model'].search([('model', '=', str(model))], limit=1).id
        notificaciones_obj = self.env['pyme.notificaciones']
        notificacion_id = False


        if origen2 == "CONVERSACIONCHANNEL":

          strmodelid = str(mensajeusuario).split('|')
          mailchanid = strmodelid[0]
          mailchantype = strmodelid[1]
          partnerid2 = []
          userids2 = []
          user_id = False
          if str(mailchantype) == "livechat":
             livechat_channel_ids = self.env['mail.channel'].search([('id', '=', int(mailchanid))]).livechat_channel_id
             for livechat_channel_id in livechat_channel_ids:
                for imusers_id in livechat_channel_id.users_ids:
                    userid = imusers_id.id
                    partnerid = imusers_id.partner_id.id
                    partnerid2 += (4,imusers_id.partner_id.id),
                    userids2 += (4,imusers_id.id),
          if str(mailchantype) == "telegram":
             idtelegram = 6
             usuariosnotificados_ids = self.env['pyme.telegram'].search([('id', '=', int(idtelegram))]).usuariosnotificados
             for usuariosnotificados in usuariosnotificados_ids:
                    userid = usuariosnotificados.id
                    partnerid = usuariosnotificados.partner_id.id
                    partnerid2 += (4,usuariosnotificados.partner_id.id),
                    userids2 += (4,usuariosnotificados.id),

          notificoano = confbasenotif.convorigendes
          mensaje = asunto
          ### print("\n\n\n ASUNTO ES: " + str(asunto) + "")
          if str(partner_id) == "False" and notificoano == False:
             print("NO NOTIFICO CONVERSACION DESCONOCIDA")
             return {}
          if str(partner_id) == "False":
             partner_nameconv = "Anónimo"
          notificacion_id = notificaciones_obj.create({
            'name': "Conversaciones " + str(model) + ". Causa: " + str(causa),
            'modo': modo,
            'aviso_utelegram': True,
            'tiponotificaicon': "CONVERSACION",
            'aviso_ptelegram': True,
            'aviso_ubot': True,
            'user_ids':  userids2,
            'partner_ids':  partnerid2,
            'mensaje_usuario': causa,
            'mensaje_cliente': causa,
            'aviso_pbot': True,
            'aviso_uemail': False,
            'aviso_pemail': False,
            'modelid': model_id,})
          



        if origen2 == "CONVERSACION":
          strmodelid = str(mensajeusuario).split('|')
          modelmc = strmodelid[0]
          modelmcid = strmodelid[1]
          im_livechat_ids = self.env[str(modelmc)].search([('id', '=', int(modelmcid))], limit=1).livechat_channel_id
          partnerid2 = []
          if str(im_livechat_ids) != False:
            ### print ("El MODELO es: " + str(im_livechat_ids) + "")
            for im_livechat in im_livechat_ids:
              for usuario in im_livechat.users_ids:
                partneridl = usuario.id
                partnerid2 += (4, partneridl),
          notificacion_id = notificaciones_obj.create({
            'name': "Conversaciones " + str(model) + ". Causa: " + str(causa),
            'modo': modo,
            'aviso_utelegram': True,
            'tiponotificaicon': "CONVERSACION",
            'aviso_ptelegram': True,
            'aviso_ubot': True,
            'user_ids':  partnerid2,
            'mensaje_usuario': causa,
            'mensaje_cliente': causa,
            'aviso_pbot': True,
            'aviso_uemail': False,
            'aviso_pemail': False,
            'modelid': model_id,})
            
        if origen2 == "WEBMAIL":
          followers_ids = self.env['fetchmail.server'].search([('id', '=', int(num))])
          ## origenmail = False
          notificamosdesconocidos = confbasenotif.emailorigendes
          if notificamosdesconocidos == False and partner_id == False:
             origenmail = False
          print("\n\n La opcion de No recibir Desconocido es: " + str(notificamosdesconocidos) + " y El Origen del MAIL es: " + str(origenmail) + ".\n\n")
          partnerid2 = []
          for linef in followers_ids:
            for lineu in linef.usuarios_ids:
              partneridl = lineu.id
              partnerid2 += (4, partneridl),
          notificacion_id = notificaciones_obj.create({
            'name': "Nueva Correo desde " + str(model) + " : " + str(num) + ". Causa: " + str(causa),
            'modo': modo,
            'aviso_utelegram': True,
            'tiponotificaicon': "WEBMAIL",
            'aviso_ptelegram': True,
            'aviso_ubot': True,
            'user_ids':  partnerid2,
            'mensaje_usuario': causa,
            'mensaje_cliente': causa,
            'aviso_pbot': True,
            'aviso_uemail': False,
            'aviso_pemail': False,
            'modelid': model_id,})

        if origen2 == "MODELO":
          if str(user_id) == "False" or str(user_id) == "false":
            notificacion_id = notificaciones_obj.create({
              'name': "Nueva notificación desde " + str(model) + " : " + str(num) + ". Causa: " + str(causa),
              'aviso_utelegram': True,
              'modo': modo,
              'tiponotificaicon': "MODELO",
              'aviso_ptelegram': True,
              'aviso_ubot': True,
              'mensaje_usuario': causa,
              'mensaje_cliente': causa,
              'partner_ids':  [(4, partner_id)],
              'aviso_pbot': True,
              'aviso_uemail': True,
              'aviso_pemail': True,
              'modelid': model_id,})
          else:
            notificacion_id = notificaciones_obj.create({
              'name': "Nueva notificación desde " + str(model) + " : " + str(num) + ". Causa: " + str(causa),
              'aviso_utelegram': True,
              'modo': modo,
              'tiponotificaicon': "MODELO",
              'aviso_ptelegram': True,
              'aviso_ubot': True,
              'mensaje_usuario': causa,
              'mensaje_cliente': causa,
              'partner_ids':  [(4, partner_id)],
              'user_ids':  [(4, user_id)],
              'aviso_pbot': True,
              'aviso_uemail': True,
              'aviso_pemail': True,
              'modelid': model_id,})


        if origen2 == "NUEVO":
          if str(model) == "helpdesk_lite.ticket": 
             gruposoportenuevo_ids = self.env['helpdesk_lite.team'].search([('nuevo', '=', True)])
             userids2 = []
             for linef in gruposoportenuevo_ids:
                if str(confbasenotif.notificaadmin) == "True":
                    userids2 += (4, linef.user_id.id),
                for lineu in linef.member_ids:
                   if str(confbasenotif.notificagroup) == "True":
                      partneridl = lineu.id
                      userids2 += (4, partneridl),
          else:
             userids2 = [(4, user_id)]
          ## if str(model) == "res.users":
          ##   userids2 = []
          notificacion_id = notificaciones_obj.create({
            'name': "Nueva notificación desde " + str(model) + " : " + str(num) + ". Causa: " + str(causa),
            'aviso_utelegram': True,
            'modo': modo,
            'tiponotificaicon': "NUEVO",
            'aviso_ptelegram': True,
            'aviso_ubot': True,
            'mensaje_usuario': causa,
            'mensaje_cliente': causa,
            'user_ids':  userids2,
            'partner_ids':  [(4, partner_id)],
            'aviso_pbot': True,
            'aviso_uemail': True,
            'aviso_pemail': True,
            'modelid': model_id,})

        if origen2 == "CHATTER":
          followers_ids = self.env['mail.followers'].search([('res_model', '=', str(model)),('res_id','=',num)])
          mensaje = causa
          partnerid2 = []
          for linef in followers_ids:
              partneridl = self.env['mail.followers'].search([('id', '=', int(linef))]).partner_id.id
              partnerid2 += (4, partneridl),
          notificacion_id = notificaciones_obj.create({
            'name': "Nueva notificación desde " + str(model) + " : " + str(num) + ". Causa: " + str(causa),
            'modo': modo,
            'aviso_utelegram': True,
            'tiponotificaicon': "CHATTER",
            'aviso_ptelegram': True,
            'aviso_ubot': True,
            'mensaje_usuario': causa,
            'mensaje_cliente': causa,
            'partner_ids':  partnerid2,
            'aviso_pbot': True,
            'aviso_uemail': True,
            'aviso_pemail': True,
            'modelid': model_id,})
        view = None
        if str(notificacion_id) != "False":
          view = {
            'name': _('GEstión Notificaicones'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pyme.notificaciones',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': notificacion_id.id }

    return view












class NotificacionesTipo(models.Model):
    _name = "pyme.notificaciones.tipo"
    _description = "Tipos de Notificación"
    
    name = fields.Char(string='Tipo de Notificación')
    conf = fields.Text(string='Descripción')

    _sql_constraints = [('name_unique', 'unique(name)', 'Ya existe una Regla del mismo tipo no se puede Duplicar')]
    
class NotificacionesCuando(models.Model):
    _name = "pyme.notificaciones.cuando"
    _description = "Tipos de Notificación"
    
    name = fields.Char(string='Cuando Notifica')
    conf = fields.Selection([('chatter', 'Mensaje'),('write', 'Al Escribir'),('create', 'Al Crear'),('unlink', 'Al Borrar')], string="Cuando Notifico")

    _sql_constraints = [('conf_unique', 'unique(conf)', 'Ya existe una Regla del mismo tipo no se puede Duplicar')]
    

class NotificacionesConf(models.Model):
    _name = "pyme.notificaciones.configuracion"
    _description = "Configuración de Notificaciones"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "create_date desc"

    
    name = fields.Many2one('ir.model', string='Modelo Afcetado', domain=[('modelonotificado','=', True)], track_visibility='onchange', index=True)
    namemodel = fields.Char(string='Nombre Modelo', related='name.model')
    sequence = fields.Integer(string='Sequence', default=10)
    cuandonotifico = fields.Many2one('pyme.notificaciones.cuando', string="Cuando Notifico")
    tipodestino = fields.Selection([('partner', 'Contactos'),('users', 'Usuarios')], string="Tipo Destino")
    enviabot = fields.Boolean(string='Envía Telegram')
    enviamail = fields.Boolean(string='Envía Email')
    envianotifinterna = fields.Boolean(string='Notificación Interna')
    botutilizado = fields.Many2one('pyme.telegram', string="Bot Utilizado")
    mailutilizado = fields.Many2one('ir.mail_server', string="Servidor Mail Saliente")
    ## notiusuarios = fields.Many2many('pyme.notificaciones.tipo', string="Tipo Notifico Usuario")
    ##noticlientes = fields.Many2many('pyme.notificaciones.tipo', string="Tipo Notifico Cliente")
    alertasnotif = fields.One2many('pyme.notificaciones','idconfnotif', string="Alertas Utilizadas")
    plantillausuario = fields.Text(string="Plantilla Notificación")
    notificaadmin = fields.Boolean(default=True, string="Notificar al responsable")
    notificagroup = fields.Boolean(default=True, string="Notificar al Grupo.")
    notificaasignado = fields.Boolean(default=True, string="Notificar al Asignado.")
    emailorigendes = fields.Boolean(default=False, string="Notifica Origen Desconocido")
    convorigendes = fields.Boolean(default=False, string="Notifica Origen Desconocido")
    botonestelgram = fields.One2many('pyme.notificaciones.botonestelgram','notifm2o', string="Botones")
    establecehorario = fields.Boolean(string="Establece Horario")
    horario = fields.Many2many('pyme.notificaciones.gc', string="Horario Notificación")
    mensajefh = fields.Text(string="Mensaje Emisor Fuera Horario")






    @api.model
    def create(self, vals):
        model_name = False
        model = vals['name']
        cuandonotifico = vals['cuandonotifico']
        tipodestino = vals['tipodestino']
        if str(model) == "False":
           raise AccessError("No Has seleccionado un Modelo a Notificar")
        if str(cuandonotifico) == "False":
           raise AccessError("Debes escoger Cuando vas a Notificar")
        if str(model) != "False":
           model_name = self.env['ir.model'].search([('id', '=', model )]).model
           model_str = self.env['ir.model'].search([('id', '=', model )]).name
        print("\nModelo: " + str(model_name) + " y Modo: >" + str(cuandonotifico) + "< y tipo de Destino: " + str(tipodestino) + "\n")
        if str(model_name) == "mail.channel" and str(tipodestino) != "users":
           if int(cuandonotifico) != 3:
              raise AccessError("La Notificación de Canal de Conversaciones debe seleccionarse como Tipo de Destino Usuarios y Cuando Notifico Create")

        if str(model_name) == "fetchmail.server" and str(tipodestino) != "users":
           if int(cuandonotifico) != 3:
              raise AccessError("La Notificación sobre Correos Electrónicos Entrantes solo puede hacerse por el Método de CREATE y Usuarios")
        if str(model_name) == "helpdesk_lite.ticket" and str(tipodestino) == "users":
           notificaadmin = vals['notificaadmin']
           notificagroup = vals['notificagroup']
           notificaasignado = vals['notificaasignado']
           if notificaadmin != True and notificagroup != True and notificaasignado != True:
              raise UserError("Para crear una Notificación de Usuario en " + str(model_str) + " debes escoger alguno de los valores de Notificación a responsable, grupo o asignado.")
        return super(NotificacionesConf, self.with_context(mail_create_nosubscribe=True)).create(vals)



    @api.multi
    def write(self, vals):
        # Do not allow changing the company_id when account_move_line already exist
        model_name = self.env['ir.model'].search([('id', '=', self.name.id )]).model
        model_str = self.env['ir.model'].search([('id', '=', self.name.id )]).name
        
        try:
           tipodestino = vals['tipodestino'] 
        except: 
           tipodestino = self.tipodestino
        try:
           cuandonotifico = vals['cuandonotifico'] 
        except: 
           cuandonotifico = self.cuandonotifico.id
        try:
           notificaadmin = vals['notificaadmin'] 
        except: 
           notificaadmin = self.notificaadmin
        try:
           notificagroup = vals['notificagroup']
        except:
           notificagroup = self.notificagroup
        try:
           notificaasignado = vals['notificaasignado']
        except:
           notificaasignado= self.notificaasignado
        if str(model_name) == "fetchmail.server" and str(tipodestino) == "partner":
           raise AccessError("Para crear una Notificación de Correo Electrónico debes escoger Tipo de Destino USUARIOS")


        print("\n\n Cuando Notifico: " + str(cuandonotifico) + "\n\n")
        if str(model_name) == "mail.channel" and str(tipodestino) == "partner":
           raise AccessError("La Notificación de Canal de Conversaciones debe seleccionarse como Tipo de Destino Usuarios y Cuando Notifico Create")
        if str(model_name) == "mail.channel" and str(cuandonotifico) != "3":
           raise AccessError("La Notificación de Canal de Conversaciones debe seleccionarse como Tipo de Destino Usuarios y Cuando Notifico Create")



        if str(model_name) == "helpdesk_lite.ticket" and str(tipodestino) == "users" and notificaadmin != True and notificagroup != True and notificaasignado != True:
           raise AccessError("Para crear una Notificación de Usuario en " + str(model_str) + " debes escoger alguno de los valores de Notificación a responsable, grupo o asignado.")

        return super(NotificacionesConf, self).write(vals)



    @api.onchange('cuandonotifico','tipodestino')
    def _onchange_cuandonotifico(self):
       conf = self.cuandonotifico.conf
       tipodestino = self.tipodestino
       ## print("\n >> " + str(conf) + " - " + str(tipodestino) + "\n")
       if str(conf) != "False":
         if str(conf) == "chatter":
            if str(tipodestino) == "users":
               raise AccessError("Las Notificaciones de CHATTER/Mensajes Solo puede ir asignada a Tipo de Destino: Contactos")



class NotificacionesAQuien(models.Model):
  _name = "pyme.notificaciones.aquien"
  _description = "A quien he notificado"
  _order = "create_date desc"


  name = fields.Many2one('pyme.notificaciones', string='Notificación')
  contacto = fields.Many2one('res.partner', string='A quien')
  metodo = fields.Char(string='Método')
  como = fields.Char(string='Como he notificado')



class NotificacionesBotonesTelegram(models.Model):
  _name = "pyme.notificaciones.botonestelgram"
  _description = "Botones Telegram"
  _order = "create_date desc"


  name = fields.Char(string='Texto')
  notifm2o = fields.Many2one('pyme.notificaciones.configuracion', string='Notificación')
  tipo = fields.Selection([('url', 'Link URL'), ('datos', 'Datos')], string='Tipo Botón', required=True, default='url')
  datos = fields.Char(string='Contenido')
  


class NotificacionesDiasFestivos(models.Model):
  _name = "pyme.notificaciones.df"
  _description = "Días Festivos"
  _order = "create_date desc"

  name = fields.Char(string='Nombre')
  dia = fields.Date(string='Calendario')

  _sql_constraints = [('dia_uniq', 'unique (dia)','Ese Dia ya cuenta como Festivo en el Listado. Escoge otro día')]


class NotificacionesDiasEspeciales(models.Model):
  _name = "pyme.notificaciones.de"
  _description = "Días Especiales"
  _order = "create_date desc"

  name = fields.Char(string='Nombre')
  dia = fields.Date(string='Calendario')

  _sql_constraints = [('dia_uniq', 'unique (dia)','Ese Dia ya cuenta como Festivo en el Listado. Escoge otro día')]


 
 
class NotificacionesControlHorario(models.Model):
  _name = "pyme.notificaciones.gc"
  _description = "Horario Notificaciones"
  _order = "create_date desc"


  name = fields.Char(string='Nombre')
  default = fields.Boolean(string='Horario por defecto')
  modelos = fields.Many2many('ir.model', string='Modelos Involucrados')
  contactos = fields.Many2many('res.partner', string='Usuarios Incluidos')
  obs = fields.Text(string='Observaciones')
  contactos = fields.One2many('res.partner','horario',string='Contactos')
  diasfestivosa = fields.Boolean(string='Excepto Días Festivos')
  diasespeciales = fields.Many2many('pyme.notificaciones.de', string='Excepto Días Especiales')
  diasfestivos = fields.Many2many('pyme.notificaciones.df', string='Excepto Días Festivos')
  lunes = fields.Boolean(string='Lunes')
  martes = fields.Boolean(string='Martes')
  miercoles = fields.Boolean(string='Miércoles')
  jueves = fields.Boolean(string='Jueves')
  viernes = fields.Boolean(string='Viernes')
  sabado = fields.Boolean(string='Sábado')
  domingo = fields.Boolean(string='Domingo')
  luneshi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Inicio', default='00')
  lunesmi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Inicio', default='00')
  luneshf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Fin', default='00')  
  lunesmf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Final', default='00')
  marteshi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Inicio', default='00')
  martesmi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Inicio', default='00')
  marteshf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Fin', default='00')  
  martesmf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Final', default='00')
  miercoleshi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Inicio', default='00')
  miercolesmi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Inicio', default='00')
  miercoleshf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Fin', default='00')  
  miercolesmf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Final', default='00')
  jueveshi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Inicio', default='00')
  juevesmi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Inicio', default='00')
  jueveshf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Fin', default='00')  
  juevesmf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Final', default='00')
  vierneshi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Inicio', default='00')
  viernesmi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Inicio', default='00')
  vierneshf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Fin', default='00')  
  viernesmf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Final', default='00')
  sabadohi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Inicio', default='00')
  sabadomi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Inicio', default='00')
  sabadohf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Fin', default='00')  
  sabadomf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Final', default='00')
  domingohi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Inicio', default='00')
  domingomi = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Inicio', default='00')
  domingohf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23')], string='Hora Fin', default='00')  
  domingomf = fields.Selection([('00', '00'),('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31'),('32', '32'),('33', '33'),('34', '34'),('35', '35'),('36', '36'),('37', '37'),('38', '38'),('39', '39'),('40', '40'),('41', '41'),('42', '42'),('43', '43'),('44', '44'),('45', '45'),('46', '46'),('47', '47'),('48', '48'),('49', '49'),('50', '50'),('51', '51'),('52', '52'),('53', '53'),('54', '54'),('55', '55'),('56', '56'),('57', '57'),('58', '58'),('59', '59')], string='Minuto Final', default='00')
