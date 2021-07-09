# -*- coding: utf-8 -*-
from openerp import http

class website_maininformatica_block(http.Controller):
    @http.route('/website_maininformatica_block/website_maininformatica_block/', auth='public', website='true')
    def index(self, **kw):
        Teachers = http.request.env['crm.phonecall']
        return http.request.render('website_maininformatica_block.index', {
            'teachers': Teachers.search([])
        })