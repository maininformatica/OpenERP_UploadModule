# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools
import random
import time
import asyncio

from odoo import models, _
import pycurl, json, requests
from odoo.exceptions import UserError, AccessError, ValidationError, Warning

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/opt/odoorasa/bin')




class RasaBot(models.AbstractModel):
  _name = 'rasa.bot'
  _description = 'Rasa Mail Bot'

  def _apply_logic(self, record, values, command=None):
        """ Apply bot logic to generate an answer (or not) for the user
        The logic will only be applied if odoobot is in a chat with a user or
        if someone pinged odoobot.

         :param record: the mail_thread (or mail_channel) where the user
            message was posted/odoobot will answer.
         :param values: msg_values of the message_post or other values needed by logic
         :param command: the name of the called command if the logic is not triggered by a message_post
        """

        pymebot = False
        if record.id != False:
           idconversacion = record.id
           livechat_id = self.env['mail.channel'].search([('id', '=', int(idconversacion))], limit=1).livechat_channel_id.id
           if livechat_id != False:
              bot = self.env['im_livechat.channel'].search([('id', '=', int(livechat_id))], limit=1).bot.id
              pymebot = True

        rasabot_id = self.env['ir.model.data'].xmlid_to_res_id("user_rasa_bot")
        ## self.env.cr.execute(""" SELECT id  FROM res_partner WHERE name='RasaBot' LIMIT 1""")
        self.env.cr.execute(""" SELECT id  FROM res_partner WHERE id='7' LIMIT 1""")
        resultv = self.env.cr.fetchone()
        rasabot_id = resultv[0]
        ## rasabot_id = 10
        if len(record) != 1 or values.get("author_id") == rasabot_id:
            return

        try:
           michannel = record.chatcerrado
           ### print("\n\n\n El tipo es: " + str(michannel) + "\n\n\n ")
        except:
           michannel = False        
        
        if self._is_bot_pinged(values) or self._is_bot_in_private_channel(record) or pymebot == True:
            body = values.get("body", "").replace(u'\xa0', u' ').strip().lower().strip(".?!")
            if michannel == True:
             answer = "Chat Cerrado. Cierra este chat y abre una nueva"
            else:
             answer = self._get_answer(record, body, values, command)
            author_idRasa = values.get('author_id')
            message =" MIERDA"
            if str(self.env.uid) == "1":
               usariochannel = str(author_idRasa)
            else:
               usariochannel = str(self.env.uid)
            if str(usariochannel) != "False":
                idchannel = str(record.id)
                partner_id = self.env['res.users'].search([('id', '=', usariochannel )]).partner_id.id

                if str(partner_id) == "False":
                   partner_id = usariochannel
                SQL = "UPDATE mail_channel SET  chatuser='" + str(partner_id) + "', public='public' WHERE id='" + str(idchannel) + "' and (chatuser IS NULL or chatuser='5')"
                ### print(str(SQL))
                self.env.cr.execute(SQL)
            else:
                idchannel = str(record.id)
                SQL = "UPDATE mail_channel SET  chatuser='5',public='public' WHERE id='" + str(idchannel) + "' and (chatuser IS NULL or chatuser='5')"
                self.env.cr.execute(SQL)

            if answer:
                message_type = values.get('message_type', 'comment')
                subtype_id = values.get('subtype_id', self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'))
                ## answer="Porompompero"
                record.with_context(mail_create_nosubscribe=True).sudo().message_post(body=answer, author_id=rasabot_id, message_type=message_type, subtype_id=subtype_id)



  def answer_lineas(self, idconversacion, body, idlin, entorno):
         respuestas = ""
         markup = False
         markupodoo = False
         mensaje = body.replace("<p>", "").replace("</p>", "")
         print("\n\n Recibiendo: " + str(mensaje) + "")
         self.env.cr.execute("select pyme_linnlu_id from pyme_bot_entradasnlu_pyme_linnlu_rel WHERE pyme_bot_entradasnlu_id in (select id from pyme_bot_entradasnlu WHERE name LIKE '%" + str(mensaje) + "%')")
         buscamoslineas = self.env.cr.fetchall()
         for buscalin in buscamoslineas:
             linea = buscalin[0]
             respuestas_ids = self.env['pyme.linnlu'].search([('id', '=', linea),('nlu','=',idlin),('entorno','=',entorno)])
             ## print("Linea Entontrada: " + str(linea) + " y Respuesta: " + str(respuesta) + "")
             for respuesta in respuestas_ids:
               idrespuestas = respuesta.id
               botones_ids = self.env['pyme.bot.botonestelgram'].search([('preguntaslin','=',idrespuestas)])
               botonesodoo=""
               for botones in botones_ids:
                 tipo = botones.tipo
                 name = botones.name
                 print("Aqui hay uno URL: " + str(name) + "")
                 if str(botones.datos2) != "False": 
                    botonesodoo += "<br>" + str(botones.datos2)
               respuestas += str(respuesta.contestacion) + botonesodoo
               print("\n\n LINEAS: Entorno:" + str(entorno) + " Bot:" + str(idlin) + "Respuestas: " + str(idrespuestas) + ".")



         ## respuestas_ids = self.env['pyme.linnlu'].search([('name', '=ilike', mensaje),('nlu','=',idlin),('entorno','=',entorno)])
         ## for respuesta in respuestas_ids:
         ##    idrespuestas = respuesta.id
         ##    botones_ids = self.env['pyme.bot.botonestelgram'].search([('preguntaslin','=',idrespuestas)])
         ##    botonesodoo=""
         ##    for botones in botones_ids:
         ##      tipo = botones.tipo
         ##      name = botones.name
         ##      print("Aqui hay uno URL: " + str(name) + "")
         ##      if str(botones.datos2) != "False": 
         ##         botonesodoo += "<br>" + str(botones.datos2)
         ##    respuestas += str(respuesta.contestacion) + botonesodoo
         ##    print("\n\n LINEAS: Entorno:" + str(entorno) + " Bot:" + str(idlin) + "Respuestas: " + str(idrespuestas) + ".")
         return [ respuestas, markup, markupodoo ]



  def _get_answer(self, record, body, values, command=False):


        rasabot = True
        idconversacion = False
        if record.id != False:
           idconversacion = record.id
           livechat_id = self.env['mail.channel'].search([('id', '=', int(idconversacion))], limit=1).livechat_channel_id.id
           if livechat_id != False:
              body = values.get("body", "").replace(u'\xa0', u' ').strip().lower().strip(".?!")
              bot = self.env['im_livechat.channel'].search([('id', '=', int(livechat_id))], limit=1).bot.id
              bot_userid = self.env['pyme.telegrambot'].search([('id', '=', int(bot))], limit=1).usuarioasignado.partner_id.id
              esrasa = self.env['pyme.telegrambot'].search([('id', '=', int(bot))], limit=1).rasaserver.id
              if esrasa == False:
                 rasabot = False
        ## print("\n\n\n Estamos AQUI. El BOT es: " + str(bot) + " ID CONVERSACION: " + str(idconversacion) + ", El Estado de RASA es: " + str(esrasa) + " . y el valor para RASA SERVER es: " + str(rasabot) + "\n\n\n")
        dataextra=""
        rasabot_state = self.env.user.rasabot_state
        if rasabot_state != 'onboarding_command2' and str(rasabot) == "True":
            ### RASA CONECTOR
            message = body
            serverrasa = message
            serverrasa1 = serverrasa.replace("<p>", "") 
            serverrasa2 = serverrasa1.replace("</p>", "")
            namebot = ""
            rasaport = ""
            idrasaserver = 2
            self.env.cr.execute(""" SELECT id FROM rasa_server ORDER BY id DESC LIMIT 1""")
            resultv = self.env.cr.fetchone()
            idrasaserver = resultv[0]
            rasaurl = namebot
            self.env.cr.execute(""" SELECT url FROM rasa_server ORDER BY id DESC LIMIT 1""")
            resultv = self.env.cr.fetchone()
            namebot = resultv[0]
            self.env.cr.execute(""" SELECT puertorasa FROM rasa_server ORDER BY id DESC LIMIT 1""")
            resultv = self.env.cr.fetchone()
            rasaport = resultv[0]
            rasaurl = namebot
            url = "http://"+ rasaurl +":" + rasaport + "/webhooks/rest/webhook/"
            userid = self.env.user.name
            dataextra += str(self.env.user.id)
            channelid = str(record.id)
            chatpartid = self.env['mail.channel'].search([('id', '=', channelid )]).chatuser.id
            chatuserid = self.env['res.users'].search([('partner_id', '=', chatpartid )]).id
            sessionid = self.env['ir.sessions'].search([('user_id', '=', chatuserid )], order='id desc', limit=1).session_id
            ### CADENAS DE CONEXION
            sqlurl = self.env['rasa.server'].search([('id', '=', idrasaserver )]).sqlurl            
            sqlport = self.env['rasa.server'].search([('id', '=', idrasaserver )]).sqlport
            odoodb = self.env['rasa.server'].search([('id', '=', idrasaserver )]).odoodb
            sqluser = self.env['rasa.server'].search([('id', '=', idrasaserver )]).sqluser
            sqlpass = self.env['rasa.server'].search([('id', '=', idrasaserver )]).sqlpass
            extrasqlcon = str(sqlurl) + "#" + str(sqlport) + "#" + str(odoodb) + "#" + str(sqluser) + "#" + str(sqlpass)

            apiurl = self.env['rasa.server'].search([('id', '=', idrasaserver )]).odoourl            
            apidb = self.env['rasa.server'].search([('id', '=', idrasaserver )]).odoodb
            apiuser = self.env['rasa.server'].search([('id', '=', idrasaserver )]).odoouser
            apipass = self.env['rasa.server'].search([('id', '=', idrasaserver )]).odoopass
            extraapicon = str(apiurl) + "#" + str(apidb) + "#" + str(apiuser) + "#" + str(apipass)

            dataextra += "-" + str(record.id) + "-" + str(chatpartid) + "-" + str(chatuserid) + "-" + str(sessionid) + "-" + str(extrasqlcon) + "-" + str(extraapicon)
            data = {"message": str(serverrasa2), "sender": "{\"user\": \"" + str(userid) + "\", \"extradata\": \"" + str(dataextra) + "\"}",}
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                        
            try:
              r = requests.post(url, data=json.dumps(data), headers=headers)
              responsem = r.text
              jsonformat  = str(responsem.replace("[", "").replace("]", "").replace("\n", " ").replace("},{", "}\n{") )
              for lines in jsonformat.splitlines():
                json_dat = json.loads(lines);
                try:
                    responsem = json_dat["image"]
                except:
                    responsem = ""
                try:
                    responsem = json_dat["text"]
                except:
                    responsem = ""

            except:
              responsem = "Error Al conectar con el Servidor RASA: " + str(rasaurl) + ". Puerto: " + str(rasaport) + "."

            
            return _(str(responsem))
            ### FIN > RASA CONECTOR

        else:
            if bot != False:
               mensaje = body.replace("<p>", "").replace("</p>", "")
               quiensoy = self.env.user.id
               print("\n\n   Eres: " + str(quiensoy) + "")
               if quiensoy != 1:
                  entorno = "user"
               else:
                  entorno = "guest"
               
               idlin = bot
               if idlin != False:
                  salidaerror = self.env['pyme.telegrambot'].search([('id', '=', bot)]).salidanoentiendo
                  modo = self.env['pyme.telegrambot'].search([('id', '=', bot)]).modo
                  respuestas = ""

                  if modo == "lin":
                     respuesta = self.answer_lineas(idconversacion, body, idlin,entorno)
                     contestacion = str(respuesta[0]).replace("\n", "<br>") 
                     respuestas += contestacion



                  if modo == "rasa":
                      respuestas += "ERROR: El estado del RASA no está habilitado o Inicializado"

                  if modo == "python":
                     from logicapython import ActionBot
                     ###                      
                     ### INICIO LOGICA PYTHON
                     ### 

                     chat_id = "0"
                     estadobot = False
                     slot = False
                     respuesta = ActionBot.PythonBot(mensaje,chat_id,estadobot,slot)
                     contestacion = str(respuesta[0]).replace("\n", "<br>")
                     markup = respuesta[1]
                     print("MODO PYTHON: Datos: " + str(mensaje) + " >> " + str(contestacion) + " Estado: " + str(estadobot) + "")
                     respuestas += contestacion

                     ###                      
                     ### FIN LOGICA PYTHON
                     ### 

                  if str(respuestas) == "":
                      respuestas = salidaerror
                  return _(str(respuestas))
            else: 
               return _("El estado del RASA no está habilitado o Inicializado")

        return False

  def _body_contains_emoji(self, body):
        # coming from https://unicode.org/emoji/charts/full-emoji-list.html
        emoji_list = itertools.chain(
            range(0x231A, 0x231c),
            range(0x23E9, 0x23f4),
            range(0x23F8, 0x23fb),
            range(0x25AA, 0x25ac),
            range(0x25FB, 0x25ff),
            range(0x2600, 0x2605),
            range(0x2614, 0x2616),
            range(0x2622, 0x2624),
            range(0x262E, 0x2630),
            range(0x2638, 0x263b),
            range(0x2648, 0x2654),
            range(0x265F, 0x2661),
            range(0x2665, 0x2667),
            range(0x267E, 0x2680),
            range(0x2692, 0x2698),
            range(0x269B, 0x269d),
            range(0x26A0, 0x26a2),
            range(0x26AA, 0x26ac),
            range(0x26B0, 0x26b2),
            range(0x26BD, 0x26bf),
            range(0x26C4, 0x26c6),
            range(0x26D3, 0x26d5),
            range(0x26E9, 0x26eb),
            range(0x26F0, 0x26f6),
            range(0x26F7, 0x26fb),
            range(0x2708, 0x270a),
            range(0x270A, 0x270c),
            range(0x270C, 0x270e),
            range(0x2733, 0x2735),
            range(0x2753, 0x2756),
            range(0x2763, 0x2765),
            range(0x2795, 0x2798),
            range(0x2934, 0x2936),
            range(0x2B05, 0x2b08),
            range(0x2B1B, 0x2b1d),
            range(0x1F170, 0x1f172),
            range(0x1F191, 0x1f19b),
            range(0x1F1E6, 0x1f200),
            range(0x1F201, 0x1f203),
            range(0x1F232, 0x1f23b),
            range(0x1F250, 0x1f252),
            range(0x1F300, 0x1f321),
            range(0x1F324, 0x1f32d),
            range(0x1F32D, 0x1f330),
            range(0x1F330, 0x1f336),
            range(0x1F337, 0x1f37d),
            range(0x1F37E, 0x1f380),
            range(0x1F380, 0x1f394),
            range(0x1F396, 0x1f398),
            range(0x1F399, 0x1f39c),
            range(0x1F39E, 0x1f3a0),
            range(0x1F3A0, 0x1f3c5),
            range(0x1F3C6, 0x1f3cb),
            range(0x1F3CB, 0x1f3cf),
            range(0x1F3CF, 0x1f3d4),
            range(0x1F3D4, 0x1f3e0),
            range(0x1F3E0, 0x1f3f1),
            range(0x1F3F3, 0x1f3f6),
            range(0x1F3F8, 0x1f400),
            range(0x1F400, 0x1f43f),
            range(0x1F442, 0x1f4f8),
            range(0x1F4F9, 0x1f4fd),
            range(0x1F500, 0x1f53e),
            range(0x1F549, 0x1f54b),
            range(0x1F54B, 0x1f54f),
            range(0x1F550, 0x1f568),
            range(0x1F56F, 0x1f571),
            range(0x1F573, 0x1f57a),
            range(0x1F58A, 0x1f58e),
            range(0x1F595, 0x1f597),
            range(0x1F5B1, 0x1f5b3),
            range(0x1F5C2, 0x1f5c5),
            range(0x1F5D1, 0x1f5d4),
            range(0x1F5DC, 0x1f5df),
            range(0x1F5FB, 0x1f600),
            range(0x1F601, 0x1f611),
            range(0x1F612, 0x1f615),
            range(0x1F61C, 0x1f61f),
            range(0x1F620, 0x1f626),
            range(0x1F626, 0x1f628),
            range(0x1F628, 0x1f62c),
            range(0x1F62E, 0x1f630),
            range(0x1F630, 0x1f634),
            range(0x1F635, 0x1f641),
            range(0x1F641, 0x1f643),
            range(0x1F643, 0x1f645),
            range(0x1F645, 0x1f650),
            range(0x1F680, 0x1f6c6),
            range(0x1F6CB, 0x1f6d0),
            range(0x1F6D1, 0x1f6d3),
            range(0x1F6E0, 0x1f6e6),
            range(0x1F6EB, 0x1f6ed),
            range(0x1F6F4, 0x1f6f7),
            range(0x1F6F7, 0x1f6f9),
            range(0x1F910, 0x1f919),
            range(0x1F919, 0x1f91f),
            range(0x1F920, 0x1f928),
            range(0x1F928, 0x1f930),
            range(0x1F931, 0x1f933),
            range(0x1F933, 0x1f93b),
            range(0x1F93C, 0x1f93f),
            range(0x1F940, 0x1f946),
            range(0x1F947, 0x1f94c),
            range(0x1F94D, 0x1f950),
            range(0x1F950, 0x1f95f),
            range(0x1F95F, 0x1f96c),
            range(0x1F96C, 0x1f971),
            range(0x1F973, 0x1f977),
            range(0x1F97C, 0x1f980),
            range(0x1F980, 0x1f985),
            range(0x1F985, 0x1f992),
            range(0x1F992, 0x1f998),
            range(0x1F998, 0x1f9a3),
            range(0x1F9B0, 0x1f9ba),
            range(0x1F9C1, 0x1f9c3),
            range(0x1F9D0, 0x1f9e7),
            range(0x1F9E7, 0x1fa00),
            [0x2328, 0x23cf, 0x24c2, 0x25b6, 0x25c0, 0x260e, 0x2611, 0x2618, 0x261d, 0x2620, 0x2626,
             0x262a, 0x2640, 0x2642, 0x2663, 0x2668, 0x267b, 0x2699, 0x26c8, 0x26ce, 0x26cf,
             0x26d1, 0x26fd, 0x2702, 0x2705, 0x270f, 0x2712, 0x2714, 0x2716, 0x271d, 0x2721, 0x2728, 0x2744, 0x2747, 0x274c,
             0x274e, 0x2757, 0x27a1, 0x27b0, 0x27bf, 0x2b50, 0x2b55, 0x3030, 0x303d, 0x3297, 0x3299, 0x1f004, 0x1f0cf, 0x1f17e,
             0x1f17f, 0x1f18e, 0x1f21a, 0x1f22f, 0x1f321, 0x1f336, 0x1f37d, 0x1f3c5, 0x1f3f7, 0x1f43f, 0x1f440, 0x1f441, 0x1f4f8,
             0x1f4fd, 0x1f4ff, 0x1f57a, 0x1f587, 0x1f590, 0x1f5a4, 0x1f5a5, 0x1f5a8, 0x1f5bc, 0x1f5e1, 0x1f5e3, 0x1f5e8, 0x1f5ef,
             0x1f5f3, 0x1f5fa, 0x1f600, 0x1f611, 0x1f615, 0x1f616, 0x1f617, 0x1f618, 0x1f619, 0x1f61a, 0x1f61b, 0x1f61f, 0x1f62c,
             0x1f62d, 0x1f634, 0x1f6d0, 0x1f6e9, 0x1f6f0, 0x1f6f3, 0x1f6f9, 0x1f91f, 0x1f930, 0x1f94c, 0x1f97a, 0x1f9c0]
        )
        if any(chr(emoji) in body for emoji in emoji_list):
            return True
        return False

  def _is_bot_pinged(self, values):
        ## rasabot_id = self.env['ir.model.data'].xmlid_to_res_id("user_rasa_bot")
        namebot = "RasaBot"
        rasabot_search = self.env['res.partner'].search([('name', 'ilike', namebot),"|", ("active", "=", True), ("active", "=", False),], limit=1)
        rasabot_id = int(rasabot_search.id)
        return (11, rasabot_id) in values.get('partner_ids', [])

  def _is_bot_in_private_channel(self, record):
        ## rasabot_id = self.env['ir.model.data'].xmlid_to_res_id("user_rasa_bot")
        namebot = "RasaBot"
        rasabot_search = self.env['res.partner'].search([('name', 'ilike', namebot),"|", ("active", "=", True), ("active", "=", False),], limit=1)
        rasabot_id = int(rasabot_search.id)
        modelname = str(record._name)
        modelid = str(record.id)
        ### print("************************************ " + str(modelname) + ":" + str(modelid))

        if str(modelname) == "pyme.mail.channel":
               res_id = self.env[str(modelname)].search([('id', '=', int(modelid))], limit=1).id
               ### print("\n\n HOLA ESTOY RECOGIENDO UN EMAIL \n\n")
               partid = 3
               self.env['mail.message'].create({'message_type':"comment",
                  'subtype_id': self.env.ref("mail.mt_comment").id, # subject type
                  'body': "Pincha <a href=\"/web?debug#action=169&model=mail.message&view_type=list\">aquí</a> para ver los Emails recibidos",
                  'subject': "Nuevo correo Recibido",
                  'needaction_partner_ids': [(4, partid)],   # partner to whom you send notification
                  'model': modelname,
                  'author_id': 7,
                  'res_id': res_id})


        ## Envios de Notificaciones
        ## Preparamos el Help Desk
        if str(modelname) == "helpdesk_lite.ticket":
           res_id = self.env[str(modelname)].search([('id', '=', int(modelid))], limit=1).id
           res_name = self.env[str(modelname)].search([('id', '=', int(modelid))], limit=1).name

           if str(res_id) != "False":
              mpartner_id = self.env[str(modelname)].search([('id', '=', int(res_id))], limit=1).partner_id.id
              if str(mpartner_id) != "False":
                 mmessage_txt = self.env['mail.message'].search([('model', '=', str(modelname)),('res_id', '=', int(res_id)),('message_type', '=', 'comment'),('author_id', '!=', int(mpartner_id))], limit=1, order='id desc').body
                 mmessage_txt = str(mmessage_txt).replace('<p>','').replace('</p>','')
                 useridname = "Jose Tormo"
                 partneridname = "Pepe Tormo Cliente"
                 partner_id2 = 88
                 user_id2 = 78
                 mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos asignado el Ticket: #" + str(self.id) + " a " + str(useridname)
                 mensajeusuario = "Hola " + str(useridname) + ". Te hemos asignado a ti el Ticket: #" + str(self.id) + "."
                 if str(mmessage_txt) != "False":
                    ## causa = "Ticket #:" + str(res_id) + " : " + str(res_name) + ", actualizado. Mensaje: " + str(mmessage_txt) + "."
                    causa = "" + str(mmessage_txt) + ""
                    modo="chatter"
                    asignado = False
                    estado = False
                    asunto = causa
                    self.pool.get('pyme.notificaciones').envianotificaciones(self, str(modelname), str(res_id) ,mensajeusuario ,mensajecliente, partner_id2, user_id2,causa,"CHATTER",modo,asignado,estado,asunto)


        ### enviatelegramc = "False"
        ### enviatelegramu = "False"
        ### enviabot = "False"
        ### enviamail = "False"
        ### urltelegram = "192.168.50.242:5005"

        ### ## Envios de Notificaciones a Telegram
        ### ## A Cliente
        ### if str(enviatelegramc) == "True" and str(rasatelegramid) != "False":
        ###         url = "http://" + str(urltelegram) + "/webhooks/telegram/webhook/"
        ###         data = { "update_id": 1, "message": { "message_id": 1, "from": { "id": "" + str(rasatelegramid) + "", "is_bot": False, "first_name": "", "username": "", "language_code": "es" }, "chat": { "id": "" + str(rasatelegramid) + "", "first_name": "", "username": "", "type": "private" }, "date": 1234, "text": "###dondeestais###|" + str(mensajeaenviar) + "" } }
        ###         headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        ###         r = requests.post(url, data=json.dumps(data), headers=headers)
        ###         responsem = r.text
        ### time.sleep(0.2)
        ### ## A Usuario
        ### if str(enviatelegramu) == "True" and str(rasatelegramidu) != "False":
        ###         url = "http://" + str(urltelegram) + "/webhooks/telegram/webhook/"
        ###         mensajeaenviar = "Estimado Usuario: " + str(rasatelegramidu) + " Se te ha asignado un Ticket"
        ###         data = { "update_id": 1, "message": { "message_id": 1, "from": { "id": "" + str(rasatelegramidu) + "", "is_bot": False, "first_name": "", "username": "", "language_code": "es" }, "chat": { "id": "" + str(rasatelegramidu) + "", "first_name": "", "username": "", "type": "private" }, "date": 1234, "text": "###dondeestais###|" + str(mensajeaenviar) + "" } }
        ###         headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        ###         r = requests.post(url, data=json.dumps(data), headers=headers)
        ###         responsem = r.text

        if record._name == 'mail.channel' and ( record.channel_type == 'chat' or record.channel_type == 'livechat' or record.channel_type == 'livechato'):
            return rasabot_id in record.with_context(active_test=False).channel_partner_ids.ids
        return False
