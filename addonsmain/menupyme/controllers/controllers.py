# -*- coding: utf-8 -*-
from openerp import http

# class Menupyme(http.Controller):
#     @http.route('/menupyme/menupyme/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/menupyme/menupyme/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('menupyme.listing', {
#             'root': '/menupyme/menupyme',
#             'objects': http.request.env['menupyme.menupyme'].search([]),
#         })

#     @http.route('/menupyme/menupyme/objects/<model("menupyme.menupyme"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('menupyme.object', {
#             'object': obj
#         })