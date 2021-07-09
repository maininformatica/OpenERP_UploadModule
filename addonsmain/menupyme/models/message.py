# -*- coding: utf-8 -*-

### from openerp import models, fields, api, exceptions, tools
from openerp import models, api, exceptions, tools
from openerp.osv import expression, osv
### from openerp.osv import expression, fields, osv
from openerp import _, api, fields, models, SUPERUSER_ID
from openerp import tools
from openerp.exceptions import UserError, AccessError
from openerp.exceptions import except_orm
from openerp.exceptions import  Warning
from openerp.osv.orm import except_orm
	
class Message_Custom(models.Model):
	_inherit = "mail.message"

	tipo_etiquetas = fields.Many2many('etiquetas_relacion', 'etiquetas', 'display_name', string='Tipo de Etiquetas')

	relacion = fields.Many2one('clasificar_tarea', string='Relación')

	tareas = fields.Many2one('project.task', string='Tareas')

	clientes = fields.Many2one('res.partner', string='Clientes')

	productos = fields.Many2one('product.template', string='Productos')

	pedido_venta = fields.Many2one('sale.order', string='Pedido de Venta')

	pedido_compra = fields.Many2one('purchase.order', string='Pedido de Compra')
	
	albaran = fields.Many2one('stock.picking', string='Albaranes')

	factura = fields.Many2one('account.invoice', string='Facturas')
		
	rel_id = fields.Char(related='relacion.name', string="IDREL")	

@api.multi
def onchange_relacion(self, cr, uid, ids, relacion, context=None):
 if relacion:           
    value = {
	'country_name': res_country.browse(cr, uid, country_id).name
	}
 return {'value': value}
