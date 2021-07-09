# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, tools
from openerp.osv import expression, fields, osv
from openerp import _, api, fields, models, SUPERUSER_ID
from openerp import tools
from openerp.exceptions import UserError, AccessError
from openerp.exceptions import except_orm



class Task_clientes(models.Model):
	_inherit = "res.partner"
	
	tasks = fields.One2many('project.task', 'partner', string='Tareas')