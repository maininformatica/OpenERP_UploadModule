# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import subprocess
import os, sys

class PartnerNews(models.Model):
     _name = 'openerp.uploadmodule'
     
     
     name  = fields.Char(string='Nombre')
     overwrite = fields.Boolean(string='Overwrite')
     app = fields.Many2one('ir.attachment', string='Select Zip File', attachment=True)
     datas_fname = fields.Char(string='Nombre', related='app.datas_fname')
     store_fname = fields.Char(string='Store Name', related='app.store_fname')
     mimetype = fields.Char(string='Tipo MIME', related='app.mimetype')
     state = fields.Selection([('init', 'Draft'), ('done', 'Done'), ('error', 'Error')], string='State', required=True, default="init" ,help="Determines the application load status for installation.")
     uploadmode = fields.Selection([('file', 'File Zip'), ('git', 'Git Clone')], string='Upload Mode', required=True, default="file" ,help="Determines the Model load for APP.")
     gitfile  = fields.Char(string='Git Clone Link')


     @api.multi
     @api.onchange('app','uploadmode','gitfile')
     def on_change_app(self):
         datas_fname = self.datas_fname  
         gitfile = self.gitfile 
         uploadmode = self.uploadmode
         if uploadmode == "file":
             nombre = datas_fname
         if uploadmode == "git":
             nombre = gitfile
         self.name = nombre


     @api.multi
     def app_install(self):
        self.ensure_one()
        file = self.app
        overwrite = self.overwrite
        store_fname = self.store_fname
        mimetype = self.mimetype
        uploadmode = self.uploadmode
        gitfile = self.gitfile 

        ## Upload Mode
        if str(uploadmode) == "file":
           if str(mimetype) != "application/zip":
              raise AccessError("Invalid Format. Only ZIP Files")
        if str(uploadmode) == "git":
           ## raise AccessError("git clone --branch 12.0 " + str(gitfile) + "")
           path = "/tmp/2"
           try: 
              os.mkdir(path);
           except:
              print("Ya creado")
           args = ["/usr/bin/git", "clone", str(gitfile), str(path) + "/"]
           subprocess.call(args)


        raise AccessError("Estas cargando: " + str(store_fname) + ".\n Overwrite: " + str(overwrite) + "")