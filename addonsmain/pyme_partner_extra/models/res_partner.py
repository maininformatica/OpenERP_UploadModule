# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP




class addResPartnerRasa(models.Model):
    _inherit = "res.partner"

    rasa_telegramid = fields.Char("Telegram ID")
    rasa_userid = fields.Char("Rasa USERID")
    latitud = fields.Char("Latitud")
    longitud = fields.Char("Longitud")
    mapslocalizacion = fields.Char("URL Localizacion en MAPS")
    localizacionamigable = fields.Text("Localizacion Amigable")
    horario = fields.Text("Horario de Atención al Público")
    horarioc = fields.Text("Horario Comercial")
    actividad = fields.Text("Actividad Empresarial")

    _sql_constraints = [('rasa_telegramid_unique', 'unique(rasa_telegramid)', 'El ID de Telegram que has escrito ya existe en otro Contacto.')]



    ## partner_gid = fields.Char("GiD")
    ##additional_info = fields.Char("Extra Information")
    ## partner_autocomplete_insufficient_credit = fields.Char("partner_autocomplete_insufficient_credit")
    ## tareas = fields.One2many('project.task', 'partner_id', string='Tareas / Mensajes Asignados')
    ## reserevas = fields.One2many('hotel_reservation', 'partner_id', string='Reserva Habitaciones')
    ## servicios = fields.One2many('hotel.reservation.services', 'partner_id', string='Servicios Reservados')
    ## serviciosrel = fields.One2many('hotel.reservation.services', 'partner_id', string='Servicios Reservados')
    ## imagenes = fields.One2many('hotel.image.extra', 'relacionp', string='Extra Images')

    


   
