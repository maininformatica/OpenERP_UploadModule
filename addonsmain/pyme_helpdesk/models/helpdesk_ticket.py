# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _
import re
from odoo.exceptions import AccessError, UserError

AVAILABLE_PRIORITIES = [
    ('0', 'Baja'),
    ('1', 'Normal'),
    ('2', 'Alta'),
    ('3', 'Urgente'),
]


class HelpdeskTicket(models.Model):
    _name = "helpdesk_lite.ticket"
    _description = "Helpdesk Tickets"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "priority desc, create_date desc"
    _mail_post_access = 'read'

    @api.model
    def _get_default_stage_id(self):
        return self.env['helpdesk_lite.stage'].search([], order='sequence', limit=1)

    name = fields.Char(string='Ticket', track_visibility='always', required=True)
    description = fields.Text('Notas Internas')
    partner_id = fields.Many2one('res.partner', string='Contacto', track_visibility='onchange', index=True)
    commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id', string='Compañia Cliente', store=True, index=True)
    contact_name = fields.Char('Nombre del Contacto')
    email_from = fields.Char('Email', help="Email Contacto", index=True)
    user_id = fields.Many2one('res.users', string='Asignado a', track_visibility='onchange', index=True, default=False)
    team_id = fields.Many2one('helpdesk_lite.team', string='Equipo de Soporte', track_visibility='onchange',
        default=lambda self: self.env['helpdesk_lite.team'].sudo()._get_default_team_id(user_id=self.env.uid),
        index=True, help='Al enviar correos, la dirección de correo electrónico predeterminada se toma del equipo de soporte')
    date_deadline = fields.Datetime(string='Fecha Límite', track_visibility='onchange')
    date_done = fields.Datetime(string='Finalizado', track_visibility='onchange')
    tipo_etiquetas = fields.Many2many('helpdesk_lite.etiquetas', string='Etiquetas')
    stage_id = fields.Many2one('helpdesk_lite.stage', string='Estado', index=True, track_visibility='onchange',
                               domain="[]",
                               copy=False,
                               group_expand='_read_group_stage_ids',
                               default=_get_default_stage_id)
    priority = fields.Selection(AVAILABLE_PRIORITIES, 'Prioridad', index=True, default='1', track_visibility='onchange')
    kanban_state = fields.Selection([('normal', 'Normal'), ('blocked', 'Bloqueado'), ('done', 'Listo para el Siguiente Estado')],
                                    string='Estado Kanban', track_visibility='onchange',
                                    required=True, default='normal')

    color = fields.Integer('Índice de Colores')
    legend_blocked = fields.Char(related="stage_id.legend_blocked", readonly=True)
    legend_done = fields.Char(related="stage_id.legend_done", readonly=True)
    legend_normal = fields.Char(related="stage_id.legend_normal", readonly=True)

    origen = fields.Selection([('odoo', 'Interno Odoo'), ('telegram', 'Telegram')],
                                    string='Generado via', required=True, default='odoo')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.user.company_id)
    tareas = fields.One2many('project.task', 'helpdesk_ticket', string='Tareas')
    origen_mail = fields.One2many('mail.message', 'ticket', string='Email')
    email_entrante = fields.Many2one('mail.message', string='Email Entrante', domain="[('model','=', 'pyme.mail.channel')]")	
    seguimiento_id = fields.One2many('pyme.seguimiento', 'helpdesk_ticket', string='Seguimiento')


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """ This function sets partner email address based on partner
        """
        self.email_from = self.partner_id.email



    @api.multi
    def crear_tarea(self):  
       idticket = self.id
       asuntoticket = self.name
       usuario = self.env.user.id
       description = self.description
       partner_id = self.partner_id.id
       email_from = ""
       if partner_id != False:
           email_from = self.env['res.partner'].search([('id', '=', partner_id )]).email
       view = {
	      'name': _('Crear Nueva Tarea'),
	      'view_type': 'form',
	      'view_mode': 'form',
	      'res_model': 'project.task',
	      'type': 'ir.actions.act_window',
	      'context': {'default_name': asuntoticket,'default_description': description,'default_user_id':usuario,'default_partner_id': partner_id,'default_helpdesk_ticket':idticket,'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
	      'target': 'current',}
       return view 

    @api.multi
    def crear_tarea_fija(self):  
       idticket = self.id
       asuntoticket = self.name
       usuario = self.env.user.id
       description = self.description
       partner_id = self.partner_id.id
       email_from = ""
       if partner_id != False:
           email_from = self.env['res.partner'].search([('id', '=', partner_id )]).email
       task_obj = self.env['project.task']
       task = task_obj.create({
          'name': str(asuntoticket),
          'partner_id': partner_id,
          'helpdesk_ticket': idticket, 
          'description': description})
       seguimiento_obj = self.env['pyme.seguimiento']
       seguimiento = seguimiento_obj.create({
	      'name': "Ticket: #" + str(asuntoticket) + " : " + str(asuntoticket),
	      'name_destino': "Tarea: " + str(asuntoticket),
	      'model_name_origen': 'helpdesk_lite.ticket',
	      'res_origen': self.id,
	      'helpdesk_ticket': self.id,
	      'model_name_destino': 'project.task', 
	      'model': 'helpdesk_lite.ticket',
	      'res_id': self.id,
	      'mail_message': self.id,
	      'project_task': task.id,
	      'res_destino': task.id})
       view_id = self.env['ir.ui.view'].search([('name', '=', 'Tareas-Popup' )]).id
       view = {
          'name': _('Crear Nueva Tarea'),
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': 'project.task',
          'view_id': view_id,
          'type': 'ir.actions.act_window',
          'target': 'new',
          'res_id': task.id }
       return view        


    @api.multi
    def unlink(self):
        partner_id = self.partner_id.id
        print(" El Partner es : " + str(partner_id))
        if partner_id == False:
           raise AccessError("Para eliminar un ticket es necesario tener un Contacto Asignado. La marca de Notificacion esta activada")
        tareastxt=""
        for ticket in self:
            for tareas in ticket.tareas:
                tareastxt +=   " - " + tareas.name  + str("\n")
        if str(tareastxt) != "":
           raise UserError("No puedes Eliminar el Ticket teniendo tareas asociadas. \n " + str(tareastxt) + "")
        for seguimiento in self.seguimiento_id:
                idseguimiento = seguimiento.id
                idmens = seguimiento.mail_message
                for mensjaes in idmens:
                    mensjaes.write({'procesado': False,'relacion': False})
                ## raise UserError("Hay un Seguimiento : "  + str(idseguimiento) + ". Tiene mensaje Origen: " + str(idmens.id) + "")
                try:
                   seguimiento.unlink()                
                except:
                   print("No he podido eliminar le Ticket #" + str(self.id) + ".")

        try: 
          modo = "unlink"
          partnerid = self.partner_id.id
          useridname = self.user_id.name
          asignado = self.user_id.name
          origen = "MODELO"
          estado = False
          asunto = self.name
          partneridname = self.partner_id.name
          mensajecliente = ""
          mensajeusuario = ""
          causa = "Eliminacion Ticket #" + str(self.id) + " : " + str(self.name) + "."
          self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), self.id ,mensajeusuario ,mensajecliente, self.partner_id.id, self.user_id.id,causa,origen,modo,asignado,estado,asunto)
        except:
          print("Error al Enviar la Notificacion por falta de Partner")
        resunlink = super(HelpdeskTicket, self).unlink()


        return resunlink



    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update(name=_('%s (copy)') % (self.name))
        return super(HelpdeskTicket, self).copy(default=default)

    def _can_add__recipient(self, partner_id):
        if not self.partner_id.email:
            return False
        if self.partner_id in self.message_follower_ids.mapped('partner_id'):
            return False
        return True

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(HelpdeskTicket, self).message_get_suggested_recipients()
        try:
            for tic in self:
                if tic.partner_id:
                    if tic._can_add__recipient(tic.partner_id):
                        tic._message_add_suggested_recipient(recipients, partner=tic.partner_id,
                                                             reason=_('Customer'))
                elif tic.email_from:
                    tic._message_add_suggested_recipient(recipients, email=tic.email_from,
                                                         reason=_('Customer Email'))
        except AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients

    def _email_parse(self, email):
        match = re.match(r"(.*) *<(.*)>", email)
        if match:
            contact_name, email_from =  match.group(1,2)
        else:
            match = re.match(r"(.*)@.*", email)
            contact_name =  match.group(1)
            email_from = email
        return contact_name, email_from

    @api.model
    def message_new(self, msg, custom_values=None):
        match = re.match(r"(.*) *<(.*)>", msg.get('from'))
        if match:
            contact_name, email_from =  match.group(1,2)
        else:
            match = re.match(r"(.*)@.*", msg.get('from'))
            contact_name =  match.group(1)
            email_from = msg.get('from')

        body = tools.html2plaintext(msg.get('body'))
        bre = re.match(r"(.*)^-- *$", body, re.MULTILINE|re.DOTALL|re.UNICODE)
        desc = bre.group(1) if bre else None

        defaults = {
            'name':  msg.get('subject') or _("No Subject"),
            'email_from': email_from,
            'description':  desc or body,
        }

        partner = self.env['res.partner'].sudo().search([('email', '=ilike', email_from)], limit=1)
        if partner:
            defaults.update({
                'partner_id': partner.id,
            })
        else:
            defaults.update({
                'contact_name': contact_name,
            })

        create_context = dict(self.env.context or {})
        # create_context['default_user_id'] = False
        # create_context.update({
        #     'mail_create_nolog': True,
        # })

        company_id = False
        if custom_values:
            defaults.update(custom_values)
            team_id = custom_values.get('team_id')
            if team_id:
                team = self.env['helpdesk_lite.team'].sudo().browse(team_id)
                if team.company_id:
                    company_id = team.company_id.id
        if not company_id and partner.company_id:
            company_id = partner.company_id.id
        defaults.update({'company_id': company_id})

        return super(HelpdeskTicket, self.with_context(create_context)).message_new(msg, custom_values=defaults)

    @api.model_create_single
    def create(self, vals):
        context = dict(self.env.context)
        context.update({
            'mail_create_nosubscribe': False,
        })
        vals['team_id'] = 1
        res = super(HelpdeskTicket, self.with_context(context)).create(vals)
        # res = super().create(vals)
        origen = "NUEVO"
        useridname = self.user_id.name
        partneridname = self.partner_id.name
        mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos asignado el Ticket: #" + str(self.id) + " a " + str(useridname)
        mensajeusuario = "Hola " + str(useridname) + ". Te hemos asignado a ti el Ticket: #" + str(self.id) + "."
        causa = "Creado Ticket #" + str(res.id) + " :: " + str(res.name) + ", por el Usuario: " + str(useridname) + "."
        modo = "create"
        asunto = vals['name']
        estado = False
        asignado = False
        idnum = res.id
        
        self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), idnum ,mensajeusuario ,mensajecliente, res.partner_id.id, res.user_id.id,causa,origen,modo,asignado,estado,asunto)
        email_entrante_id = res.email_entrante.id
        email_entrante = res.email_entrante
        print("\n\n EL ID que ha salido es: " + str(res.id) + " y Email: " + str(email_entrante_id) + ".\n\n ")
        if email_entrante_id != False:
            asuntoticket = res.name
            seguimiento_obj = self.env['pyme.seguimiento']
            seguimiento = seguimiento_obj.create({
           	   'name': "Email: " + str(asuntoticket),
           	   'name_destino': "Ticket: #" + str(res.id) + " :: " + str(asuntoticket),
           	   'model_name_origen': 'mail.message',
           	   'res_origen': email_entrante_id,
           	   'model_name_destino': 'helpdesk_lite.ticket',
           	   'model': 'mail.message', 
           	   'res_id': email_entrante_id,
           	   'mail_message': email_entrante_id,
           	   'helpdesk_ticket': res.id,
           	   'res_destino': res.id})
            email_entrante.write({'ticket': res.id})

        if res.partner_id:
            res.message_subscribe([res.partner_id.id])
        return res


    @api.multi
    def write(self, vals):
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
            stage = self.env['helpdesk_lite.stage'].browse(vals['stage_id'])
            if stage.last:
                vals.update({'date_done': fields.Datetime.now()})
            else:
                vals.update({'date_done': False})

        escribimos = super(HelpdeskTicket, self).write(vals)

        ## Notificaciones
        causa = ""
        modo = "write"
        origen = "MODELO"
        if 'user_id' in vals:
           userid = vals['user_id']
           ## print("Value Asignado: " + str(userid) + ".")
           useridname = self.user_id.name
           asignado = self.user_id.name
           estado = False
           asunto = self.name
           partneridname = self.partner_id.name
           mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos asignado el Ticket: #" + str(self.id) + " a " + str(useridname)
           mensajeusuario = "Hola " + str(useridname) + ". Te hemos asignado a ti el Ticket: #" + str(self.id) + "."
           causa = "Actualización Ticket #" + str(self.id) + " : " + str(self.name) + ". Cambio de Usuario: " + str(useridname) + "."
           self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), self.id ,mensajeusuario ,mensajecliente, self.partner_id.id, self.user_id.id,causa,origen,modo,asignado,estado,asunto)


        if 'stage_id' in vals:
           stageid = vals['stage_id']
           ## print("Cambio de Estado: " + str(stageid) + ".")
           estadoname = self.env['project.task.type'].search([('id', '=', int(stageid))], limit=1).name
           useridname = self.user_id.name
           asignado = self.user_id.name
           asunto = self.name
           estado = estadoname
           partneridname = self.partner_id.name
           mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos actualizado el Ticket: #" + str(self.id) + " al estado de " + str(estadoname)
           mensajeusuario = "Hola " + str(useridname) + ". Hemos actualizado el Ticket: #" + str(self.id) + " al estado de " + str(estadoname)
           causa = "Actualización Ticket #" + str(self.id) + " : " + str(self.name) + ". Cambio de Estado: " + str(estadoname) + "."
           self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), self.id ,mensajeusuario ,mensajecliente, self.partner_id.id, self.user_id.id,causa,origen,modo,asignado,estado,asunto)
        
        if 'partner_id' in vals:
           partnerid = vals['partner_id']
           useridname = self.user_id.name
           asignado = self.user_id.name
           estado = False
           asunto = self.name
           partneridname = self.partner_id.name
           mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos cambiado el Ticket: #" + str(self.id) + " al cliente  " + str(partneridname)
           mensajeusuario = "Hola " + str(useridname) + ". Te hemos cambiao el Ticket: #" + str(self.id) + " al cliente " + str(partneridname)
           causa = "Actualización Ticket #" + str(self.id) + " : " + str(self.name) + ". Cambio de Cliente: " + str(partneridname) + "."
           self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), self.id ,mensajeusuario ,mensajecliente, self.partner_id.id, self.user_id.id,causa,origen,modo,asignado,estado,asunto)
        return {}

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = []
        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.multi
    def takeit(self):
        self.ensure_one()
        vals = {
            'user_id' : self.env.uid,
            # 'team_id': self.env['helpdesk_lite.team'].sudo()._get_default_team_id(user_id=self.env.uid).id
        }
        causa = ""
        modo = "write"
        origen = "MODELO"
        takeitid = super(HelpdeskTicket, self).write(vals)
        useridname = self.user_id.name
        asignado = self.user_id.name
        estado = self.stage_id.name
        asunto = self.name
        partneridname = self.partner_id.name
        mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos asignado el Ticket: #" + str(self.id) + " a " + str(useridname)
        mensajeusuario = "Hola " + str(useridname) + ". Te hemos asignado a ti el Ticket: #" + str(self.id) + "."
        causa = "Actualización Ticket #" + str(self.id) + " : " + str(self.name) + ". Cambio de Usuario: " + str(useridname) + "."
        self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), self.id ,mensajeusuario ,mensajecliente, self.partner_id.id, self.user_id.id,causa,origen,modo,asignado,estado,asunto)

        return takeitid



    @api.model_cr
    def _register_hook(self):
        HelpdeskTicket.website_form = bool(self.env['ir.module.module'].
                                           search([('name', '=', 'website_form'), ('state', '=', 'installed')]))
        if HelpdeskTicket.website_form:
            self.env['ir.model'].search([('model', '=', self._name)]).write({'website_form_access': True})
            self.env['ir.model.fields'].formbuilder_whitelist(
                self._name, ['name', 'description', 'date_deadline', 'priority', 'partner_id', 'user_id'])
        pass

class HelpEtiqueta(models.Model):
    _name = 'helpdesk_lite.etiquetas'
	
    name = fields.Char(string='Etiquetas')
    ## model = fields.Many2one('ir.model')
    ## donde = fields.Selection([('TAREA', 'Tarea'),('EMAIL', 'Correo Electrónico'),('CALENDAR', 'Calendario'),('PARTNER', 'Entidades'),('ARTICULOS', 'Artículos')], string='Tipo')

class HelpTareas(models.Model):
    _inherit = 'project.task'
	
    helpdesk_ticket = fields.Many2one('helpdesk_lite.ticket', string='HelpDesk Ticket')
    email_entrante = fields.Many2one('mail.message', string='Email Entrante', domain="[('model','=', 'pyme.mail.channel')]")	


class Seguimiento(models.Model):
    _inherit = 'pyme.seguimiento'
	

    helpdesk_ticket = fields.Many2one('helpdesk_lite.ticket', string='Ticket Asociado')


