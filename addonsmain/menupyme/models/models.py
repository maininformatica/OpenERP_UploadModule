# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
## from openerp import models, api, exceptions
from openerp.osv import expression
## from openerp import _, api, fields, models, SUPERUSER_ID
from openerp import _, api, models, SUPERUSER_ID
from openerp import tools
from openerp.exceptions import UserError, AccessError


class Mensaje(models.Model):
    _name = 'mails_relacion'

    prueba = fields.Char(string='Prueba')
	
class Etiqueta(models.Model):
    _name = 'etiquetas_relacion'
	
    name = fields.Char(string='Etiquetas')
    model = fields.Many2one('ir.model')
    donde = fields.Selection([('TAREA', 'Tarea'),('EMAIL', 'Correo Electrónico'),('CALENDAR', 'Calendario'),('PARTNER', 'Entidades'),('ARTICULOS', 'Artículos')], string='Tipo')
	
	
	
class Clasificar(models.Model):
    _name = 'clasificar_tarea'
	
    name = fields.Char(string='Descripcion')
	
    model = fields.Many2one('ir.model')
	



	
	
	
	
	

