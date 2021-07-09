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

class RasaTraker(models.Model):

    _name = "events"
    _description = "Rasa Server Tracker"
    _order = 'id desc'

    name = fields.Char(string='Nombre')
    sender_id = fields.Char(string='Sender')
    type_name = fields.Char(string='Tipo')
    timestamp = fields.Float(string='Timestamp')
    intent_name = fields.Char(string='Intent')
    action_name = fields.Char(string='Accion')
    data = fields.Char(string='DATA')

class RasaConector(models.Model):

    _name = "rasa.server"
    _description = "Rasa Server Conector"
    _order = 'id desc'


    name = fields.Char(string='Descripción')
    url = fields.Char(string='Direccion Rasa')
    localhosturl= fields.Boolean(string='Modo Localhost')
    urlx = fields.Char(string='Direccion IP LAN/WAN', help='Direccion Publica del Servidor Utilizado para acceso Remoto, por Ejemplo Rasa X')
    puertorasa = fields.Char(string='Puerto API Rasa')
    direccionagente = fields.Char(string='Directorio Agente Local', help='Direcorio Servidor Local Donde se encuenta Agente de RASA')
    puertorasax= fields.Char(string='Puerto HTTP Rasa X')
    passwordx = fields.Char(string='Password Rasa X')
    stringconexion = fields.Char(string='Datos Conexion')
    state = fields.Selection([
       ('draft', 'No Conectado'),
       ('connected', 'Conectado'),
       ('error', 'Error'),
       ('cancel', 'Cancelado'),
       ], string='Status', copy=False, readonly=True, index=True, track_visibility='onchange', track_sequence=3, default='draft')
    readfiles = fields.Char(string='Lee Ficheros', compute='readyml')
    credentials = fields.Text(string='Fichero Credentials')
    endpoint = fields.Text(string='Fichero EndPoint')
    configfile = fields.Text(string='Fichero Configuracion')
    actions = fields.Text(string='Fichero Actions')
    backupfichero = fields.Boolean(string='Realiza Copia de Seguridad de los Ficheros Originales')
    acciones = fields.One2many('rasa.actions', 'relact' ,string='Acciones')
    credential = fields.One2many('rasa.credentials', 'relcred' ,string='Credentials')
    endpoints = fields.One2many('rasa.endpoints', 'relendp' ,string='EndPoints')
    funciones = fields.One2many('rasa.functions', 'relfunc' ,string='Funciones')
    apiusername = fields.Char(string='Username API')
    apipassword = fields.Char(string='Password API')
    apibbdd = fields.Char(string='BBDD API')
    logactions = fields.Text(string='Log Actions')
    sshpass = fields.Char(string='Rasa SSH Password')
    sshuser = fields.Char(string='Rasa SSH Username')
    sshport = fields.Char(string='Rasa SSH Puerto')
    image_url = fields.Char(string="Url")
    img_attach = fields.Html('Image Html')
    img_attachsrc = fields.Char('Image Html SRC')
    odoourl = fields.Char('Url Odoo')
    odoodb = fields.Char('BBDD Odoo')
    odoouser = fields.Char('User Odoo')
    odoopass = fields.Char('Pass Odoo')
    sqlurl = fields.Char('PostreSQL Host')
    sqlport = fields.Char('PostreSQL Host')
    sqldb = fields.Char('PostreSQL BBDD')
    sqluser = fields.Char('User PostreSQL')
    sqlpass = fields.Char('Pass PostreSQL')
    saludoinicial = fields.Char('Saludo Inicial', help='En este campo puedes inroducir el saludo inicial del Bot RASA')
    salidaerror = fields.Char('Salida Error', help='Cuando el Bot saca un error, este muestra el siguiente mensaje')
    salidavacia = fields.Char('Salida Vacia', help='Opción de texto de un mensaje para una salida sin datos a una pregunta')
    salidanoentiendo = fields.Char('Salida No entiendo', help='Respuesta del Bot ante una pregunta sin un NLU Válido')


    @api.onchange('image_url')
    def onchange_image_url(self):
         if self.image_url:
             self.img_attach = '<image id="img" src="' + str(self.image_url) + '"/>'
             self.img_attachsrc= '<iframe id="img" src="' + str(self.image_url) + '"/>'

    @api.onchange('odoodb')
    def onchange_odoodb(self):
         if self.odoodb:
             self.sqldb = self.odoodb
             return {}




    @api.multi
    def editor(self):
         idlocal = self.id
         return {
                'type': 'ir.actions.act_window',
                'name': 'Editor RASA',
                'res_model': 'rasa.server',
                'res_id': idlocal,
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('pyme_rasa.rasa_server_view2_form').id,
                'target': 'self'
         };



    @api.multi
    def probar_conexion(self, default=None):
        for serverrasa in self:
           
           if serverrasa.localhosturl:
               serverrasa.url = "localhost"
            
           rasa_server = "http://" + serverrasa.url + ":" + serverrasa.puertorasa
           proc = subprocess.Popen(["curl", rasa_server], stdout=subprocess.PIPE)
           msgrasa = (out, err) = proc.communicate()
           strmsgrasa =str(msgrasa[0])
           rasasa = strmsgrasa.split('\'')
           servidorconectado = "Hello" in rasasa
           if "Rasa" in rasasa[1]:
               rasaserver = self.url
               editor="http://" + str(rasaserver) + ":5000/editor/graphpage?bot=odoorasa#"
               self.write({'state': 'connected'})
               self.write({'stringconexion': rasasa[1]})
               self.write({'image_url': editor})
               self.write({'img_attach': '<image id="img" src="' + str(editor) + '"/>'})
               self.write({'img_attachsrc': '<iframe id="img" src="' + str(editor) + '"/>'})
		   
           else:
               self.write({'state': 'error'})
               raise UserError(_('Error al Conectar con RASA'))
           return 

    @api.multi
    def getapidata(self, default=None):
        bbdd =  self._cr.dbname
        self.write({'apibbdd': str(bbdd)})
        self.write({'apiusername': 'admin'})
        ## self.write({'apipassword': 'Admin%19'})
        return 


 
    def cerrar_conexion(self, default=None):
        for serverrasa in self:
            self.write({'state': 'draft'})
            self.write({'stringconexion': ''})
    

    def abrirrasax(self, default=None):
        
        ur1 = self.urlx
        passw = self.passwordx
        puertorasax = self.puertorasax

        url = "http://" + str(ur1) + ":" + str(puertorasax) + "/login?username=me&password=" + str(passw) + ""
        return {
            'name'     : 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'new',
            'url'      : url
               }
    


    @api.depends('readfiles')
    def form_recargar_rasa(self, default=None):
        
        if self.localhosturl:
           nameview = "rasa.server_restartview_form"
           self.env.cr.execute(""" select id from ir_ui_view where name='%s'""" % (nameview))
           result = self.env.cr.fetchone()
           ## raise UserError(_('La ID: ' + str(result[0]) + '.'))

           return {
            'res_id': self.id,
            'res_model': 'rasa.server',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': result[0],
            'target': 'new'
           }
        else:
           clientssh = SSHClient()
           clientssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
           clientssh.load_system_host_keys()
           username = self.sshuser
           password = self.sshpass
           hostnamessh = self.url
           portssh = self.sshport


           if str(username) == "False" or str(password) == "False" or str(hostnamessh) == "False" or str(portssh) == "False":
              raise AccessError("Alguno de los Parámetros SSH Necesarios no esta cumplimentado. Repase Username, Password y Puerto en la Ficha de Conexión SSH")
              return {}
           try:
              conex = clientssh.connect(hostname=str(hostnamessh), port=str(portssh), username=str(username), password=str(password), pkey=None, key_filename=None, timeout=None, allow_agent=True, look_for_keys=True, compress=False)
              if str(conex) == "None":
                stdin_, stdout_, stderr_ = clientssh.exec_command("/opt/odoorasa/bin/rasaactions.sh  odoorasa rasa")
                stdout_.channel.recv_exit_status()
                lines = stdout_.readlines()
                time.sleep(5)
                ### ftp_client=clientssh.open_sftp()
                ### ftp_client.get("/opt/odoorasa/rasa_actions.log","/opt/odoorasa/alquist-yaml-editor/bots/odoorasa/logs/full_log.out")
                ### ftp_client.close()
                for line in lines:
                      linesstr = ""
                      linesstr += (str(line))
                ## raise Warning(str(linesstr)) 

           except AuthenticationException:
                 raise Warning("Parece que el usuario y/o contraseña de la Configuracion SSH es incorrecto")
           except paramiko.ssh_exception.NoValidConnectionsError:
                 raise Warning("No Puedo conectar con el Servidor SHH. NO puedo recargar el RASA Server de Forma Remota")
           finally:
                clientssh.close() 



    @api.depends('readfiles')
    def recargar_rasa(self, default=None):
        
        dondeestoy = os.getcwd()
        dirrasatrain = self.direccionagente
        puertorasa = self.puertorasa
        puertorasax = self.puertorasax
        passwordx = self.passwordx


        hagobakcup = str(self.backupfichero)
        src_c="../" + dirrasatrain + "/credentials.yml"
        dst_c="../" + dirrasatrain + "/credentials.yml_OLD"
        src_e="../" + dirrasatrain + "/endpoints.yml"
        dst_e="../" + dirrasatrain + "/endpoints.yml_OLD"
        src_a="../" + dirrasatrain + "/actions.py"
        dst_a="../" + dirrasatrain + "/actions.py_OLD"


        if hagobakcup == 'True':
            copyfile(src_c, dst_c)
            copyfile(src_e, dst_e)
            copyfile(src_a, dst_a)
        
        
        ### ### Escribo Credentials
        ### credentialstxt = str(self.credentials)
        ### f= open(src_c,"w+")
        ### f.write(credentialstxt)
        ### f.close() 
        ### ### Escribo Credentials
        ### endpointtxt = str(self.endpoint)
        ### f= open(src_e,"w+")
        ### f.write(endpointtxt)
        ### f.close()
        ### ### Escribo Credentials
        ### actionstxt = str(self.actions)
        ### f= open(src_a,"w+")
        ### f.write(actionstxt)
        ### f.close()

        fechahoracopia = time.strftime("%y%m%d%H%M%S")

        

        src = "../" + dirrasatrain 
        dst = "../" + dirrasatrain + "-"+ fechahoracopia +"__copiaODOO"
        destination = shutil.copytree(src, dst)

        try:
 
            
            
            ## CREAMOS EL APIDATA
            dondeestoy = os.getcwd()
            dirrasatrain = self.direccionagente
            
            apiimport ="import xmlrpc.client\n"
            apiurl = "\nurl = \"http://localhost:8069\"\n"
            apiusername = "username = \"" + str(self.apiusername) + "\"\n"
            apipassword = "pwd = \"" + str(self.apipassword) + "\"\n"
            apibbdd = "dbname = \"" + str(self.apibbdd) + "\"\n"
            datoscomunes = """sock_common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) \nuid = sock_common.login(dbname, username, pwd) \nmodels = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url)) \n"""
            todapicon = "\n## Datos de Conexion API\n" + apiimport + "\n" + apiurl + apiusername + apipassword + apibbdd + datoscomunes + "\n"

            tmpfile="/tmp/apidata.py"
            destact="../" + dirrasatrain + "/apidata.py"
            codigotxt = str(todapicon)
            f= open(tmpfile,"w+")
            f.write(codigotxt)
            f.close()
            copyfile(tmpfile, destact)
            time.sleep(2)


            
            
            
            ## Escribo CREDENTIALS
            dondeestoy = os.getcwd()
            dirrasatrain = self.direccionagente
            ## Leer Fichero Cabecera
            file = open(dondeestoy + "/addons/pyme_rasa/data/cabecera_credenyend.txt", "r") 
            filecred = file.read() 
            for credenciales in self.credential:
                if credenciales.state == "online":
                    filecredx = """\n""" + credenciales.nameact +  """:\n"""
                    filecred = filecred + filecredx
                    for line in credenciales.codigo.splitlines():
                        line = " " + line + "\n"
                        filecred = filecred + line
                    tmpfile="/tmp/codigoaccion2_cred.py"
                    codigotxt = str(filecred)
                    f= open(tmpfile,"w+")
                    f.write(codigotxt)
                    f.close()
            destact="../" + dirrasatrain + "/credentials.yml"
            copyfile(tmpfile, destact)
            time.sleep(2)


            ## Escribo ENDPOINTS
            dondeestoy = os.getcwd()
            dirrasatrain = self.direccionagente
            ## Leer Fichero Cabecera
            file = open(dondeestoy + "/addons/pyme_rasa/data/cabecera_credenyend.txt", "r") 
            filecred = file.read() 
            for endpoints in self.endpoints:
                if endpoints.state == "online":
                    filecredx = """\n""" + endpoints.nameact +  """:\n"""
                    filecred = filecred + filecredx
                    for line in endpoints.codigo.splitlines():
                        line = " " + line + "\n"
                        filecred = filecred + line
                    tmpfile="/tmp/codigoaccion2_end.py"
                    codigotxt = str(filecred)
                    f= open(tmpfile,"w+")
                    f.write(codigotxt)
                    f.close()
            destact="../" + dirrasatrain + "/endpoints.yml"
            copyfile(tmpfile, destact)
            time.sleep(2)
            
            
            
            ## FUNCIONES
            dondeestoy = os.getcwd()
            dirrasatrain = self.direccionagente
            ## Leer Fichero Cabecera
            file = open(dondeestoy + "/addons/pyme_rasa/data/cabecera_functions.txt", "r") 
            filecred = file.read() 
            for acciones in self.funciones:
                if acciones.state == "online":
                    filecredx = """\n## Funcion escrita desde ODOO \n"""
                    filecred = filecred + filecredx
                    for line in acciones.codigo.splitlines():
                        line = "" + line + "\n"
                        filecred = filecred + line
                    filecred = filecred + """\n## FIN Acion escrita en Funciones \n"""
                    tmpfile="/tmp/codigoaccion2_func.py"
                    codigotxt = str(filecred)
                    f= open(tmpfile,"w+")
                    f.write(codigotxt)
                    f.close()
            destact="../" + dirrasatrain + "/functions.py"
            copyfile(tmpfile, destact)
            time.sleep(2)
            
            ## Escribo ACCIONES
            dondeestoy = os.getcwd()
            dirrasatrain = self.direccionagente
            ## Leer Fichero Cabecera
            file = open(dondeestoy + "/addons/pyme_rasa/data/cabecera_actions.txt", "r") 
            filecred = file.read() 
            for acciones in self.acciones:
                if acciones.state == "online":
                    ## raise UserError(_('' + str(acciones.name) + ''))
                    ## Leememos la variable de esta accion
                    filecredx = """\n\nclass Action""" + acciones.nameact +  """(Action):\n\tdef name(self) -> Text:\n\t\treturn \"action_""" + acciones.nameact +  """\"\n\tdef run(self, dispatcher: CollectingDispatcher,\n\t\ttracker: Tracker,\n\t\tdomain: Dict[Text, Any]) -> List[Dict[Text, Any]]:"""
                    filecredx = filecredx + """\n\n\t\t## Acion escrita en acciones.nameact\n"""
                    filecred = filecred + filecredx
                    for line in acciones.codigo.splitlines():
                        line = "\t\t " + line + "\n"
                        filecred = filecred + line
                    filecred = filecred + """\n\t\t ## return []\n"""
                    filecred = filecred + """\n\t\t## FIN Acion escrita en acciones.nameact\n"""
                    tmpfile="/tmp/codigoaccion2.py"
                    codigotxt = str(filecred)
                    f= open(tmpfile,"w+")
                    f.write(codigotxt)
                    f.close()
            destact="../" + dirrasatrain + "/actions.py"
            copyfile(tmpfile, destact)
            time.sleep(15)



            recargaactions = os.system("../bin/rasarestart.sh odoorasa " + puertorasa + " " + puertorasax + " " + passwordx + " " + dirrasatrain + " > /tmp/rasa.log 2>&1 &")
            recargaactions = os.system("../bin/runactions.sh odoorasa " + dirrasatrain + " > /tmp/rasarunactions.log 2>&1 &")
            return True
        except:
            raise UserError(_('EL rasa NO responde Correctamente. Es posible que hayas cometido algun error en la Edicion de los Ficheros o no esté habilitado ningun contenido. Por favor Revisalos'))


    @api.depends('readfiles')
    def recargar_actions(self, default=None):
        
              
            ## CREAMOS EL APIDATA
            dondeestoy = os.getcwd()
            dirrasatrain = self.direccionagente
            
            apiimport ="import xmlrpc.client\n"
            apiurl = "\nurl = \"http://localhost:8069\"\n"
            apiusername = "username = \"" + str(self.apiusername) + "\"\n"
            apipassword = "pwd = \"" + str(self.apipassword) + "\"\n"
            apibbdd = "dbname = \"" + str(self.apibbdd) + "\"\n"
            datoscomunes = """sock_common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) \nuid = sock_common.login(dbname, username, pwd) \nmodels = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url)) \n"""
            todapicon = "\n## Datos de Conexion API\n" + apiimport + "\n" + apiurl + apiusername + apipassword + apibbdd + datoscomunes + "\n"

            tmpfile="/tmp/apidata.py"
            destact="../" + dirrasatrain + "/apidata.py"
            codigotxt = str(todapicon)
            f= open(tmpfile,"w+")
            f.write(codigotxt)
            f.close()
            copyfile(tmpfile, destact)
            time.sleep(2)

 
            ## FUNCIONES
            dondeestoy = os.getcwd()
            dirrasatrain = self.direccionagente
            ## Leer Fichero Cabecera
            file = open(dondeestoy + "/addons/pyme_rasa/data/cabecera_functions.txt", "r") 
            filecred = file.read() 
            for acciones in self.funciones:
                if acciones.state == "online":
                    filecredx = """\n## Funcion escrita desde ODOO \n"""
                    filecred = filecred + filecredx
                    for line in acciones.codigo.splitlines():
                        line = "" + line + "\n"
                        filecred = filecred + line
                    filecred = filecred + """\n## FIN Acion escrita en Funciones \n"""
                    tmpfile="/tmp/codigoaccion2_func.py"
                    codigotxt = str(filecred)
                    f= open(tmpfile,"w+", encoding="utf-8")
                    f.write(codigotxt)
                    f.close()
            destact="../" + dirrasatrain + "/functions.py"
            copyfile(tmpfile, destact)
            time.sleep(2)

            dondeestoy = os.getcwd()
            dirrasatrain = self.direccionagente
            ## Leer Fichero Cabecera
            file = open(dondeestoy + "/addons/pyme_rasa/data/cabecera_actions.txt", "r") 
            filecred = file.read() 
            for acciones in self.acciones:
                if acciones.state == "online":
                    filecredx = """\n\nclass Action""" + acciones.nameact +  """(Action):\n\tdef name(self) -> Text:\n\t\treturn \"action_""" + acciones.nameact +  """\"\n\tdef run(self, dispatcher: CollectingDispatcher,\n\t\ttracker: Tracker,\n\t\tdomain: Dict[Text, Any]) -> List[Dict[Text, Any]]:"""
                    filecredx = filecredx + """\n\n\t\t## Acion escrita en acciones.nameact\n"""
                    filecred = filecred + filecredx
                    for line in acciones.codigo.splitlines():
                        line = "\t\t " + line + "\n"
                        filecred = filecred + line
                    filecred = filecred + """\n\t\t return []\n"""
                    filecred = filecred + """\n\t\t## FIN Acion escrita en acciones.nameact\n"""
                    tmpfile="/tmp/codigoaccion2.py"
                    codigotxt = str(filecred)
                    f= open(tmpfile,"w+", encoding="utf-8")
                    f.write(codigotxt)
                    f.close()
            destact="../" + dirrasatrain + "/actions.py"
            copyfile(tmpfile, destact)
            time.sleep(20)

            recargaactions = os.system("../bin/runactions.sh odoorasa " + dirrasatrain + " > /tmp/rasarunactions.log 2>&1 &")
            return True
        
   
                
    @api.depends('readfiles')
    def applyactions(self, default=None):
        
        ## CREAMOS EL APIDATA
        dondeestoy = os.getcwd()
        dirrasatrain = self.direccionagente
            
        apiimport ="import xmlrpc.client\n"
        apiurl = "\nurl = \"http://localhost:8069\"\n"
        apiusername = "username = \"" + str(self.apiusername) + "\"\n"
        apipassword = "pwd = \"" + str(self.apipassword) + "\"\n"
        apibbdd = "dbname = \"" + str(self.apibbdd) + "\"\n"
        datoscomunes = """sock_common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) \nuid = sock_common.login(dbname, username, pwd) \nmodels = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url)) \n"""
        todapicon = "\n## Datos de Conexion API\n" + apiimport + "\n" + apiurl + apiusername + apipassword + apibbdd + datoscomunes + "\n"

        tmpfile="/tmp/apidata.py"
        destact="../" + dirrasatrain + "/apidata.py"
        codigotxt = str(todapicon)
        f= open(tmpfile,"w+")
        f.write(codigotxt)
        f.close()
        copyfile(tmpfile, destact)
        time.sleep(2)

        
        
        dondeestoy = os.getcwd()
        dirrasatrain = self.direccionagente
        ## Leer Fichero Cabecera
        file = open(dondeestoy + "/addons/pyme_rasa/data/cabecera_actions.txt", "r") 
        filecred = file.read() 
        for acciones in self.acciones:
            if acciones.state == "online":
                ## raise UserError(_('' + str(acciones.name) + ''))
                ## Leememos la variable de esta accion
                filecredx = """\n\nclass Action""" + acciones.nameact +  """(Action):\n\tdef name(self) -> Text:\n\t\treturn \"action_""" + acciones.nameact +  """\"\n\tdef run(self, dispatcher: CollectingDispatcher,\n\t\ttracker: Tracker,\n\t\tdomain: Dict[Text, Any]) -> List[Dict[Text, Any]]:"""
                filecredx = filecredx + """\n\n\t\t## Acion escrita en acciones.nameact\n"""
                filecred = filecred + filecredx
                for line in acciones.codigo.splitlines():
                    line = "\t\t " + line + "\n"
                    filecred = filecred + line
                filecred = filecred + """\n\t\t return []\n"""
                filecred = filecred + """\n\t\t## FIN Acion escrita en acciones.nameact\n"""
                tmpfile="/tmp/codigoaccion2.py"
                codigotxt = str(filecred)
                f= open(tmpfile,"w+")
                f.write(codigotxt)
                f.close()
        destact="../" + dirrasatrain + "/actions.py"
        copyfile(tmpfile, destact)
        time.sleep(15)

        raise UserError(_('Se han aplicado los Cambios en el RASA'))

