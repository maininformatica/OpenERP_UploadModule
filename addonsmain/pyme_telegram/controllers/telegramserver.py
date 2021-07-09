#!/usr/bin/python

import telebot
import config
import xmlrpc.client
import pycurl, json, requests
import datetime
import time
from datetime import timedelta
from unidecode import unidecode
from telebot import types
from telebot.types import ReplyKeyboardMarkup,KeyboardButton,KeyboardButtonPollType,ReplyKeyboardRemove
import psycopg2 
import unidecode
import sys
import os

url_odoo = str(sys.argv[2])
bbdd_odoo = str(sys.argv[3])
user_odoo = str(sys.argv[4])
pass_odoo = str(sys.argv[5])

### dataapicon="http://192.168.45.182:8069#HELP#admin#admin"
dataapicon= str(url_odoo) + "#" + str(bbdd_odoo) + "#" + str(user_odoo) + "#" + str(pass_odoo) + ""
url = str(dataapicon.split("#")[0]) 
username = str(dataapicon.split("#")[2])  
pwd = str(dataapicon.split("#")[3])  
dbname = str(dataapicon.split("#")[1])  
sock_common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) 
uid = sock_common.login(dbname, username, pwd) 
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url)) 

## API_TOKEN = '1730507116:AAEbitOTTnIefEnJE43EB5B5bUuEHxEYzEk'
API_TOKEN = str(sys.argv[1])

r = requests.get("https://api.telegram.org/bot" + str(API_TOKEN) + "/deleteWebhook")
r.json()


token = str(API_TOKEN)
bot = telebot.TeleBot(API_TOKEN, threaded=False)


global estadobot
estadobot = False



### SQL
## connection = psycopg2.connect(user=sqluser, password=sqlpass, host=sqlhost, port=sqlport, database=sqlbd) 
connection = psycopg2.connect(database=dbname) 
cursordb = connection.cursor() 


def save_slot(chat_id,variable):
   f = open( "/tmp/slot_" + str(chat_id) + ".txt", 'w' )
   f.write(str(chat_id) + "|" + str(variable))
   f.close()

def read_slot(chat_id,variable):
    data = ['False']
    try:
      with open ("/tmp/slot_" + str(chat_id) +".txt", "r") as myfile:
        data=myfile.readlines()
    except:
        data = ['False']
    return str(data[0])
def del_slot(chat_id):
    fichero = "/tmp/slot_" + str(chat_id) + ".txt"
    try:
        os.remove(str(fichero))
    except:
        print("NO puedo Borrar: >" + str(fichero) + "<")



def read_horario(chat_id):
   is_between = True
   mensajefh = ""
   partner_ids = models.execute_kw(dbname, uid, pwd, 'res.partner', 'search_read', [[['rasa_telegramid', '=', chat_id]]],{'fields': ['id', 'name','horario'], 'limit': 1})    
   if partner_ids != []:
      partner_id = partner_ids[0]['id']
      partner_name = partner_ids[0]['id']
      print("El partner tiene el horario: >" + str(partner_ids[0]['horario']) + "<")
      if partner_ids[0]['horario'] != False:
        partner_horario_id = partner_ids[0]['horario'][0]
        partner_horario_mensaje = partner_ids[0]['horario'][1]
        if partner_horario_id != False:
          is_between = False
          hoario_ids = models.execute_kw(dbname, uid, pwd, 'pyme.notificaciones.gc', 'search_read', [[['id', '=', partner_horario_id]]],{'fields': ['id', 'name','mensajefh','lunes','martes','miercoles','jueves','viernes','sabado','domingo'], 'limit': 1})
          ### Miramos HORARIO
          now = datetime.datetime.now()
          dateahora = datetime.datetime.now() + timedelta(hours=2)
          diasemana = datetime.datetime.today().strftime('%A')
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
          for horariodata in hoario_ids:
             lunes = horariodata['lunes']
             martes = horariodata['martes']
             miercoles = horariodata['miercoles']
             jueves = horariodata['jueves']
             viernes = horariodata['viernes']
             sabado = horariodata['sabado']
             domingo = horariodata['domingo']
             if str(lunes) == "True" and str(diasemana) == "lunes": diaok = "lunes"
             if str(martes) == "True" and str(diasemana) == "martes": diaok = "martes"
             if str(miercoles) == "True" and str(diasemana) == "miercoles": diaok = "miercoles"
             if str(jueves) == "True" and str(diasemana) == "jueves":  diaok = "jueves"
             if str(viernes) == "True" and str(diasemana) == "viernes":  diaok = "viernes"
             if str(sabado) == "True" and str(diasemana) == "sabado":  diaok = "sabado"
             if str(domingo) == "True" and str(diasemana) == "domingo":  diaok = "domingo"
             ### print("Los datos son: " + str(horariodata) + "")
             hora = hora.split('.')
             hora = hora[0]
             cursordb.execute("SELECT " + str(diaok) + "hi," + str(diaok) + "mi  FROM pyme_notificaciones_gc WHERE id='" + str(partner_horario_id) + "' LIMIT 1")
             resultv = cursordb.fetchone()
             horaini = resultv[0]
             minini = resultv[1]
             cursordb.execute("SELECT " + str(diaok) + "hf," + str(diaok) + "mf  FROM pyme_notificaciones_gc WHERE id='" + str(partner_horario_id) + "' LIMIT 1")
             resultv = cursordb.fetchone()
             horafin = resultv[0]
             minfin = resultv[1]
             hstart = horaini + ":" + minini
             hend = horafin + ":" + minfin
             ## between = is_hour_between(hstart,hend,hora)
             is_between = False
             is_between |= hstart <= hora <= hend
             is_between |= hend < hstart and (hstart <= hora or hora <= hend)
             mensajefh = str(hoario_ids[0]['mensajefh'])
             print(str(mensajefh))
   return [ is_between, mensajefh ]




def insertaconversacion(chat_id,quien,mensaje):
       partner_id = 3
       channel_id = False
       partner_ids = models.execute_kw(dbname, uid, pwd, 'res.partner', 'search_read', [[['rasa_telegramid', '=', chat_id]]],{'fields': ['id', 'name'], 'limit': 1})    
       ### try:
       if 1 == 1:
        
        if partner_ids != []:
          partner_id = partner_ids[0]['id']
          channel_ids = models.execute_kw(dbname, uid, pwd, 'mail.channel', 'search_read', [[['chatuser', '=', partner_id],['channel_type', '=', 'telegram']]],{'fields': ['id', 'name'], 'limit': 1})    
          if channel_ids == []:
             channel_id = models.execute_kw(dbname, uid, pwd, 'mail.channel', 'create', [{'name': chat_id, 'channel_type': 'telegram', 'chatuser': partner_id}])
          else:
             channel_id = channel_ids[0]['id']
          ## print("\n\n Partner: >" +  str(partner_ids) + "<  Channel: " + str(channel_id)  + " \n\n")
        else:
          cursordb.execute("select count(*) from mail_channel WHERE name='" + str(chat_id) + "' and chatuser='" + str(partner_id) + "'")
          namepart = cursordb.fetchone() 
          if str(namepart[0]) == "0":
            createchannel = models.execute_kw(dbname, uid, pwd, 'mail.channel', 'create', [{
                 'name': chat_id,
                 'channel_type': 'telegram',
                 'chatuser': partner_id}])
            channel_id = createchannel
          else:
            channel_ids = models.execute_kw(dbname, uid, pwd, 'mail.channel', 'search_read', [[['chatuser', '=', partner_id],['channel_type', '=', 'telegram']]],{'fields': ['id', 'name'], 'limit': 1})    
            channel_id = channel_ids[0]['id']
        if channel_id != False:
          if quien == "bot": 
             partner_id = 1
          idnuevomensaje = models.execute_kw(dbname, uid, pwd, 'mail.message', 'create', [{
                 'model': 'mail.channel',
                 'message_type': 'comment',
                 'subtype_id': 1,
                 'record_name': str(mensaje),
                 'body': '<p>' + str(mensaje) + '</p>',
                 'res_id': int(channel_id),
                 ## 'parent_id': msg_id,
                 'author_id': partner_id,
                 }])
        print("Chat: " + str(chat_id) + " Quien: " + str(quien) + " Mensaje: " + str(mensaje) + " Parner: " + str(partner_id) + " Canal: " + str(channel_id) + "")
       ### except:
       ###  print("Error Al insertar la conversacion")


def normalize(s):
    replacements = (
        ("á", "a"),
        ("à", "a"),
        ("é", "e"),
        ("è", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ò", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.lower())
    return s


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    ## print ("\n\n La llamada es: " + str(call) + "")
    chat_id = call.from_user.id
    ## chat_id = False
    answer = "False"
    mensajes_error_ids = models.execute_kw(dbname, uid, pwd, 'pyme.telegrambot', 'search_read', [[['id','=',8]]], {'fields': ['salidavacia', 'salidanoentiendo']})
    markup = telebot.types.InlineKeyboardMarkup()


    ##
    ## CANCELAR
    ##
    if 'CANCELAR|' in call.data:
         datastr = str(call.data).split("|")
         chat_id = datastr[1]
         delslot = del_slot(chat_id)
         answer = "Has Cancelado el Proceso. Para inciar el Chat escribe: hola"

    ##
    ## AYUDA
    ##
    if '/help' in call.data:
       botid_ids = models.execute_kw(dbname, uid, pwd, 'pyme.telegram', 'search_read', [[['token_telegram', '=', token]]],{'fields': ['id', 'mensajehelp'], 'limit': 1})    
       mensajehelp = botid_ids[0]['mensajehelp']
       answer = str(mensajehelp)


    ##
    ## INICIO DE REGISTRO
    ##

    ## Registrarse Paso 1
    if 'registro-paso1|' in call.data:
         datastr = str(call.data).split("|")
         chat_id = datastr[1]
         answer = "Hola. Vamos a proceder al Alta de Usuario.\nEs un proceso de tres preguntas. Escribiendo <b>cancelar</b> saldrá del proceso de registro en cualquier paso."
         answer += "\n\nEn cualquier momento podrás pinchar en el botón CANCELAR para salir del proceso"
         estadobot = "registro-paso2|" + str(chat_id)
         markup.add(telebot.types.InlineKeyboardButton(text="CANCELAR", callback_data="CANCELAR|" + str(chat_id) + ""))
         markup.add(telebot.types.InlineKeyboardButton(text="SIGUIENTE >>", callback_data="registro-paso2|" + str(chat_id) + ""))
         slot = save_slot(chat_id,estadobot)

    ## Registrarse Paso 2
    if 'registro-paso2|' in call.data:
         datastr = str(call.data).split("|")
         chat_id = datastr[1]
         answer = "Inciciamos el proceso.\nNecesitamos que escribas tu <b>NOMBRE</b>"
         estadobot = "registro-paso3|" + str(chat_id)
         markup.add(telebot.types.InlineKeyboardButton(text="CANCELAR", callback_data="CANCELAR|" + str(chat_id) + ""))
         slot = save_slot(chat_id,estadobot)
    ## Registrarse Paso FINAL
    if 'registro-pasof|' in call.data:
         datastr = str(call.data).split("|")
         try: 
           chat_id = datastr[1]
           nombre = datastr[2]  
           email = datastr[3]
           telefono = datastr[4]
           answer = "Gracias por Registrarte " + str(nombre) + "."  
           idnuevouser = models.execute_kw(dbname, uid, pwd, 'res.users', 'create', [{
                 'name': nombre,
                 'origencliente': 'Telegram',
                 'login': email,
                 'sel_groups_1_9_10': 9
                 }])
           partnersdesc = models.execute_kw(dbname, uid, pwd, 'res.users', 'read', [idnuevouser])
           partner_dataid = partnersdesc[0]["partner_id"]
           ## print ("\n\nUser" + str(idnuevouser) + "\n Partner: " + str(partner_dataid[0]) + "")
           updatereservcreate = models.execute_kw(dbname, uid, pwd, 'res.partner', 'write', [[partner_dataid[0]], {'email': email}])
           updatereservcreate = models.execute_kw(dbname, uid, pwd, 'res.partner', 'write', [[partner_dataid[0]], {'phone': telefono}])
           updatereservcreate = models.execute_kw(dbname, uid, pwd, 'res.partner', 'write', [[partner_dataid[0]], {'rasa_telegramid': chat_id}])
           mensaje = "Casi hemos acabado <b>" + str(nombre) + "</b>. Hemos enviado un email a tu cuenta <b>" + str(email) + "</b>, con las instrucciones para poder generar una contraseña y activar la cuenta."
           estadobot = "registro-completado|" + str(chat_id)
           slot = save_slot(chat_id,estadobot)
           slot = del_slot(chat_id)
         except:
           answer = "ha ocurrido un error en el Registro Inténtalo de Nuevo más tarde"  
           slot = del_slot(chat_id)


    ##
    ## FIN DE REGISTRO
    ##


    ##
    ## INICIO DE TICKETS
    ##

    ## Ver mis Tcikets
    if 'ver-mis-tickets|' in str(call.data):
         nomcli = ""
         datastr = str(call.data).split("|")
         try:
           partid = int(datastr[1])
           entorno = "contacto"
         except:
           partid = 0
           entorno = "guest"

         user_datac = models.execute_kw(dbname, uid, pwd, 'res.users', 'search', [[['partner_id', '=', partid]]])
         usersdesc = models.execute_kw(dbname, uid, pwd, 'res.users', 'read', [user_datac])
         if usersdesc != []:
           userpart_id = usersdesc[0]["id"]
           tipousuario = usersdesc[0]["sel_groups_1_9_10"]
           print("Tipo Usuario: " + str(tipousuario))
           if str(tipousuario) == "1":
             entorno = "user"

         print("El PartID es: " + str(partid) + " y los datos recibidos son: " + str(call.data) + ". Entorno: " + str(entorno))
         answer = 'Mostramos Tus Tickets\n'
         if str(entorno) == "user":
            tickets_datac = models.execute_kw(dbname, uid, pwd, 'helpdesk_lite.ticket', 'search', [[['user_id', '=', userpart_id],['stage_id', 'not in', (4,5)]]])
            tickets_datac += models.execute_kw(dbname, uid, pwd, 'helpdesk_lite.ticket', 'search', [[['user_id', '=', False],['team_id.user_id', '=', 2],['stage_id', 'not in', (4,5)]]])
            tickets_datac.sort()
         else:
            tickets_datac = models.execute_kw(dbname, uid, pwd, 'helpdesk_lite.ticket', 'search', [[['partner_id', '=', partid],['stage_id', 'not in', (4,5)]]])
         if entorno == "contacto":
            markup.add(telebot.types.InlineKeyboardButton(text=" CREAR NUEVO TICKET ", callback_data="crear-ticket|" + str(partid) + ""))
         for tickets in tickets_datac:
             tickets_id = models.execute_kw(dbname, uid, pwd, 'helpdesk_lite.ticket', 'read', [tickets])
             desc_id = tickets_id[0]["id"]
             desc_name = tickets_id[0]["name"]
             partner_name = tickets_id[0]["partner_id"][1]
             if str(entorno)=="user":
               nomcli = partner_name + " :: "
             ## answer += "Ticket #" + str(desc_id) + ", Asunto: " + str(desc_name) + ".\n"
             tipodoc = "helpdesk_lite.ticket"
             markup.add(telebot.types.InlineKeyboardButton(text=str(nomcli) + "Ticket #" + str(desc_id) + " : " + str(desc_name) + "", callback_data="ver-doc|" + str(partid) + "|" + str(desc_id) + "|" + str(tipodoc)))
    ## Ver Tickets específico
    ### if 'ver-ticket|' in str(call.data):
    if 'ver-doc|' in str(call.data):
         datastr = str(call.data).split("|")
         try:
           partid = int(datastr[1])
         except:
           partid = 0
         try:
           desc_id = int(datastr[2])
         except:
           desc_id = 0
         try:
           modelname = str(datastr[3])
         except:
           modelname = "False"
         print("El PartID es: " + str(partid) + " >" + str(modelname) + "< ")
         markup = telebot.types.InlineKeyboardMarkup()
         if str(modelname) == "helpdesk_lite.ticket":
             answer = "Mostramos El Ticket <b>#" + str(desc_id) + "</b>\n"
             tickets_datac = models.execute_kw(dbname, uid, pwd, str(modelname), 'search', [[['id', '=', desc_id]]])
             for ticketid in tickets_datac:
                 tickets_id = models.execute_kw(dbname, uid, pwd, str(modelname), 'read', [ticketid])
                 desc_name = tickets_id[0]["name"]
                 estado_name = tickets_id[0]["stage_id"][1]
                 asignado_name = tickets_id[0]["user_id"]
                 if str(asignado_name) != "False":
                    estado = "Asignado a: <b>" + str(tickets_id[0]["user_id"][1]) + "</b>\n"
                 else:
                    estado = ""
                 answer += "Asunto: <b>" + str(desc_name) + "</b>\n"
                 answer += "Estado: <b>" + str(estado_name) + "</b>\n"
                 answer += estado
                 markup.add(telebot.types.InlineKeyboardButton(text='Escribir un Comentario', callback_data="escribit-cmnt|" + str(partid) + "|" + str(ticketid) + ""))
                 markup.add(telebot.types.InlineKeyboardButton(text='Cerrar Ticket', callback_data="cerrar-ticket|" + str(partid) + "|" + str(ticketid) + ""))
                 ## Mensajes
                 ticket_msgids = models.execute_kw(dbname, uid, pwd, 'mail.message', 'search',[[['model', '=', str(modelname)],['message_type', '=', 'comment'],['res_id', '=', int(ticketid)]]], {'offset': 0, 'order': 'date'})
                 ## print("\n\n MSG" + str(ticket_msgids) + "\n\n")
                 try:
                  mensajeticket = "\nMensajes ----------------------------------"
                  for descmsg_id in ticket_msgids:
                    descmsg = models.execute_kw(dbname, uid, pwd, 'mail.message', 'read', [int(descmsg_id)])
                    descmsg_date = descmsg[0]["date"]
                    fechaguay = datetime.datetime.strptime(descmsg_date, '%Y-%m-%d %H:%M:%S')
                    fechamenos = fechaguay + datetime.timedelta(hours=1)
                    descmsg_autor = descmsg[0]["author_id"][1]
                    descmsg_name = descmsg[0]["body"]
                    descmsg_name = descmsg_name.replace("<p>", "").replace("</p>", "")
                    mensajeticket += "\nFecha:  " + str(fechamenos) + " "                     
                    mensajeticket += "\nAutor:  " + str(descmsg_autor) + " "                    
                    mensajeticket += "\nTexto:  " + str(descmsg_name) + " "                
                    mensajeticket += "\n-------------------------------------------"
                 except:
                    mensajeticket = "\nNo hemos encontrado mensajes asociados al ticket."
         if str(modelname) == "project.task":
             answer = "Mostramos La Tarea <b>#" + str(desc_id) + "</b>\n"
             tickets_datac = models.execute_kw(dbname, uid, pwd, str(modelname), 'search', [[['id', '=', desc_id]]])
             for ticketid in tickets_datac:
                 tickets_id = models.execute_kw(dbname, uid, pwd, str(modelname), 'read', [ticketid])
                 desc_name = tickets_id[0]["name"]
                 estado_name = tickets_id[0]["stage_id"][1]
                 asignado_name = tickets_id[0]["user_id"]
                 if str(asignado_name) != "False":
                    estado = "Asignado a: <b>" + str(tickets_id[0]["user_id"][1]) + "</b>\n"
                 else:
                    estado = ""
                 answer += "Asunto: <b>" + str(desc_name) + "</b>\n"
                 answer += "Estado: <b>" + str(estado_name) + "</b>\n"
                 answer += estado
                 markup.add(telebot.types.InlineKeyboardButton(text='Escribir un Comentario', callback_data="escribit-cmnt|" + str(partid) + "|" + str(ticketid) + ""))
                 markup.add(telebot.types.InlineKeyboardButton(text='Cerrar Ticket', callback_data="cerrar-ticket|" + str(partid) + "|" + str(ticketid) + ""))
                 ## Mensajes
                 ticket_msgids = models.execute_kw(dbname, uid, pwd, 'mail.message', 'search',[[['model', '=', str(modelname)],['message_type', '=', 'comment'],['res_id', '=', int(ticketid)]]], {'offset': 0, 'order': 'date'})
                 ## print("\n\n MSG" + str(ticket_msgids) + "\n\n")
                 try:
                  mensajeticket = "\nMensajes ----------------------------------"
                  for descmsg_id in ticket_msgids:
                    descmsg = models.execute_kw(dbname, uid, pwd, 'mail.message', 'read', [int(descmsg_id)])
                    descmsg_date = descmsg[0]["date"]
                    fechaguay = datetime.datetime.strptime(descmsg_date, '%Y-%m-%d %H:%M:%S')
                    fechamenos = fechaguay + datetime.timedelta(hours=1)
                    descmsg_autor = descmsg[0]["author_id"][1]
                    descmsg_name = descmsg[0]["body"]
                    descmsg_name = descmsg_name.replace("<p>", "").replace("</p>", "")
                    mensajeticket += "\nFecha:  " + str(fechamenos) + " "                     
                    mensajeticket += "\nAutor:  " + str(descmsg_autor) + " "                    
                    mensajeticket += "\nTexto:  " + str(descmsg_name) + " "                
                    mensajeticket += "\n-------------------------------------------"
                 except:
                    mensajeticket = "\nNo hemos encontrado mensajes asociados al ticket."






             answer += mensajeticket



         markup.add(telebot.types.InlineKeyboardButton(text='Volver al Listado de Tickets', callback_data="ver-mis-tickets|" + str(partid) + ""))
    ## Realizar Comentario TICKET
    if 'escribit-cmnt|' in str(call.data):
         datastr = str(call.data).split("|")
         try:
           partid = int(datastr[1])
         except:
           partid = 0
         try:
           desc_id = int(datastr[2])
         except:
           desc_id = 0
         print("El PartID es: " + str(partid) + "")
         estadobot = "comentario-ticket|" + str(desc_id) + "|" + str(partid)
         slot = save_slot(chat_id,estadobot)
         answer = 'Escribime el Comentario\n'
         markup.add(telebot.types.InlineKeyboardButton(text="CANCELAR", callback_data="CANCELAR|" + str(chat_id) + ""))
    ## Cerrar Ticket
    if 'cerrar-ticket|' in str(call.data):
         datastr = str(call.data).split("|")
         try:
           partid = int(datastr[1])
         except:
           partid = 0
         try:
           desc_id = int(datastr[2])
         except:
           desc_id = 0
         print("El PartID es: " + str(partid) + "")
         estadobot = "cerrar-ticketDef|" + str(desc_id) + "|" + str(partid)
         slot = save_slot(chat_id,estadobot)
         answer = "Estas Seguro que deseas Cerrar el Ticket #" + str(desc_id) + "\n"
         markup.add(telebot.types.InlineKeyboardButton(text="SI", callback_data="cerrar-ticketDef|" + str(partid) + "|" + str(desc_id) + ""))
         markup.add(telebot.types.InlineKeyboardButton(text="NO", callback_data="CANCELAR|" + str(chat_id) + ""))
    ## Cerrar Ticket
    if 'cerrar-ticketDef|' in str(call.data):
         datastr = str(call.data).split("|")
         try:
           partid = int(datastr[1])
         except:
           partid = 0
         try:
           desc_id = int(datastr[2])
         except:
           desc_id = 0
         tickets_datac = models.execute_kw(dbname, uid, pwd, 'helpdesk_lite.ticket', 'search', [[['id', '=', desc_id]]])
         for tickets in tickets_datac:
             tickets_id = models.execute_kw(dbname, uid, pwd, 'helpdesk_lite.ticket', 'read', [tickets])
             desc_id = tickets_id[0]["id"]
             desc_name = tickets_id[0]["name"]
         tickets_datac = models.execute_kw(dbname, uid, pwd, 'helpdesk_lite.ticket', 'write', [[desc_id], {'stage_id': 5}])
         ## HORARIO
         ## Funcion  
         horario = read_horario(chat_id)
         if horario[0] == True:
            print("Dentro de Horario")
            mensajefh = ""
         else:
            print ("Fuera de Horario: " + str(horario[1]) + "")
            mensajefh = str(horario[1]) + "\n\n"
         ## HORARIO
         ## Funcion  

         answer = mensajefh + "El Ticket #" + str(desc_id) + ", ha sido cerrado"
         

    ## Crear Ticket
    if 'crear-ticket|' in call.data:
         datastr = str(call.data).split("|")
         try:
           partid = int(datastr[1])
         except:
           partid = 0 
         estadobot = "crear-ticket-2|" + str(partid)
         slot = save_slot(chat_id,estadobot)
         answer = 'Escribe el Asunto del Ticket que quieres Abrir\n'
         markup.add(telebot.types.InlineKeyboardButton(text="CANCELAR", callback_data="CANCELAR|" + str(chat_id) + ""))
    ##
    ## FIN DE TICKETS
    ##

    ## Salidas Error
    if str(answer) == "False":
       answer = str(mensajes_error_ids[0]['salidavacia'])
    bot.send_message(call.message.chat.id, answer, reply_markup=markup, parse_mode="HTML")
    conversacion = insertaconversacion(chat_id,"bot",answer)
    return {}


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    ## bot.reply_to(message, message.text)
    ### print("\n\n         TODO EL MENSAJE \n\n")
    ### print(str(message))
    ### print("\n\n")
    markup = telebot.types.InlineKeyboardMarkup()
    chat_id = message.chat.id
    entrada=normalize(message.text)
    quien = chat_id
    botid_ids = models.execute_kw(dbname, uid, pwd, 'pyme.telegram', 'search_read', [[['token_telegram', '=', token]]],{'fields': ['id', 'inteligencia'], 'limit': 1})
    print("\n\n El CHAT ID: " + str(chat_id) + "\n\n")
    if 1 == 1:
    ## try: 
        ## HORARIO
        ## Funcion
        horario = read_horario(chat_id)
        if horario[0] == True:
           print("Dentro de Horario")
           mensajefh = ""
        else:
           print ("Fuera de Horario: " + str(horario[1]) + "")
           ## mensajefh = str(horario[1]) + "\n\n"
           mensajefh = ""
        ## HORARIO
        ## Funcion        

        try: 
           botid = botid_ids[0]['id']
           nlu = botid_ids[0]['inteligencia'][0]
           print("El BOT es: " + str(botid) + ". EL NLU Utilizado es: " + str(nlu) + ".")
        except:
           print("El BOT NO ESTA Congigurado SALGO")
           return {}
        slot = read_slot(chat_id,entrada)
        ## FUNCIONES
        print("SLOT: " + str(slot))
        entradalu = entrada
        conversacion = insertaconversacion(chat_id,quien,entrada)
        ## TODO A LOWER
        entrada = entrada.lower()
        ## entradalu = entradalu.lower()
        if "crear-ticket-2" in str(slot):
           slot_data = str(slot).split("|")
           doc_id=slot_data[2]
           idnuevoticket = False
           ## HORARIO
           ## Funcion  
           horario = read_horario(chat_id)
           if horario[0] == True:
              print("Dentro de Horario")
              mensajefh = ""
           else:
              print ("Fuera de Horario: " + str(horario[1]) + "")
              mensajefh = str(horario[1]) + "\n\n"
           ## HORARIO
           ## Funcion  
           try:
              idnuevoticket = models.execute_kw(dbname, uid, pwd, 'helpdesk_lite.ticket', 'create', [{'partner_id': doc_id,'name': str(entradalu), 'origen': 'telegram',}])
              ## mensaje="Hemos Creado el Ticket: " + str(entradalu) + " en el Número #" + str(idnuevoticket) + "."
              mensaje= mensajefh + "Ticket Creado: " + str(entradalu) + " en el Número #" + str(idnuevoticket) + "."
           except:
              mensaje="Ha Habido un Error al Crear el Ticket, inténtalo de nuevo más tarde."
           delslot = del_slot(chat_id)
           bot.send_message(chat_id, mensaje, reply_markup=markup, parse_mode="HTML")           
           ## return [ mensaje, markup ]
           return {}
        ## Registrarse Paso 3
        if 'registro-paso3|' in str(slot):
           mensaje = "Dime tu <b>EMAIL</b>"
           estadobot = "registro-paso4|" + str(chat_id) + "|" + str(entradalu)
           markup.add(telebot.types.InlineKeyboardButton(text="CANCELAR", callback_data="CANCELAR|" + str(chat_id) + ""))
           slot = save_slot(chat_id,estadobot)
           bot.send_message(chat_id, mensaje, reply_markup=markup, parse_mode="HTML")
           return {}
        ## Registrarse Paso 4
        if 'registro-paso4|' in str(slot):
           slot_data = str(slot).split("|")
           nombre = slot_data[3]
           mensaje = "Dime tu <b>TELÉFONO</b>"
           estadobot = "registro-paso5|" + str(chat_id) + "|" + str(nombre) + "|" + str(entradalu)
           markup.add(telebot.types.InlineKeyboardButton(text="CANCELAR", callback_data="CANCELAR|" + str(chat_id) + ""))
           slot = save_slot(chat_id,estadobot)
           bot.send_message(chat_id, mensaje, reply_markup=markup, parse_mode="HTML")
           return {}
        ## Registrarse Paso 5
        if 'registro-paso5|' in str(slot):
           slot_data = str(slot).split("|")
           try:
            nombre = slot_data[3]
           except: 
            nombre = False
           try:
            email = slot_data[4]
           except: 
            email = False
           telefono = entradalu
           mensaje = "Estos son Tus Datos\nNombre: <b>" + str(nombre) + "</b>\nEmail: <b>" + str(email) + "</b>\nTeléfono: <b>" + str(telefono) + "</b>\nId Telegram: " + str(chat_id) + "\n\n"
           mensaje += "\nDebes leer las condiciones de privacidad en pinchando <b><a href='http://192.168.50.243:8069/condiciones-de-registro-y-privacidad-de-datos'>AQUÍ</a></b>.\nPara aceptar el registro y las condiciones pulsa Aceptar. Si no estás conforme puedes cancelar el proceso"
           estadobot = "registro-pasof|" + str(chat_id) + "|" + str(nombre) + "|" + str(email) + "|" + str(entradalu)
           markup.add(telebot.types.InlineKeyboardButton(text="CANCELAR", callback_data="CANCELAR|" + str(chat_id) + ""))
           markup.add(telebot.types.InlineKeyboardButton(text="ACEPTAR", callback_data=estadobot))
           slot = save_slot(chat_id,estadobot)
           bot.send_message(chat_id, mensaje, reply_markup=markup, parse_mode="HTML")
           return {}
        ## COMENTARIO
        if "comentario-ticket|" in str(slot):
           slot_data = str(slot).split("|")
           doc_id=slot_data[2]
           msgids = models.execute_kw(dbname, uid, pwd, 'mail.message', 'search', [[['message_type', '=','notification'],['res_id', '=',int(doc_id)],['body','ilike','<p>Helpdesk Tickets crea']]])
           msgid = models.execute_kw(dbname, uid, pwd, 'mail.message', 'read', [msgids])
           msg_id = msgid[0]["id"]
           parner_id=slot_data[3]
           try:
              ## partner_datac = models.execute_kw(dbname, uid, pwd, 'res.partner', 'search', [[['rasa_telegramid', '=', chat_id]]])
              ## partnersdesc = models.execute_kw(dbname, uid, pwd, 'res.partner', 'read', [partner_datac])
              ## parner_id = partnersdesc[0]["id"]
              idnuevomensaje = models.execute_kw(dbname, uid, pwd, 'mail.message', 'create', [{
                 'model': 'helpdesk_lite.ticket',
                 'message_type': 'comment',
                 'subtype_id': 1,
                 'record_name': str(entradalu),
                 'body': '<p>' + str(entradalu) + '</p>',
                 'res_id': int(doc_id),
                 'parent_id': msg_id,
                 'author_id': parner_id,
                 }])
              mensaje="Hemos Guardado el comentario: " + str(entrada) + " en el Documento #" + str(doc_id) + "."
           except:
              mensaje="Error Al Guardar el Mensaje con id: " + str(doc_id) + " en el Parent: " + str(msg_id) + " Tu id de partner es: " + str(parner_id) + ", inténtalo de nuevo más tarde."
           delslot = del_slot(chat_id)
           bot.send_message(chat_id, mensaje, reply_markup=markup, parse_mode="HTML")
           return {}


        if botid != False:
           modo = models.execute_kw(dbname, uid, pwd, 'pyme.telegrambot', 'read', [nlu], {'fields': ['modo']})
           salidanoentiendo = models.execute_kw(dbname, uid, pwd, 'pyme.telegrambot', 'read', [nlu], {'fields': ['salidanoentiendo']})
           modo = modo[0]['modo']
           txtsalidanoentiendo = salidanoentiendo[0]['salidanoentiendo']
           ### print ("EL NLU es: " + str(nlu) + " y el modo es: " + str(modo) + "")
           print ("El CHAT ID ES: " + str(chat_id) +"")
           if str(modo) == "python":
              from logicapython import ActionBot
              respuesta = ActionBot.PythonBot(entrada,chat_id,estadobot,slot)
              contestacion = respuesta[0] 
              markup = respuesta[1]
              print("MODO PYTHON: Datos: " + str(entrada) + " >> " + str(contestacion) + " Estado: " + str(estadobot) + "")
              bot.send_message(chat_id, contestacion,reply_markup=markup, parse_mode="HTML")


           if str(modo) == "lin":
              markup = telebot.types.InlineKeyboardMarkup()
              entorno = "guest"
              partner_datac = models.execute_kw(dbname, uid, pwd, 'res.partner', 'search', [[['rasa_telegramid', '=', chat_id]]])
              partnersdesc = models.execute_kw(dbname, uid, pwd, 'res.partner', 'read', [partner_datac])
              if partnersdesc != []:
                 parner_name = partnersdesc[0]["name"]
                 parner_id = partnersdesc[0]["id"]
                 entorno = "contacto"
                 user_datac = models.execute_kw(dbname, uid, pwd, 'res.users', 'search', [[['partner_id', '=', parner_id]]])
                 usersdesc = models.execute_kw(dbname, uid, pwd, 'res.users', 'read', [user_datac])
                 if usersdesc != []:
                    userpart_id = usersdesc[0]["id"]
                    tipousuario = usersdesc[0]["sel_groups_1_9_10"]
                    print("Tipo Usuario: " + str(tipousuario))
                    if str(tipousuario) == "1":
                       entorno = "user"
              cursordb.execute("select pyme_linnlu_id from pyme_bot_entradasnlu_pyme_linnlu_rel WHERE pyme_bot_entradasnlu_id in (select id from pyme_bot_entradasnlu WHERE name LIKE '%" + str(entrada) + "%')")
              namepart = cursordb.fetchall()              
              contestacion = ""
              print(">> El Entorno es: " + str(entorno) + " y las lineas de contestacion son: " + str(namepart) + "")
              mensajelog = ""
              for buscalin in namepart:
                idmilin = buscalin[0]
                respuestas_ids = models.execute_kw(dbname, uid, pwd, 'pyme.linnlu', 'search', [[['id', '=',int(idmilin)],['nlu', '=',nlu],['entorno', '=',entorno]]])
                buscaresp = models.execute_kw(dbname, uid, pwd, 'pyme.linnlu', 'read', [respuestas_ids])
                print("\n\nBOTID: " + str(botid) + " Tenemos: " + str(idmilin) + " NLU: " + str(nlu) + " >>>> " + str(buscaresp) + "\n\n")
                if buscaresp != []:
                   for respuestas in buscaresp:
                     respuestasid = respuestas["id"]
                     datoscliente = models.execute_kw(dbname, uid, pwd, 'res.partner', 'search_read', [[['rasa_telegramid', '=', chat_id]]],{'fields': ['id', 'name'], 'limit': 1})
                     print("AQUI EN MADRID")
                     try:
                       num = datoscliente[0]['id']
                       partner_name= datoscliente[0]['name']
                     except:
                       num = 0
                       partner_name = False
                     contestaciond = str(respuestas['contestacion'])
                     try:
                       contestaciond = contestaciond.replace('$respid',str(respuestasid))
                       contestaciond = contestaciond.replace('$idcliente',str(num))
                       contestaciond = contestaciond.replace('$cliente',str(partner_name))
                       contestaciond = contestaciond.replace('$chatid',str(chat_id))
                       contestacion += str(contestaciond)
                     except:
                       contestacion += str(contestaciond)
                     ## print ("Aui estaoyu: " + str(respuestas['contestacion']) + "")
                     botones_ids = models.execute_kw(dbname, uid, pwd, 'pyme.bot.botonestelgram', 'search', [[['preguntaslin', '=',respuestasid]]])
                     for botones in botones_ids:
                       boton = models.execute_kw(dbname, uid, pwd, 'pyme.bot.botonestelgram', 'read', [botones])
                       tipo = boton[0]["tipo"]
                       datos = boton[0]["datos"]
                       try: 
                         datos = datos.replace('$respid',str(respuestasid))
                         datos = datos.replace('$idcliente',str(num))
                         datos = datos.replace('$cliente',str(partner_name))
                         datos = datos.replace('$chatid',str(chat_id))
                       except:
                         datos = datos
                       name = boton[0]["name"]
                       mensajelog += name
                       try:
                         name = name.replace('$respid',str(respuestasid))
                         name = name.replace('$idcliente',str(num))
                         name = name.replace('$cliente',str(partner_name))
                         name = name.replace('$chatid',str(chat_id))
                       except:
                         name = name
                       if str(datos) != "False":
                        try:
                         if str(tipo) == "url":
                           markup.add(telebot.types.InlineKeyboardButton(text=str(name), url=str(datos)))
                         if str(tipo) == "datos":
                           markup.add(telebot.types.InlineKeyboardButton(text=str(name), callback_data=str(datos)))
                         ## print("Aqui hay uno URL: " + str(datos) + " para la contestacion: " + str(contestacion) + "")
                        except:
                         print("Error al Montar los Botones de Contestación")

              else:
                 if botid != False and str(contestacion) == "":
                    ## print ("EL NLU es: " + str(nlu) +"")
                    ## print ("El CHAT ID ES: " + str(chat_id) +"")
                    contestacion = str(txtsalidanoentiendo)
                 ## else:
                 ##   contestacion = " Error al conectar con el Motor NLU"
                 print("MODO LINEAS: Datos: " + str(entrada) + " >> " + str(contestacion) + "")
              mensajelog = contestacion + "" + mensajelog
              conversacion = insertaconversacion(chat_id,"bot",mensajelog)
              contestacion = mensajefh + contestacion
              bot.send_message(chat_id, contestacion, reply_markup=markup, parse_mode="HTML")
bot.polling()
