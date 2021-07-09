# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                  'currency_id', 'company_id', 'date_invoice', 'type')
    def compute_discount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        discount = 0
        for line in self.invoice_line_ids:
            discount += (line.price_unit * line.quantity * line.discount) / 100
        self.discount = discount
        ## self.discount = 2
        ## 
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        ## self.amount_untaxed_signed = amount_untaxed_signed * sign
    
    
    
    @api.one
    @api.depends('invoice_line_ids')
    def compute_total_before_discount(self):
        total = 0
        for line in self.invoice_line_ids:
            total += line.price_subtotal
        self.total_before_discount = total
        totalbd = self.total_before_discount
        totalun = self.amount_untaxed
        discounttype = self.discount_type
        discountrate = self.discount_rate
        discount = self.discount
        self.amount_untaxed = totalbd - discount
        
      
    discount_type = fields.Selection([('percentage', 'Porcentaje'), ('amount', 'Importe')], string='Tipo de Descuento',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='amount')
    discount_rate = fields.Float(string='Valor Descuento', digits=(16, 2),
                                 readonly=True, states={'draft': [('readonly', False)]}, default=0.0)
    discount = fields.Monetary(string='Descuento Global', digits=(16, 2), default=0.0,
                               store=True, track_visibility='always')
    total_before_discount = fields.Monetary(string='Importe Bruto', digits=(16, 2), store=True, compute='compute_total_before_discount')


    @api.multi
    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        totalbd = self.total_before_discount
        discount = self.discount
        if discount:
            self.amount_untaxed = totalbd - discount
        



    @api.multi
    @api.onchange('discount_rate')
    def _onchange_discount_rate(self):
        vals = {}
        for line in self.invoice_line_ids:
            vals[line] = {
                'price_unit': line.price_unit,
                'discount': line.discount,
                'importe': line.importe,
                'quantity': line.quantity,
                
            }
        totalbd = self.total_before_discount
        discounttype = self.discount_type
        discountrate = self.discount_rate
        if discounttype == 'amount' :
            self.amount_untaxed = totalbd - discountrate 
            self.discount = discountrate 
        else:
            discrate = totalbd * ( discountrate/100) 
            self.discount = discrate
            self.amount_untaxed = totalbd - discrate     
        




    @api.multi
    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        totalbd = self.total_before_discount
        totalun = self.amount_untaxed
        discounttype = self.discount_type
        discountrate = self.discount_rate
        if discountrate != 0:
            if discounttype == 'amount':
                discountrate = (discountrate * totalbd ) / 100
                self.discount_rate = discountrate 
            else:
                discountrate = (discountrate * 100 ) / totalbd
                self.discount_rate = discountrate


        
        


    @api.multi
    def get_taxes_values(self):
        vals = {}
        for line in self.invoice_line_ids:
            vals[line] = {
                'price_unit': line.price_unit,
                'discount': line.discount,
                'importe': line.importe,
                'quantity': line.quantity,
                
            }

            
            prev_price_unit = line.price_unit
            
            if line.importe:
                price_unit = line.importe / line.quantity
                price_subtotal = price_unit * line.quantity
            else:  
                price_unit = line.price_unit
                price_subtotal = line.price_subtotal

            line.update({
                'price_subtotal': price_subtotal,
                'price_unit': price_unit,
                'discount': 0.0,
            })
        tax_grouped = super(AccountInvoice, self).get_taxes_values()
        for line in self.invoice_line_ids:
            line.update(vals[line])
        return tax_grouped
        




    @api.model
    def create(self, vals):
        
        if not vals.get('journal_id') and vals.get('type'):
            vals['journal_id'] = self.with_context(type=vals.get('type'))._default_journal().id

        onchanges = self._get_onchange_create()
        for onchange_method, changed_fields in onchanges.items():
            if any(f not in vals for f in changed_fields):
                invoice = self.new(vals)
                getattr(invoice, onchange_method)()
                for field in changed_fields:
                    if field not in vals and invoice[field]:
                        vals[field] = invoice._fields[field].convert_to_write(invoice[field], invoice)
        bank_account = self._get_default_bank_id(vals.get('type'), vals.get('company_id'))
        if bank_account and not vals.get('partner_bank_id'):
            vals['partner_bank_id'] = bank_account.id

        invoice = super(AccountInvoice, self.with_context(mail_create_nolog=True)).create(vals)

        if any(line.invoice_line_tax_ids for line in invoice.invoice_line_ids) and not invoice.tax_line_ids:
            self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (invoice.id,))
            ###    invoice.compute_taxes()

        return invoice











class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    discount2 = fields.Float(
        'Descuento (%)',
        digits=dp.get_precision('Discount'),
    )
    importe = fields.Float(
        'Importe',
        digits=dp.get_precision('Discount'),
    )
    discount3 = fields.Float(
        'Descuento (Importe)',
        digits=dp.get_precision('Discount'),
    )
    

    @api.multi
    @api.onchange('discount3')
    def _onchange_discount3(self):
        total = self.price_unit * self.quantity
        if ( self.discount3 and total != 0):
            self.discount2 = (self.discount3 * 100) / total
            
  
  
    @api.multi
    ## @api.depends('discount2')
    def _compute_price(self):
        for line in self:
            prev_price_unit = line.price_unit
            prev_discount = line.discount
            cantidad = line.quantity
            discount2 = line.discount2
            subtotal=line.price_subtotal
            price_unit = line.price_unit * (1 - (line.discount2 or 0.0) / 100.0) 
            importe = price_unit * cantidad
            
            if discount2 != 0:
                discount3 = ( prev_price_unit - price_unit ) 
                
                
            else:
                discount3 = 0
          
            line.update({
                'price_unit': price_unit,
                'discount': 0.0,
                'importe': importe,
                'discount3': discount3,
            })
            super(AccountInvoiceLine, line)._compute_price()
            line.update({
                'price_unit': prev_price_unit,
                'importe': importe,
                'discount': prev_discount,
            })
