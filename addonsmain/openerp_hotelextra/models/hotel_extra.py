# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import pycurl, json, requests


class ImageExtra(models.Model):

     _name = 'hotel.image.extra'
     _description = 'Imágenes EXTRA PYME'

     image = fields.Binary("Imagen", attachment=True, help="Imagen  limitada a 1024x1024px",)
     name = fields.Char("Nombre")
     relacion = fields.Many2one('hotel.room.type', string='Relacion Tipo Habitación')
     relacionp = fields.Many2one('res.partner', string='Relacion con Contactos')


class RoomExtra(models.Model):

     _inherit = 'hotel.room'

     sequence = fields.Integer(string='Sequence', default=10)
     activa = fields.Boolean("TELEGRAM", attachment=True, help="Activa para reservar",)




class RoomTypeExtra(models.Model):

     _inherit = 'hotel.room.type'

     image = fields.Binary("Imagen", attachment=True, help="Imagen  limitada a 1024x1024px",)
     pvpbase = fields.Float("Precio Base", attachment=True, help="Precio de la Habitación Base",)
     activa = fields.Boolean("Telegram", attachment=True, help="Activa para reservar",)
     descripcion = fields.Char(string='Descripción')
     maxpeople = fields.Integer(string='Max. Ocupacion')
     imagenes = fields.One2many('hotel.image.extra', 'relacion', string='Más Imágenes')
     relhab = fields.One2many('hotel.room', 'categ_id', string='Más Imágenes')     
     

class RoomAmenitiesTypeExtra(models.Model):

     _inherit = 'hotel.room.amenities.type'

     image = fields.Binary("Image", attachment=True, help="Imagen  limitada a 1024x1024px",)
     descripcion = fields.Char(string='Descripción')



class ServiceTypeExtra(models.Model):

     _inherit = 'hotel.service.type'

     image = fields.Binary("Image", attachment=True, help="Imagen  limitada a 1024x1024px",)
     descripcion = fields.Char(string='Descripción')
     activa = fields.Boolean("TELEGRAM", attachment=True, help="Activa para reservar",)
     conreserva = fields.Boolean("Incluido en Reserva", attachment=True, help="Dicho Servicio está en la reserva de la Habitación",)

class ServiceExtra(models.Model):

     _inherit = 'hotel.services'
     activa = fields.Boolean("TELEGRAM", attachment=True, help="Activa para reservar",)
     activahos = fields.Boolean("Serv. Alojado", attachment=True, help="Activa para reservar si estás Hospedado",)
     preguntatelegram = fields.Text(string="Texto Pregunta")
     ## preguntatelegram2 = fields.Text(string="Pregunta 2")     


class ServiceReservationdetallesExtra(models.Model):

     _name = 'hotel.reservation.services'

     name = fields.Many2one('hotel.services')
     partner_id = fields.Many2one('res.partner', related='numreserva.partner_id', store=True)
     tipodeservicio = fields.Many2one('hotel.service.type', related='name.categ_id', store=True)
     numreserva = fields.Many2one('hotel.reservation')
     fechahora = fields.Char('Detalle')
     obs = fields.Char('Observaciones')
     gestionado = fields.Boolean('Gestionado')
     gestionadofecha = fields.Datetime('Fecha Gestionado')
     
     

     def marcagestionado(self):
           self.write({'gestionado': True})
           self.write({'gestionadofecha': fields.Datetime.now()})

           
           
     def quitagestionado(self):
           self.write({'gestionado': False})
           self.write({'gestionadofecha': False})
         




class ServiceReservationExtra(models.Model):

     _inherit = 'hotel.reservation'
     
     observaciones = fields.Text('Observaciones del Cliente')
     tipoaloj = fields.Many2one('hotel.services', string='Tipo de Alojamiento')
     relservicios = fields.Many2many('hotel.reservation.services', string='Servicios Reservados')  
     estoyalojado = fields.Boolean(string='Estoy Alojado', related='partner_id.estoyalojado') 
     tiporest = fields.Boolean(string='Reserva Restaurante') 
 
 
     @api.multi
     def button_estoyalojado(self, default=None):
        partnerid = self.partner_id.id
        self.env.cr.execute(""" update res_partner set estoyalojado='t' where id='%s'""" % (str(partnerid)))
        ## self.write({'estoyalojado': True})
 
 


class ProjectTaskExtra(models.Model):

     _inherit = 'project.task'
     
     respuesta = fields.Text(string='Respuesta Cliente')   
 

class ResPartnerExtra(models.Model):

     _inherit = 'res.partner'
     
     estoyalojado = fields.Boolean(string='Estoy Alojado')  
     reserevas = fields.One2many('hotel.reservation', 'partner_id', string='Reserva Habitaciones')
     mensajes = fields.One2many('project.task', 'partner_id', string='Mensajes')
     serviciosrel = fields.One2many('hotel.reservation.services', 'partner_id', string='Servicios Reservados')
     enviarmensaje = fields.Char("Enviar Mensaje")
     ## imagenes = fields.One2many('hotel.image.extra', 'relacionp', string='Extra Images')     

     @api.multi
     def buttonenviarmensaje(self, default=None):
          iduser = self.id
          mensaje = str(self.enviarmensaje)
          rasatelegramid = str(self.rasa_telegramid)
          print("================" + str(mensaje) + ". Usuario: " + str(rasatelegramid))
          self.write({'enviarmensaje': False})  
          if mensaje == "False":
             raise UserError("ERROR: No puedes Enviar un Mensaje Vacio. Edita, escribe el texto y pincha en Enviar")
             return []
          if rasatelegramid == "False":
             raise UserError("ERROR: No puedes Enviar un Mensaje sin usuario de Telegram")
             return []
          url = "http://localhost:5005/webhooks/telegram/webhook/"
          data = {
              "update_id": 1,
              "message": {
                  "message_id": 1,
                  "from": {
                      "id": "" + str(rasatelegramid) + "",
                      "is_bot": False,
                      "first_name": "",
                      "username": "",
                      "language_code": "es"
                  },
                  "chat": {
                      "id": "" + str(rasatelegramid) + "",
                      "first_name": "",
                      "username": "",
                      "type": "private"
                  },
                  "date": 1234,
                  "text": "/notify-" + str(mensaje) + ""
              }
          }
          headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
          r = requests.post(url, data=json.dumps(data), headers=headers)
          responsem = r.text
          if str(responsem) == "success":
                    project_id = 10
                    description = ' '
          else:
                    project_id = 11
                    description = 'Respuesta: <b>' + str(responsem) + '</b>.'

          task_obj = self.env['project.task']
          taskproject = task_obj.create({
            'name': str(mensaje),
            'project_id': project_id,
            'partner_id': iduser,
            'stage_id': 19,
            'description': str(description),})

     
          return
