# -*- coding: utf-8 -*-

import logging
import poplib
from imaplib import IMAP4, IMAP4_SSL
from poplib import POP3, POP3_SSL
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from uuid import uuid4

_logger = logging.getLogger(__name__)
MAX_POP_MESSAGES = 50
MAIL_TIMEOUT = 60


class EmailEtiquetas(models.Model):
    _name = 'mail.message.etiquetas'
    name = fields.Char(string='Nombre')





class EmailRecepcionBorrar(models.Model):
    _name = 'mail.message.delete'
    name = fields.Char(string='¿Deseas Borrar Estos Correos?')
    mails_ids = fields.Many2many('mail.message', string='Lista de Correos')



    def _default_active_ids(self):
        return self.env['mail.message.delete'].browse(self._context.get('active_ids'))

    @api.multi
    def wizard_method(self):
        self.ensure_one()
        mails_ids = self.env['mail.message'].browse(self._context.get('active_ids'))
        for mails_id in mails_ids:
            print ("La relación es: " + str(mails_id.relacion.name) + " y el mail: " + str(mails_id.id))            
            if str(mails_id.relacion.name) != "False": 
               raise AccessError("No se Puede Eliminar este correo porque tiene un documento relacionado")
            else:
               mails_id.write({'borrado': True})




class EmailEnviosBorrar(models.Model):
    _name = 'mail.mail.delete'
    name = fields.Char(string='¿Deseas Borrar Estos Correos?')
    mails_ids = fields.Many2many('mail.mail', string='Lista de Correos')



    def _default_active_ids(self):
        return self.env['mail.mail.delete'].browse(self._context.get('active_ids'))

    @api.multi
    def wizard_method(self):
        self.ensure_one()
        mails_ids = self.env['mail.mail'].browse(self._context.get('active_ids'))
        for mails_id in mails_ids:
            print ("mail: " + str(mails_id.id))            
            mails_id.write({'borrado': True})


class EmailEnvios(models.Model):
    _inherit = "mail.mail"

    usuario = fields.Many2one('res.users', string='Usuario')
    firma = fields.Html(string='Firma', related='usuario.signature', store=True)
    borrado  = fields.Boolean(string='Eliminado')
    email_bcc  = fields.Char(string='Cco')


    @api.multi
    @api.onchange('message_type')
    def on_change_message_type(self):
         body_html = self.body_html         
         body = self.body
         self.usuario = self.env.user.id
         firma = self.firma
         if str(body) == "False":
             body = ""
         if str(body_html) == "False":
             body_html = ""
         body = str(body) + "<br>" + str(firma)
         body_html = str(body_html) + "<br>" + str(firma)
         self.body_html = body_html
         self.body = body
         return {}


    @api.model
    def create(self, values):
        usuario = self.env.user.id
        # notification field: if not set, set if mail comes from an existing mail.message
        values['usuario'] = usuario
        if 'notification' not in values and values.get('mail_message_id'):
            values['notification'] = True
        new_mail = super(EmailEnvios, self).create(values)
        if values.get('attachment_ids'):
            new_mail.attachment_ids.check(mode='read')
        return new_mail


    def borrar(self):  
       usuario = self.env.user.id
       idcorreo = self.id
       self.write({'borrado': True})
       self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%Emials Salientes%' and type='tree' ORDER BY id DESC LIMIT 1""")
       result = self.env.cr.fetchone()
       record_id = int(result[0])
       view = {
          'name': _('Emails Enviados'),
          'view_type': 'form',
          'view_mode': 'tree',
          'res_model': 'mail.mail',
          'view_id': record_id,
          'type': 'ir.actions.act_window',
          'domain': "[('borrado','!=',True)]",
          'target': 'current',
          'res_id': False }
       return view    

    def reenviar(self):  
       resultado = "Enviando Email: \n" 
       usuario = self.env.user.id
       idmail = self.id
       email_from = self.email_from
       attachment_ids = self.attachment_ids
       subject = "RV: " + self.subject
       body = self.body
       recipient_ids = self.author_id
       mailline_obj = self.env['mail.mail']
       self.ensure_one()
       self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%Emials Salientes%' and type='form' ORDER BY id DESC LIMIT 1""")
       result = self.env.cr.fetchone()
       record_id = int(result[0])
       invoice = mailline_obj.create({
          'usuario': usuario,
          'body': body,
          'body_html': body,
          'attachment_ids': attachment_ids,
          'recipient_ids': recipient_ids,
          'subject': subject})
       for attch_id in attachment_ids:
           adj_data = self.attch_id.datas
           maillineatch_obj = self.env['mail.mail']           
           resultado =  'mail.mail_' + str(invoice.id) + '\n',
           attch_create = maillineatch_obj.create({
                      'res_model': 'mail.mail',
                      'res_id': invoice.id,
                      'datas': datas})           
       raise UserError(str(resultado))    
       view = {
          'name': _('Reenviar Correo'),
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'mail.mail',
          'view_id': record_id,
          'type': 'ir.actions.act_window',
          'target': 'new',
          'res_id': invoice.id }
       return view        


class Clasificar(models.Model):
    _name = 'mail.clasificar'
	
    name = fields.Char(string='Descripcion')
    model = fields.Many2one('ir.model')



class Seguimiento(models.Model):
    _name = 'pyme.seguimiento'
	
    name = fields.Char(string='Descripción')
    name_destino = fields.Char(string='Destino')
    model_origen = fields.Many2one('ir.model', string='Modelo Origen')
    model_name_origen = fields.Char(string='Modelo Origen')
    res_origen = fields.Integer(string='Id Origen')
    model_destino = fields.Many2one('ir.model', string='Modelo Destino')
    model_name_destino = fields.Char(string='Modelo Origen')
    res_destino = fields.Integer(string='Id Destino')
    mail_message = fields.Many2one('mail.message', string='Modelo Destino')
    res_id = fields.Integer(string='Id Origen')
    model = fields.Char(string='Modelo')


    @api.multi
    def action_open(self):
        idres = self.res_id        	
        idmodel = self.model
        view = {
          'name': _('Documento Relacionado'),
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': str(idmodel),
          'view_id': False,
          'type': 'ir.actions.act_window',
          'target': 'current',
          'res_id': idres }
        return view  

	

class MailMessageCustom(models.Model):
	_inherit = "mail.message"



	def _compute_total_weight(self):
		relname = False
		relacionstr2 = "NADA"
		for rec in self:
		   relname = rec.rel_id
		   ### print("\n\n La rel es: " + str(relname) + "\n\n")
		   if relname == False:
		      relname = ""
		      relacionstr2 = ""
		   if str(relname) == "project.task":
		      relacionstr2 = "Tarea"
		   if str(relname) == "helpdesk_lite.ticket":
		      relacionstr2 = "Ticket"
		   rec.relacionstr2 = str(relacionstr2)
		## return str(relacionstr2)



	bandejaentrada = fields.Many2one('fetchmail.server', string='Bandeja de Entrada', readonly=True)
	usuarios_ids = fields.Many2many('res.users',string='Usuarios', help='Selecciona los Uusarios que pueden leer este correo', related='bandejaentrada.usuarios_ids',  readonly=True)
	etiquetas = fields.Many2many('mail.message.etiquetas', string='Etiquetas')
	destacar = fields.Boolean(string='Destacar')
	procesado = fields.Boolean(string='Procesado')
	procesado_por = fields.Many2one('res.users', string='Quien lo Procesa')
	procesado_cuando = fields.Datetime(string='Cuando se Procesa')
	procesado_des = fields.Boolean(string='Quita Procesado')
	relacion = fields.Many2one('mail.clasificar', string='Relación')
	relsel  = fields.Boolean(string='RelSel')
	rel_id = fields.Char(string='Relación Name')
	relacionstr  = fields.Char(string='Relación')
	relacionstr2  = fields.Char(string='Relación', compute='_compute_total_weight')
	tareas = fields.Many2one('project.task', string='Tareas')
	ticket = fields.Many2one('helpdesk_lite.ticket', string='Tickets')
	clientes = fields.Many2one('res.partner', string='Clientes')
	seguimiento_id = fields.One2many('pyme.seguimiento', 'mail_message', string='Seguimiento')
	borrado  = fields.Boolean(string='Eliminado')



	@api.onchange('relacion')
	def _onchange_relacion(self):
		usuario = self.env.user.id
		rel = self.relacion.id
		relname = self.relacion.model.model
		## print("\n\n La relacion es: " + str(relname) + "\n\n")
		if relname == False:
		   relname = ""
		   relacionstr = ""
		if str(relname) == "project.task":
		   relacionstr = "Tarea"
		if str(relname) == "helpdesk_lite.ticket":
		   relacionstr = "Ticket"
		self.rel_id = str(relname)
		self.relacionstr = str(relacionstr)


	@api.onchange('tareas','ticket')
	def _onchange_relsel(self):
		id = self.id
		tareas = self.tareas.id
		tareasname = self.tareas.name
		ticket = self.ticket.id
		ticketname = self.ticket.name        
		print(str(tareas) + " :: " + str(ticket) + " == " + str(tareasname) + " :: " + str(ticketname))
		if str(tareas) == "False" and str(ticket) == "False":
				self.relsel = False
		else:
				self.relsel = True

	@api.multi
	def elimina_relacion(self):
		for tareas in self.tareas:
			for seguimiento in tareas.seguimiento_id:
				if seguimiento:
				   seguimiento.unlink()
		for ticket in self.ticket:
			for seguimiento in ticket.seguimiento_id:
				if seguimiento:
				   seguimiento.unlink()
		self.write2({'relsel': False,'rel_id': False,'relacion': False,'tareas': False,'ticket': False,'procesado': False,'procesado_por':False,'procesado_cuando':False})

		return {}


	@api.multi
	def write2(self, vals):
	    if 'model' in vals or 'res_id' in vals:
	 	    self._invalidate_documents()
	    res = super(MailMessageCustom, self).write(vals)
	    if vals.get('attachment_ids'):
	 	    for mail in self:
	 	       mail.attachment_ids.check(mode='read')
	    if 'notification_ids' in vals or 'model' in vals or 'res_id' in vals:
	 	    self._invalidate_documents()
	    return res

	@api.multi
	def write(self, vals):
	    usuario = self.env.user.id
	    relacionstr = vals.get('res_id')
	    procesado_des = self.procesado_des
	    ## print("\n\n Esto Hay: " + str(procesado_des) + " :: " + str(self.relacion.name) + " " + str(self.tareas.id) + " " + str(self.ticket.id) + "\n\n")
	    if 'model' in vals or 'res_id' in vals:
	 	    self._invalidate_documents()

	    if procesado_des != True:
	        ## print("\n\n\n PASO POR AQUI \n\n\n")
	        vals['procesado'] = True
	        vals['procesado_por'] = usuario
	        vals['procesado_cuando'] = fields.Datetime.now()
	        vals['procesado_des'] = False
	    else:
	        vals['procesado'] = False
	        vals['procesado_por'] = False
	        vals['procesado_cuando'] = False
	        vals['procesado_des'] = False

	    res = super(MailMessageCustom, self).write(vals)




	    if vals.get('attachment_ids'):
	 	    for mail in self:
	 	       mail.attachment_ids.check(mode='read')
	    if 'notification_ids' in vals or 'model' in vals or 'res_id' in vals:
	 	    self._invalidate_documents()

	    for task in self.tareas:
	       for seguimiento in task.seguimiento_id:
	           seguimiento.unlink()
	       asuntoticket = self.subject
	       seguimiento_obj = self.env['pyme.seguimiento']
	       seguimiento2 = seguimiento_obj.create({
	          'name': "Email: " + str(asuntoticket),
	          'name_destino': "Tarea: " + str(asuntoticket),
	          'model_name_origen': 'mail.message',
	          'res_origen': self.id,
	          'model_name_destino': 'project.task', 
	          'model': 'mail.message', 
	          'res_id': self.id,
	          'mail_message': self.id,
	          'project_task': task.id,
	          'res_destino': task.id})


	    for ticket in self.ticket:
	       for seguimiento in ticket.seguimiento_id:
	           seguimiento.unlink()
	       asuntoticket = self.subject
	       seguimiento_obj = self.env['pyme.seguimiento']
	       seguimiento2 = seguimiento_obj.create({
	              'name': "Email: " + str(asuntoticket),
	              'name_destino': "Ticket: #" + str(ticket.id) + " :: " + str(asuntoticket),
	              'model_name_origen': 'mail.message',
	              'res_origen': self.id,
	              'model_name_destino': 'helpdesk_lite.ticket',
	              'model': 'mail.message', 
	              'res_id': self.id,
	              'mail_message': self.id,
	              'helpdesk_ticket': ticket.id,
	              'res_destino': ticket.id})
               

	    return res




	@api.multi
	def borrar(self):  
		usuario = self.env.user.id
		idcorreo = self.id
		if str(self.relacion.name) != "False": 
				raise AccessError("No se Puede Eliminar este correo porque tiene un documento relacionado")
		else:
				self.write({'borrado': True})
		self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%Emials Entrantes%' and type='tree' ORDER BY id DESC LIMIT 1""")
		result = self.env.cr.fetchone()
		record_id = int(result[0])
		view = {
				'name': _('Emails Entrantes'),
				'view_type': 'form',
				'view_mode': 'tree',
				'res_model': 'mail.message',
				'view_id': record_id,
				'type': 'ir.actions.act_window',
				'domain': "[('message_type','=','email'),('model','=','pyme.mail.channel'),('usuarios_ids','in', uid),('borrado','!=',True)]",
				'target': 'current',
				'res_id': False }
		return view 

	@api.multi
	def button_procesado(self):
		idmail = self.id
		usuario = self.env.user.id
		procesado = self.procesado
		if str(procesado) == "True":
			self.write2({'procesado':False,'procesado_des':False})
		else:
			self.write2({'procesado':True,'procesado_por':usuario,'procesado_cuando':fields.Datetime.now()})
		return {}


	@api.multi
	def seleccionar_tarea(self):  
	   for rec in self:
	      rec.write({'tareas': rec.tareas.id})

	@api.multi
	def crear_tarea(self):  
	   idmail = self.id
	   asuntoticket = self.subject
	   usuario = self.env.user.id
	   description = self.body
	   partner_id = self.author_id.id
	   email_from = ""
	   if partner_id != False:
	   	   email_from = self.env['res.partner'].search([('id', '=', partner_id )]).email
	   task_obj = self.env['project.task']
	   task = task_obj.create({
	      'name': str(asuntoticket),
	      'partner_id': partner_id,
	      'email_from': email_from,
	      'email_entrante': idmail, 
	      'description': description})
	   seguimiento_obj = self.env['pyme.seguimiento']
	   seguimiento = seguimiento_obj.create({
	      'name': "Email: " + str(asuntoticket),
	      'name_destino': "Tarea: " + str(asuntoticket),
	      'model_name_origen': 'mail.message',
	      'res_origen': self.id,
	      'model_name_destino': 'project.task', 
	      'model': 'mail.message', 
	      'res_id': self.id,
	      'mail_message': self.id,
	      'project_task': task.id,
	      'res_destino': task.id})
	   self.write({'tareas': task.id, 'procesado': True, 'procesado_por': usuario,'procesado_cuando':fields.Datetime.now()})
	   ## view_id = self.env['ir.ui.view'].search([('name', '=', 'Tareas-Popup' )]).id
	   view = {
	      'name': _('Crear Nueva Tarea'),
	      'view_type': 'form',
	      'view_mode': 'form',
	      'res_model': 'project.task',
	      'type': 'ir.actions.act_window',
	      'target': 'current',
	      'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
	      ## 'view_id': view_id,
	      'res_id': task.id }
	   return view        



	@api.multi
	def crear_tarea_tmp(self):  
	   idmail = self.id
	   asuntoticket = self.subject
	   usuario = self.env.user.id
	   description = self.body
	   partner_id = self.author_id.id
	   email_from = ""
	   if partner_id != False:
	   	   email_from = self.env['res.partner'].search([('id', '=', partner_id )]).email
	   view = {
	      'name': _('Crear Nueva Tarea'),
	      'view_type': 'form',
	      'view_mode': 'form',
	      'res_model': 'project.task',
	      'type': 'ir.actions.act_window',
	      'target': 'current',
	      'context': {'default_name': asuntoticket,'default_description': description,'default_user_id':usuario,'default_partner_id': partner_id,'default_email_entrante':idmail,'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},}
	   return view 



	@api.multi
	def seleccionar_ticket(self):  
	   for rec in self:
	      rec.write({'ticket': rec.ticket.id})


	@api.multi
	def crear_ticket(self):  
	   idmail = self.id
	   asuntoticket = self.subject
	   usuario = self.env.user.id
	   description = self.body
	   partner_id = self.author_id.id
	   email_from = ""
	   if partner_id != False:
	   	   email_from = self.env['res.partner'].search([('id', '=', partner_id )]).email
	   ticket_obj = self.env['helpdesk_lite.ticket']
	   ticket = ticket_obj.create({
	      'name': str(asuntoticket),
	      'partner_id': partner_id,
	      'email_from': email_from,
	      'email_entrante': idmail, 
	      'description': description})
	   seguimiento_obj = self.env['pyme.seguimiento']
	   seguimiento = seguimiento_obj.create({
	      'name': "Email: " + str(asuntoticket),
	      'name_destino': "Ticket: #" + str(ticket.id) + " :: " + str(asuntoticket),
	      'model_name_origen': 'mail.message',
	      'res_origen': self.id,
	      'model_name_destino': 'helpdesk_lite.ticket',
	      'model': 'mail.message', 
	      'res_id': self.id,
	      'mail_message': self.id,
	      'helpdesk_ticket': ticket.id,
	      'res_destino': ticket.id})
	   self.write({'ticket': ticket.id, 'procesado': True, 'procesado_por': usuario,'procesado_cuando':fields.Datetime.now()})
	   view = {
	      'name': _('Crear Nuevo Ticket'),
	      'view_type': 'form',
	      'view_mode': 'form',
	      'res_model': 'helpdesk_lite.ticket',
	      'type': 'ir.actions.act_window',
	      'target': 'current',
	      'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
	      'res_id': ticket.id }
	   return view        


	@api.multi
	def crear_ticket_tmp(self):  
	   idmail = self.id
	   asuntoticket = self.subject
	   usuario = self.env.user.id
	   description = self.body
	   partner_id = self.author_id.id
	   email_from = ""
	   if partner_id != False:
	   	   email_from = self.env['res.partner'].search([('id', '=', partner_id )]).email
	   view = {
	      'name': _('Crear Nuevo Ticket'),
	      'view_type': 'form',
	      'view_mode': 'form',
	      'res_model': 'helpdesk_lite.ticket',
	      'type': 'ir.actions.act_window',
	      'target': 'current',
	      'context': {'default_name': asuntoticket,'default_description': description,'default_user_id':usuario,'default_partner_id': partner_id,'default_email_entrante':idmail,'default_email_from':email_from,'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},}
	   return view        





	@api.multi
	def responder(self):  
	   idmail = self.id
	   usuario = self.env.user.id
	   email_from = self.email_from
	   subject = "RE: " + self.subject
	   body = self.body
	   ### raise UserError("El Body es: " + str(body) + ".")
	   recipient_ids = self.author_id
	   mailline_obj = self.env['mail.mail']
	   self.ensure_one()
	   self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%Emials Salientes%' and type='form' ORDER BY id DESC LIMIT 1""")
	   result = self.env.cr.fetchone()
	   record_id = int(result[0])
	   invoice = mailline_obj.create({
	      'usuario': usuario,
	      'body': body,
	      'body_html': body,
	      'recipient_ids': recipient_ids,
	      'email_to': email_from,
	      'subject': subject})
	   view = {
	      'name': _('Responder'),
	      'view_type': 'form',
	      'view_mode': 'form',
	      'res_model': 'mail.mail',
	      'view_id': record_id,
	      'type': 'ir.actions.act_window',
	      'target': 'new',
	      'res_id': invoice.id }
	   return view        

	def reenviar(self):  
	   resultado = "Reeviando Mensaje: \n"
	   idmail = self.id
	   usuario = self.env.user.id
	   email_from = self.email_from
	   attachment_ids = self.attachment_ids
	   subject = "RV: " + self.subject
	   body = self.body
	   ### raise UserError("El Body es: " + str(body) + ".")
	   recipient_ids = self.author_id
	   mailline_obj = self.env['mail.mail']
	   self.ensure_one()
	   self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%Emials Salientes%' and type='form' ORDER BY id DESC LIMIT 1""")
	   result = self.env.cr.fetchone()
	   record_id = int(result[0])
	   invoice = mailline_obj.create({
	      'usuario': usuario,
	      'body': body,
	      'body_html': body,
	      'recipient_ids': recipient_ids,
	      'subject': subject})
	   for attch_id in attachment_ids:
	   	   adj_id = attch_id.id
	   	   maillineatch_obj = self.env['mail.mail']           
	   	   resultado =  'mail.mail_' + str(invoice.id) + '\n',
	   	   self.env.cr.execute("INSERT INTO message_attachment_rel (message_id,attachment_id) VALUES ('" + str(invoice.mail_message_id.id) + "','" + str(adj_id) + "')")
	   view = {
	      'name': _('Reenviar Correo'),
	      'view_type': 'form',
	      'view_mode': 'form',
	      'res_model': 'mail.mail',
	      'view_id': record_id,
	      'type': 'ir.actions.act_window',
	      'target': 'new',
	      'res_id': invoice.id }
	   return view        
        

	def buscarcorreo(self):  
	   idmail = self.id
	   bandejaentrada_ids = self.bandejaentrada
	   for bandejaentrada_id in bandejaentrada_ids:
	   	   realizafetch = self.env['fetchmail.server'].fetch_mail()
	   	   ## print("Lanzado el FETCHMAIL para: " + str(bandejaentrada_id.id))            
	   return {}



class EmailPymeChannel(models.Model):

    _description = 'WEBMAIL Pyme'
    _name = 'pyme.mail.channel'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'name'


    name = fields.Char('Name')
    model = fields.Char('Modelo')
    model_id = fields.Many2one('fetchmail.server', string='Fetchmail')
    messsage_id = fields.Many2one('mail.message', string='MAIL')
    active = fields.Boolean('Active', default=True)

    @api.multi
    def write(self, vals):
        idchannel = self.id
        idmail = self.env['mail.message'].search([('res_id', '=', idchannel )], order='id desc', limit=1).id
        vals['model'] = "fetchmail.server"
        vals['messsage_id'] = idmail
        res = super(EmailPymeChannel, self).write(vals)

        ### notification_ids = [(0, 0, {'res_partner_id': 86}),(0, 0, {'res_partner_id': 3})]
        ### self.message_post(body='Nuevo Email recibido <a href=\"/web#action=169&model=mail.message&view_type=list\"> Aquí</a> ', message_type="notification", subtype="mail.mt_comment", 
        ###         author_id=3, 
        ###         notification_ids=notification_ids)


        return res

    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, parent_id=False, subtype=None, **kwargs):
        """ Temporary workaround to avoid spam. If someone replies on a channel
        through the 'Presentation Published' email, it should be considered as a
        note as we don't want all channel followers to be notified of this answer. """
        self.ensure_one()
        datos = self.env.ref('base.main_company')
        ### print("\n\n  Encontrado un Email " + str(datos) + "\n\n")
        if parent_id:
            parent_message = self.env['mail.message'].sudo().browse(parent_id)
            if parent_message.subtype_id and parent_message.subtype_id == self.env.ref('website_blog.mt_blog_blog_published'):
                if kwargs.get('subtype_id'):
                    kwargs['subtype_id'] = False
                subtype = 'mail.mt_note'


        res = super(EmailPymeChannel, self).message_post(parent_id=parent_id, subtype=subtype, **kwargs)
        return {}




class EmailFetchMail(models.Model):

    _inherit = 'fetchmail.server'
    _description = 'Incoming Mail Server'
    _order = 'priority'

    usuarios_ids = fields.Many2many('res.users',string='Usuarios', help='Selecciona los Uusarios que pueden leer este correo')

    @api.multi
    def fetch_mail(self):
        """ WARNING: meant for cron usage only - will commit() after each email! """
        additionnal_context = {
            'fetchmail_cron_running': True
        }
        MailThread = self.env['mail.thread']
        for server in self:
            _logger.info('start checking for new emails on %s server %s', server.type, server.name)
            additionnal_context['fetchmail_server_id'] = server.id
            additionnal_context['server_type'] = server.type
            count, failed = 0, 0
            imap_server = None
            pop_server = None
            if server.type == 'imap':
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    result, data = imap_server.search(None, '(UNSEEN)')
                    for num in data[0].split():
                        res_id = None
                        result, data = imap_server.fetch(num, '(RFC822)')
                        imap_server.store(num, '-FLAGS', '\\Seen')
                        try:
                            res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, data[0][1], save_original=server.original, strip_attachments=(not server.attach))
                        except Exception:
                            _logger.info('Failed to process mail from %s server %s.', server.type, server.name, exc_info=True)
                            failed += 1
                        imap_server.store(num, '+FLAGS', '\\Seen')
                        self._cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.type, server.name, (count - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.type, server.name, exc_info=True)
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
            elif server.type == 'pop':
                try:
                    while True:
                        pop_server = server.connect()
                        (num_messages, total_size) = pop_server.stat()
                        pop_server.list()
                        for num in range(1, min(MAX_POP_MESSAGES, num_messages) + 1):
                            (header, messages, octets) = pop_server.retr(num)
                            message = (b'\n').join(messages)
                            res_id = None
                            alias_model_id = 223
                            causa = ""
                            try:
                                partner_id = False
                                user_id = False
                                estado = False
                                asunto = False
                                email_from = False
                                res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, message, save_original=server.original, strip_attachments=(not server.attach))
                                modelwebmail = self.env['pyme.mail.channel'].search([('id', '=', int(res_id))])
                                message_ids = self.env['mail.message'].search([('res_id', '=', int(res_id)),('model','=','pyme.mail.channel')])
                                for message_id in message_ids:
                                   messageid = message_id.id
                                   estado = str(message_id.email_from)
                                   email_from = estado.replace('<','').replace('>','')
                                   asunto = str(message_id.subject)
                                   partner_id = message_id.author_id.id
                                   causa = "Email recibido desde: " + str(email_from) + " :: Asunto: " + str(message_id.subject) + ""
                                   message_id.write2({'bandejaentrada': self.id, 'procesado': False, 'procesado_cuando': False, 'procesado_por': False})
                                for webmail in modelwebmail:
                                    webmail.write({'model_id': self.id})
                                mensajecliente = "False"
                                mensajeusuario = "Recibido Nuevo Correo"
                                origen="WEBMAIL"
                                modo="create"
                                asignado = False
                                if str(email_from) != "False":
                                   for users in self.usuarios_ids:
                                      user_id = users.id
                                      ### print("\n\n ******************************** El Usuario es: " + str(user_id) + " y El partner ID: " + str(partner_id) + " y el from es: " + str(email_from) + "\n\n********************************************")
                                      notif = self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), self.id ,mensajeusuario ,mensajecliente, partner_id, user_id,causa,origen,modo,asignado,email_from,asunto)
                                if str(estado) != "False" and str(asunto) != "False":
                                  print("\n\n pyme_emails/models.py >> MAIL RECIBIDO Con Notificacion: " + str(notif) + "\n\n " + str(self.id) + " y ES UN ID: " + str(res_id) + " y MENSAJE: " + str(message_ids) + "\nFrom: " + str(email_from) + " Causa: " + str(causa) + "********************************************\n\n")
                                pop_server.dele(num)
                            except Exception:
                                _logger.info('Failed to process mail from %s server %s.', server.type, server.name, exc_info=True)
                                failed += 1
                            self.env.cr.commit()
                        if num_messages < MAX_POP_MESSAGES:
                            break
                        pop_server.quit()
                        _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", num_messages, server.type, server.name, (num_messages - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.type, server.name, exc_info=True)
                finally:
                    if pop_server:
                        pop_server.quit()
            server.write({'date': fields.Datetime.now()})
        return True





class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    def build_email(
            self, email_from, email_to, subject, body, email_cc=None,
            email_bcc=None, reply_to=False, attachments=None,
            message_id=None, references=None, object_id=False,
            subtype='plain', headers=None,
            body_alternative=None, subtype_alternative='plain'):
        if email_from:
            if email_bcc is None:
                email_bcc = [email_from]
            elif isinstance(email_bcc, list) and email_from not in email_bcc:
                email_bcc.append(email_from)
        return super(IrMailServer, self).build_email(
            email_from, email_to, subject, body, email_cc=email_cc,
            email_bcc=email_bcc, reply_to=reply_to, attachments=attachments,
            message_id=message_id, references=references, object_id=object_id,
            subtype=subtype, headers=headers,
            body_alternative=body_alternative,
            subtype_alternative=subtype_alternative)
  