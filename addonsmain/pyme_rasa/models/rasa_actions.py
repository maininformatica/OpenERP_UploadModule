#

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


class RasaAcciones(models.Model):

    _name = "rasa.actions"
    _description = "Rasa Server Actions"
    _order = "sequence, id desc"

    name = fields.Char(string="Descripcion")
    nameact = fields.Char(string="Nombre Accion")
    codigo = fields.Text(string="Codigo")
    relact = fields.Many2one("rasa.server", string="Relacion Rasa Server")
    sequence = fields.Integer(string="Sequence", default=10)
    image_url = fields.Char(string="Url")
    img_attach = fields.Html('Image Html')
    img_attachsrc = fields.Char('Image Html')
    state = fields.Selection([
       ("draft", "Borrador / NO aplicado"),
       ("online", "Online"),
       ("error", "Error"),
       ("cancel", "Cancelado"),
       ], string='Status', copy=False, readonly=True, index=True, track_visibility='onchange', track_sequence=3, default='draft')


    @api.onchange('image_url')
    def onchange_image_url(self):
         if self.image_url:
             self.img_attach = '<image id="img" src="' + str(self.image_url) + '"/>'
             self.img_attachsrc= '<iframe id="img" src="' + str(self.image_url) + '"/>'


    
    
    
    @api.multi
    def testfile(self, default=None):
        
        dondeestoy = os.getcwd()
        ## file = open(dondeestoy + "/addons/pyme_rasa/data/cabecera_actions.py", "r") 
        ## filecred = file.read() 
        
        ### Escribo Accion Temporal
        tmpfile="/tmp/codigoaccion.py"
        codigotxt = str(self.codigo)
        f= open(tmpfile,"w+")
        f.write(codigotxt)
        f.close() 


        raise UserError(_('' + str(codigotxt) + ''))
        
    @api.depends('readfiles')
    def applycontenido(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'online'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return


    @api.depends('readfiles')
    def cancelacontenido(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'cancel'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return

    @api.depends('readfiles')
    def vueleveborrador(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'draft'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return


class RasaCredentials(models.Model):

    _name = "rasa.credentials"
    _description = "Rasa Server Credentials"
    _order = "sequence, id desc"

    name = fields.Char(string="Descripcion")
    nameact = fields.Char(string="Nombre Credential")
    codigo = fields.Text(string="Codigo")
    relcred = fields.Many2one("rasa.server", string="Relacion Rasa Server")
    sequence = fields.Integer(string="Sequence", default=10)
    state = fields.Selection([
       ("draft", "Borrador / NO aplicado"),
       ("online", "Online"),
       ("error", "Error"),
       ("cancel", "Cancelado"),
       ], string='Status', copy=False, readonly=True, index=True, track_visibility='onchange', track_sequence=3, default='draft')


    @api.depends('readfiles')
    def applycontenido(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'online'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return


    @api.depends('readfiles')
    def cancelacontenido(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'cancel'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return

    @api.depends('readfiles')
    def vueleveborrador(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'draft'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return





class RasaEndpoints(models.Model):

    _name = "rasa.endpoints"
    _description = "Rasa Server Endpoints"
    _order = "sequence, id desc"

    name = fields.Char(string="Descripcion")
    nameact = fields.Char(string="Nombre Endpoint")
    codigo = fields.Text(string="Codigo")
    relendp = fields.Many2one("rasa.server", string="Relacion Rasa Server")
    sequence = fields.Integer(string="Sequence", default=10)
    state = fields.Selection([
       ("draft", "Borrador / NO aplicado"),
       ("online", "Online"),
       ("error", "Error"),
       ("cancel", "Cancelado"),
       ], string='Status', copy=False, readonly=True, index=True, track_visibility='onchange', track_sequence=3, default='draft')


    @api.depends('readfiles')
    def applycontenido(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'online'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return


    @api.depends('readfiles')
    def cancelacontenido(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'cancel'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return

    @api.depends('readfiles')
    def vueleveborrador(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'draft'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return


class RasaFunctions(models.Model):

    _name = "rasa.functions"
    _description = "Rasa Server Funciones"
    _order = "sequence, id desc"

    name = fields.Char(string="Descripcion")
    nameact = fields.Char(string="Nombre Funcion")
    codigo = fields.Text(string="Codigo")
    relfunc = fields.Many2one("rasa.server", string="Relacion Rasa Server")
    sequence = fields.Integer(string="Sequence", default=10)
    state = fields.Selection([
       ("draft", "Borrador / NO aplicado"),
       ("online", "Online"),
       ("error", "Error"),
       ("cancel", "Cancelado"),
       ], string='Status', copy=False, readonly=True, index=True, track_visibility='onchange', track_sequence=3, default='draft')


    @api.depends('readfiles')
    def applycontenido(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'online'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return


    @api.depends('readfiles')
    def cancelacontenido(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'cancel'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return

    @api.depends('readfiles')
    def vueleveborrador(self, default=None):
        dondeestoy = os.getcwd()
        self.write({'state': 'draft'})


        ## raise UserError(_('' + str(filecred) + ''))
        
        return
