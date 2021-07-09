# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
class dialogflowacc(models.Model):

     _name = 'dialogflowacc'

     name = fields.Char(string='Nombre de Accion', required=True)
     numeventos = fields.Integer(string='Total eventos')
     resultadopos = fields.Text(string='Resultado Positivo')
     resultadoneg = fields.Text(string='Resultado Negativo')
     variables = fields.One2many('dialogflowvariables', 'accion', string='variables')
     codigointent = fields.Char(string='Código Intent')
     entrada = fields.Char(string='Variable Entrada Accion')
     accioncodigo = fields.Char(string='Parametros DialogFlow')
     llamada = fields.One2many('crm.phonecall', 'dialogflow', string='variables')

     _sql_constraints = [
              ('unique_accioncodigo', 'unique(accioncodigo)','Error: No puedes duplicar la variable de Parametros DialogFlow')
              ]


class dialogflowvariables(models.Model):

     _name = 'dialogflowvariables'

     name = fields.Char(string='Variable')
     direccion = fields.Selection([('IN', 'ENTRADA'), ('OUT', 'SALIDA')], string='Tipo variable')
     campo = fields.Many2one('ir.model.fields', string='campo')
     accion = fields.Many2one('dialogflowacc')

class dialogflowlogging(models.Model):

     _name = 'dialogflowlogging'

     name = fields.Char(string='Origen')
     date = fields.Datetime(string='Fecha Log', index=True, help="Fecha en la que se guarda el LOG.")
     datos = fields.Text('Datos')
     accion = fields.Many2one('dialogflowacc')


class CrmPhonecall(models.Model):
     # Herencia de la tabla de ventas
     _inherit = 'crm.phonecall'

     # Añadir el estado Pedido a ventas
     descripcion  = fields.Text('Descripcion')
     dialogflow = fields.Many2one('dialogflowacc')
     intent = fields.Char(string='Intent Reconocido')
     notas = fields.Text('Notas')
     emailenviado = fields.Boolean(string="Email Enviado")

     @api.multi
     def action_asignavariables(self, default=None):
         pedido = self.descripcion
         cadenaPedido = pedido.split (" || ")

         self.intent = cadenaPedido[0]
         self.partner_phone = cadenaPedido[4]
         self.notas = cadenaPedido[1]


         ##raise UserError(_('Cadena: %s' % cadena))
