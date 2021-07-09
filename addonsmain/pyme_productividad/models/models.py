# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError


class EmailActivityExtra(models.Model):
    _inherit = 'mail.activity'
    namemodel = fields.Char(string='Docuemnto Origen',related='res_model_id.name')
	
    @api.multi
    def action_open_related_document(self):
        idactivity = self.id        	
        idmodel = self.res_model
        iddestino = self.res_id
        view = {
          'name': _('Emails Enviados'),
          'view_type': 'form',
          'view_mode': 'form',
          'res_model': str(idmodel),
          'view_id': False,
          'type': 'ir.actions.act_window',
          'target': 'current',
          'res_id': iddestino }
        return view  






class ProjectExtra(models.Model):
    _inherit = 'project.project'
    tareaportalvisible = fields.Boolean(string='Tarea Visible en Portal de Proyectos', default=False)
    privacy_visibility = fields.Selection([
            ('resyasig', 'Responsables y Asignados'),
            ('asignmanual', 'Permite añadir cualquier Contacto a Seguidores'),
            ## ('followers', 'No se como llamarle. Lo que hace es no permite crear followers pero arrastra mis seguidores'),
            ## ('employees', 'Visible para todos los empleados'),
            ('portal', 'Añade Siempre Clientes a Seguidores'),
        ],
        string='Privacy', required=True,
        default='resyasig',
        help="Holds visibility of the tasks or issues that belong to the current project:\n"
                "- On invitation only: Employees may only see the followed project, tasks or issues\n"
                "- Visible by all employees: Employees may see all project, tasks or issues\n"
                "- Visible by following customers: employees see everything;\n"
                "   if website is activated, portal users may see project, tasks or issues followed by\n"
                "   them or by someone of their company\n")










class InviteWizardExtra(models.TransientModel):
    _inherit = 'mail.wizard.invite'


    @api.multi
    def add_followers(self):
        email_from = self.env['mail.message']._get_default_from()
        for wizard in self:
            Model = self.env[wizard.res_model]
            document = Model.browse(wizard.res_id)

            # filter partner_ids to get the new followers, to avoid sending email to already following partners
            new_partners = wizard.partner_ids - document.message_partner_ids
            new_channels = wizard.channel_ids - document.message_channel_ids
            document.message_subscribe(new_partners.ids, new_channels.ids)

            strdatos = ""
            proyectotarea = "False"
            if str(wizard.res_model) == "project.task":
               proyectotarea = self.env['project.task'].search([('id', '=', int(wizard.res_id))]).project_id.privacy_visibility
               ## strdatos += "Es tarea con Tipo de Proyecto: " + str(proyectotarea)
            for partners in wizard.partner_ids:
                strdatos += "\n Cliente: " + str(partners.name) + ""

            ### print("Es: " + str(proyectotarea))
            ### if str(proyectotarea) != "False":
            ###   if str(proyectotarea) != "asignmanual":
            ###     raise UserError("La configruación al Proyecto que pertenece la Tarea Impide agregar a: " + str(strdatos))

            model_name = self.env['ir.model']._get(wizard.res_model).display_name
            # send an email if option checked and if a message exists (do not send void emails)
            if wizard.send_mail and wizard.message and not wizard.message == '<br>':  # when deleting the message, cleditor keeps a <br>
                message = self.env['mail.message'].create({
                    'subject': _('Invitation to follow %s: %s') % (model_name, document.name_get()[0][1]),
                    'body': wizard.message,
                    'record_name': document.name_get()[0][1],
                    'email_from': email_from,
                    'reply_to': email_from,
                    'model': wizard.res_model,
                    'res_id': wizard.res_id,
                    'no_auto_thread': True,
                    'add_sign': True,
                })
                partners_data = []
                recipient_data = self.env['mail.followers']._get_recipient_data(document, False, pids=new_partners.ids)
                for pid, cid, active, pshare, ctype, notif, groups in recipient_data:
                    pdata = {'id': pid, 'share': pshare, 'active': active, 'notif': 'email', 'groups': groups or []}
                    if not pshare and notif:  # has an user and is not shared, is therefore user
                        partners_data.append(dict(pdata, type='user'))
                    elif pshare and notif:  # has an user and is shared, is therefore portal
                        partners_data.append(dict(pdata, type='portal'))
                    else:  # has no user, is therefore customer
                        partners_data.append(dict(pdata, type='customer'))
                self.env['res.partner'].with_context(auto_delete=True)._notify(
                    message, partners_data, document,
                    force_send=True, send_after_commit=False)
                message.unlink()
        return {'type': 'ir.actions.act_window_close'}




class TaskExtra(models.Model):
    _inherit = 'project.task'

    def _compute_task_count2(self):
        task_data = self.env['project.task'].read_group([('project_id', 'in', self.ids), '|', ('stage_id.fold', '=', False), ('stage_id', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.task_count2 = result.get(project.id, 0)




    tareaportalvisible = fields.Boolean(string='Tarea Visible en Portal de Proyectos', default=False)
    seguimiento_id = fields.One2many('pyme.seguimiento', 'project_task', string='Seguimiento')	
    cliente = fields.Many2one('res.partner', string='Cliente Ticket')
    clientesproyecto = fields.Many2one('res.partner', string='Cliente Proyecto')
    task_count2 = fields.Integer(compute='_compute_task_count2', string="Contador Visibles")
    email_entrante = fields.Many2one('mail.message', string='Email Entrante', domain="[('model','=', 'pyme.mail.channel')]")	
    project_id = fields.Many2one('project.project',
        string='Project',
        default=1,
        index=True,
        track_visibility='onchange',
        change_default=True)


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        print("PEPEPEEPEP")
        ### self.email_from = self.partner_id.email

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            for field_name in self._subtask_implied_fields():
                ### self[field_name] = self.parent_id[field_name]
                print("PEPEPE")

    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            if self.project_id.tareaportalvisible == True:
               self.tareaportalvisible = True
            else:
               self.tareaportalvisible = False

            if self.project_id.partner_id:
               self.clientesproyecto = self.project_id.partner_id
            if not self.parent_id and self.project_id.partner_id:
                print("PEPEPEEPEP")
                #### self.partner_id = self.project_id.partner_id
            if self.project_id not in self.stage_id.project_ids:
                self.stage_id = self.stage_find(self.project_id.id, [('fold', '=', False)])

    @api.model
    @api.multi
    def create(self, vals):
        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)
        # force some parent values, if needed
        if 'parent_id' in vals and vals['parent_id']:
            vals.update(self._subtask_values_from_parent(vals['parent_id']))
            context.pop('default_parent_id', None)
        # for default stage
        if vals.get('project_id') and not context.get('default_project_id'):
            context['default_project_id'] = vals.get('project_id')
        # user_id change: update date_assign
        if vals.get('user_id'):
            vals['date_assign'] = fields.Datetime.now()
        # Stage change: Update date_end if folded stage and date_last_stage_update
        if vals.get('stage_id'):
            vals.update(self.update_date_end(vals['stage_id']))
            vals['date_last_stage_update'] = fields.Datetime.now()
        task = super(TaskExtra, self.with_context(context)).create(vals)
        clientesproyecto = task.clientesproyecto.id
        tipoproyecyo = self.project_id.privacy_visibility
        creadores = str(self.create_uid.partner_id.id) + "," + str(self.write_uid.id) + "," + str(self.user_id.id)
        strfoll = "Creadores: " + str(creadores) + ". Los Seguidores son: "
        res = task
        origen = "NUEVO"
        modo = "create"
        useridname = self.user_id.name
        partneridname = self.partner_id.name
        mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos asignado el Ticket: #" + str(self.id) + " a " + str(useridname)
        mensajeusuario = "Hola " + str(useridname) + ". Te hemos asignado a ti el Ticket: #" + str(self.id) + "."
        causa = "Creada TAREA #" + str(res.id) + " :: " + str(res.name) + ", por el Usuario: " + str(useridname) + "."
        print("\n\n " + str(res.partner_id.id) + " " + str(res.user_id.id) + "")
        estado = self.env['helpdesk_lite.stage'].search([('id', '=', int(self.stage_id.id))], limit=1).name
        asignado = self.user_id.name
        asunto = vals['name']
        idtarea = task.id
        self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), idtarea ,mensajeusuario ,mensajecliente, res.partner_id.id, res.user_id.id,causa,origen,modo,asignado,estado,asunto)
        email_entrante_id = res.email_entrante.id
        helpdesk_ticket = res.helpdesk_ticket.id
        email_entrante = res.email_entrante
        print("\n\n EL ID que ha salido es: " + str(res.id) + " y Email: " + str(email_entrante_id) + ".\n\n ")
        if email_entrante_id != False:
            asuntoticket = res.name
            seguimiento_obj = self.env['pyme.seguimiento']
            seguimiento = seguimiento_obj.create({
	          'name': "Email: " + str(asuntoticket),
	          'name_destino': "Tarea: " + str(asuntoticket),
	          'model_name_origen': 'mail.message',
	          'res_origen': res.id,
	          'model_name_destino': 'project.task', 
	          'model': 'mail.message', 
	          'res_id': self.id,
	          'mail_message': self.id,
	          'project_task': task.id,
	          'res_destino': task.id})
            email_entrante.write({'tarea': res.id})
        if helpdesk_ticket != False:
            asuntoticket = res.name
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

        return task


    @api.multi
    def write(self, vals):
        now = fields.Datetime.now()
        # subtask: force some parent values, if needed
        if 'parent_id' in vals and vals['parent_id']:
            vals.update(self._subtask_values_from_parent(vals['parent_id']))
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            vals.update(self.update_date_end(vals['stage_id']))
            vals['date_last_stage_update'] = now
            # reset kanban state when changing stage
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
        # user_id change: update date_assign
        if vals.get('user_id') and 'date_assign' not in vals:
            vals['date_assign'] = now

        result = super(TaskExtra, self).write(vals)
        # rating on stage
        if 'stage_id' in vals and vals.get('stage_id'):
            self.filtered(lambda x: x.project_id.rating_status == 'stage')._send_task_rating_mail(force_send=True)
        # subtask: update subtask according to parent values
        subtask_values_to_write = self._subtask_write_values(vals)
        if subtask_values_to_write:
            subtasks = self.filtered(lambda task: not task.parent_id).mapped('child_ids')
            if subtasks:
                subtasks.write(subtask_values_to_write)

        causa = ""
        modo = "write"
        ## Notificaciones
        if 'user_id' in vals:
           userid = vals['user_id']
           print("Value Asignado: " + str(userid) + ".")
           useridname = self.user_id.name
           partneridname = self.partner_id.name
           asignado = useridname
           estado = False
           asunto = self.name
           mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos asignado la TAREA: #" + str(self.id) + " a " + str(useridname)
           mensajeusuario = "Hola " + str(useridname) + ". Te hemos asignado a ti la TAREA: #" + str(self.id) + "."
           causa = "Tarea #:" + str(self.id) + " : " + str(self.name) + ". Cambio de Usuario: " + str(useridname) + "."
           self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), self.id ,mensajeusuario ,mensajecliente, self.partner_id.id, self.user_id.id,causa,"MODELO",modo,asignado,estado,asunto)


        if 'stage_id' in vals:
           stageid = vals['stage_id']
           print("Cambio de Estado: " + str(stageid) + ".")
           estadoname = self.env['helpdesk_lite.stage'].search([('id', '=', int(stageid))], limit=1).name
           useridname = self.user_id.name
           asignado = useridname
           estado = self.env['helpdesk_lite.stage'].search([('id', '=', int(stageid))], limit=1).name
           asunto = self.name
           partneridname = self.partner_id.name
           mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos actualizado la TAREA: #" + str(self.id) + " al estado de " + str(estadoname)
           mensajeusuario = "Hola " + str(useridname) + ". Hemos actualizado el Ticket: #" + str(self.id) + " al estado de " + str(estadoname)
           causa = "Tarea #:" + str(self.id) + " : " + str(self.name) + ". Cambio de Estado: " + str(estadoname) + "."
           self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), self.id ,mensajeusuario ,mensajecliente, self.partner_id.id, self.user_id.id,causa,"MODELO",modo,asignado,estado,asunto)


        if 'partner_id' in vals:
           partnerid = vals['partner_id']
           useridname = self.user_id.name
           partneridname = self.partner_id.name
           asignado = useridname
           estado = False
           asunto = self.name
           mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos cambiado la TAREA: #" + str(self.id) + " al cliente  " + str(partneridname)
           mensajeusuario = "Hola " + str(useridname) + ". Te hemos cambiao el Ticket: #" + str(self.id) + " al cliente " + str(partneridname)
           causa = "Tarea #:" + str(self.id) + " : " + str(self.name) + ". Cambio de Cliente: " + str(partneridname) + "."
           self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), self.id ,mensajeusuario ,mensajecliente, self.partner_id.id, self.user_id.id,causa,"MODELO",modo,asignado,estado,asunto)



        
        return result


    @api.multi
    def unlink(self):
        for tareas in self:
            for seguimiento in tareas.seguimiento_id:
                idseguimiento = seguimiento.id
                idmens = seguimiento.mail_message
                for mensjaes in idmens:
                    mensjaes.write({'procesado': False,'relacion': False})
                ## raise UserError("Hay un Seguimiento : "  + str(idseguimiento) + ". Tiene mensaje Origen: " + str(idmens.id) + "")
                seguimiento.unlink()                

            modo = "unlink"
            useridname = self.user_id.name
            partneridname = self.partner_id.name
            asignado = useridname
            estado = self.env['helpdesk_lite.stage'].search([('id', '=', int(self.stage_id.id))], limit=1).name
            asunto = self.name
            mensajecliente = ""
            mensajeusuario = ""
            causa = "Tarea #:" + str(self.id) + " : " + str(self.name) + ". Eliminada."
            self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), self.id ,mensajeusuario ,mensajecliente, self.partner_id.id, self.user_id.id,causa,"MODELO",modo,asignado,estado,asunto)
            resunlink = super(TaskExtra, tareas).unlink()
            return resunlink

    def _message_post_after_hook(self, message, *args, **kwargs):
        ### print("\n\n\n ESTAMOS EN TAREAS: " + str(message.body) + "\n\n\n")
        modo="chatter"
        if str(message.body) != "":
            mmessage_txt = str(message.body).replace('<p>','').replace('</p>','')
            useridname = "Jose Tormo"
            partneridname = "Pepe Tormo Cliente"
            partner_id2 = self.partner_id.id
            user_id2 = self.user_id.id
            mensajecliente = "Estimado Cliente " + str(partneridname) + ", hemos asignado el Ticket: #" + str(self.id) + " a " + str(useridname)
            mensajeusuario = "Hola " + str(useridname) + ". Te hemos asignado a ti el Ticket: #" + str(self.id) + "."
            if str(mmessage_txt) != "False":
               causa = "Tarea #:" + str(self.id) + " : " + str(self.name) + ", actualizada. Mensaje: " + str(mmessage_txt) + "."
               asignado = False
               estado = False
               asunto = mmessage_txt
               self.pool.get('pyme.notificaciones').envianotificaciones(self, str(self._name), str(self.id) ,mensajeusuario ,mensajecliente, partner_id2, user_id2,causa,"CHATTER",modo,asignado,estado,asunto)

        if self.email_from and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email_from)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email_from', '=', new_partner.email),
                    ('stage_id.fold', '=', False)]).write({'partner_id': new_partner.id})
        ## return super(Task, self)._message_post_after_hook(message, *args, **kwargs)
        return {}


    
    
class TaskSeguimiento(models.Model):
    _inherit = 'pyme.seguimiento'
    project_task = fields.Many2one('project.task', string='Tarea Asociada')    