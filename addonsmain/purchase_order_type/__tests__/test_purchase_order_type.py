# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Pierre Faniel - Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


class TestpurchaseOrderType(common.TransactionCase):

    def setUp(self):
        super(TestpurchaseOrderType, self).setUp()
        self.purchase_type_model = self.env['purchase.order.type']
        self.purchase_order_model = self.env['purchase.order']
        self.invoice_model = self.env['account.invoice']
        self.partner = self.env.ref('base.res_partner_1')
        self.sequence = self.env['ir.sequence'].create({
            'name': 'Test purchases Order',
            'code': 'purchase.order',
            'prefix': 'TSO',
            'padding': 3,
        })
        self.journal = self.env['account.journal'].search(
            [('type', '=', 'purchase')], limit=1)
        self.warehouse = self.env.ref('stock.stock_warehouse_shop0')
        self.product = self.env.ref('product.product_product_4')
        self.immediate_payment = self.env.ref(
            'account.account_payment_term_immediate')
        self.purchase_pricelist = self.env.ref('product.list0')
        self.free_carrier = self.env.ref('stock.incoterm_FCA')
        self.purchase_type = self.purchase_type_model.create({
            'name': 'Test purchase Order Type',
            'sequence_id': self.sequence.id,
            'journal_id': self.journal.id,
            'warehouse_id': self.warehouse.id,
            'picking_policy': 'one',
            'payment_term_id': self.immediate_payment.id,
            'pricelist_id': self.purchase_pricelist.id,
            'incoterm_id': self.free_carrier.id,
        })
        self.partner.purchase_type = self.purchase_type

    def get_purchase_order_vals(self):
        purchase_line_dict = {
            'product_id': self.product.id,
            'name': self.product.name,
            'product_uom_qty': 1.0,
            'price_unit': self.product.lst_price,
        }
        return {
            'partner_id': self.partner.id,
            'order_line': [(0, 0, purchase_line_dict)]
        }

    def test_purchase_order_confirm(self):
        purchase_type = self.purchase_type
        order_vals = self.get_purchase_order_vals()
        order = self.purchase_order_model.create(order_vals)
        order.onchange_partner_id()
        self.assertTrue(order.type_id == purchase_type)

        order.onchange_type_id()
        self.assertTrue(order.warehouse_id == purchase_type.warehouse_id)
        self.assertTrue(order.picking_policy == purchase_type.picking_policy)
        self.assertTrue(order.payment_term_id == purchase_type.payment_term_id)
        self.assertTrue(order.pricelist_id == purchase_type.pricelist_id)
        self.assertTrue(order.incoterm == purchase_type.incoterm_id)

        order.action_confirm()

    def test_invoice_onchange_type(self):
        purchase_type = self.purchase_type
        invoice = self.invoice_model.new({'purchase_type_id': purchase_type.id})
        invoice.onchange_purchase_type_id()
        self.assertTrue(invoice.payment_term == purchase_type.payment_term_id.id)
        self.assertTrue(invoice.journal_id == purchase_type.journal_id)

    def test_invoice_onchange_partner(self):
        invoice = self.invoice_model.create({'partner_id': self.partner.id})
        invoice._onchange_partner_id()
        self.assertTrue(invoice.purchase_type_id == self.purchase_type)

    def test_prepare_invoice(self):
        purchase_type = self.purchase_type
        order_vals = self.get_purchase_order_vals()
        order_vals['type_id'] = purchase_type.id
        order = self.purchase_order_model.create(order_vals)
        invoice_vals = order._prepare_invoice()
        self.assertTrue(invoice_vals['purchase_type_id'] == purchase_type.id)
        self.assertTrue(invoice_vals['journal_id'] == purchase_type.journal_id.id)
