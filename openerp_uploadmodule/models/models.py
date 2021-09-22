# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import subprocess, time
import os, sys, shutil, zipfile

class UploadModuleWizard(models.Model):
     _name = 'openerp.uploadmodule'
     


     @api.multi
     @api.depends('app','datas_fname','gitfile')
     def _compute_name(self):
       nombre = ""
       for rec in self:
         datas_fname = rec.datas_fname  
         gitfile = rec.gitfile 
         uploadmode = rec.uploadmode
         if uploadmode == "file":
             nombre = datas_fname
         if uploadmode == "git":
             nombre = gitfile
         rec.source = nombre

     
     name  = fields.Char(string='Nombre')
     source  = fields.Char(string='Origen', compute='_compute_name')
     overwrite = fields.Boolean(string='Overwrite')
     app = fields.Many2one('ir.attachment', string='Archivo', attachment=True)
     datas_fname = fields.Char(string='Nombre', related='app.datas_fname')
     store_fname = fields.Char(string='Store Name', related='app.store_fname')
     mimetype = fields.Char(string='Tipo MIME', related='app.mimetype')
     state = fields.Selection([('init', 'Borrador'), ('done', 'OK'), ('error', 'Error')], string='Status', required=True, default="init")
     uploadmode = fields.Selection([('file', 'File Zip'), ('git', 'Git Clone')], string='Tipo Origen', required=True, default="file")
     gitfile  = fields.Char(string='Git Clone URL')

     @api.multi
     def uploadapp(self):
       iddoc = self.id
       nombre = self.name
       view_id = self.env['ir.ui.view'].search([('model','=','ir.attachment'),('name', '=', 'view_appattachment_form')], limit=1).id
       ## raise AccessError("La vista es: " + str(view_id) + "")
       view = {
          'name': _('Adjuntar Archivo'),
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'ir.attachment',
          'view_id': view_id,
          'type': 'ir.actions.act_window',
          'context': {'default_name': nombre},
          'target': 'new',
          'res_id': False }
       return view

     @api.multi
     def unlink(self):
         iddoc = self.id
         state = self.state
         if str(state) == "done":
            raise AccessError("You can only delete entries in draft status.")
         unlink = super(UploadModuleWizard, self.with_context(mail_create_nosubscribe=True)).unlink()
         return unlink


     @api.multi
     def update_module(self):
         notif = self.pool.get('base.module.update').update_module(self)


     @api.multi
     def testzip(self,dst):
           ## dst = "/tmp/tmpapp.zip"
           targetdirtmp = "/tmp/1/"
           args = ["/usr/bin/rm", str(targetdirtmp), "-rf"]
           subprocess.call(args)
           zip = zipfile.ZipFile(dst)
           ziplist = zip.namelist()
           if "__manifest__.py" not in str(ziplist):
              raise AccessError("El Fichero No contiene El Documento de Manifiesto y/o es inválido")
              return False
           try:
             zip_ref = zipfile.ZipFile(str(dst),"r")
             unzip = zip_ref.extractall(str(targetdirtmp))
             dirppal = os.listdir(str(targetdirtmp))[0]
             ficheros = os.listdir(str(targetdirtmp) + "/" + str(dirppal))
             if "__manifest__.py" not in str(ficheros):
               raise AccessError("El Fichero de Configuración del Módulo NO esta en la Raiz del Modulo: " + str(dirppal) + "")
               return False
             lines = ""
             with open(str(targetdirtmp) + "/" + str(dirppal) + "/__manifest__.py") as f:
                lines = f.readlines()
                lines = str(lines).replace('\"','\'')
             ### if "version" in str(lines):
             ###    if "12." not in str(lines):
             ###      raise AccessError("La versión del Módulo no es correcta: \n" + str(lines))
             ###      return False
           except:
             raise AccessError("El archivo Seleccionado No contiene la estructura válida de módulo de ODOO. No se Puede Importar")
           return True


     @api.multi
     def cancel(self):
         iddoc = self.id
         self.write({'state': 'init'})


     @api.multi
     def setdone(self):
         iddoc = self.id
         self.write({'state': 'done'})


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
           datadir = "/opt/openerp/data/share/Odoo"
           bbdd = self.env.cr.dbname
           src = str(datadir) + "/filestore/" + str(bbdd) + "/" + str(store_fname)
           dst = "/tmp/tmpapp.zip"
           ifisfile = os.path.isfile(str(dst))
           if str(ifisfile) == "True":
               deletefile = os.remove(str(dst))
           targetdir = "/opt/openerp/openerp/addons/"
           shutil.copyfile(src, dst)
           zip_ref = zipfile.ZipFile(str(dst),"r")
           testzip = self.testzip(dst)
           if str(testzip) != "True":
              raise AccessError("El Fichero ZIP No es válido")
           unzip = zip_ref.extractall(str(targetdir))
           with zipfile.ZipFile(str(dst),"r") as zip_ref:
               zip_ref.extractall(str(targetdir))
        if str(uploadmode) == "git":
           ## raise AccessError("git clone --branch 12.0 " + str(gitfile) + "")
           iddoc = self.id
           dirtmp = "/tmp/gitapp" + str(iddoc) + "/"
           ## raise AccessError("El directorio es: " + str(dirtmp) + "")
           args = ["/usr/bin/rm", str(dirtmp), "-rf"]
           subprocess.call(args)
           path = "/opt/openerp/oca/addons/"
           try: 
              os.mkdir(path);
           except:
              print("Ya creado")
           args = ["/usr/bin/git", "clone", str(gitfile), str(dirtmp) + "/"]
           subprocess.call(args)
           time.sleep(3)
           destination = os.system("cp -rf " + str(dirtmp) + "/* " + str(path) + "")
           ## destination = shutil.copytree(str(dirtmp),  str(path), copy_function = shutil.copy) 
           ## args = ["/usr/bin/cp", str(dirtmp), str(path) + "-ru"]
           ## subprocess.call(args)



        notif = self.pool.get('base.module.update').update_module(self)
        menu = self.env['ir.ui.menu'].search([('parent_id', '=', False)])[:1]
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id},
        }
        ## raise AccessError("Estas cargando: " + str(store_fname) + ".\n Overwrite: " + str(overwrite) + "")