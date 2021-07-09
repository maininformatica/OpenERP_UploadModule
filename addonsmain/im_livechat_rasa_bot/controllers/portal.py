# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        # domain is needed to hide non portal project for employee
        # portal users can't see the privacy_visibility, fetch the domain for them in sudo
        userid = request.session.uid
        partnerid = request.env['res.users'].search([('id', '=', userid)])
        print("Pues esto es lo que veo: " + str(userid) + "y partner: " + str(partnerid.partner_id.id))
        channel_count = request.env['mail.channel'].search_count([('chatuser', '=', partnerid.partner_id.id)])
        values.update({
            'channel_count': channel_count,
        })
        return values

    @http.route(['/my/messages', '/my/messages/page/<int:page>'], type='http', auth="user", website=True)
    def my_messages(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', **kw):
        groupby = 'none'  # kw.get('groupby', 'project') #TODO master fix this
        values = self._prepare_portal_layout_values()        

        searchbar_sortings = {
            'date': {'label': _('Más Nuevo'), 'order': 'create_date desc'},
            'date2': {'label': _('Más Antiguo'), 'order': 'create_date'},
        }

        searchbar_inputs = {
            'All': {'input': 'content', 'label': _('Mensaje Contiene...')},
		}
        searchbar_filters = {
            'All': {'label': _('Todos'), 'domain': []},
        }
        
        domain = ([])


        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content'):
                search_domain = OR([search_domain, [('channel_message_ids.body', 'ilike', search)]])
            domain += search_domain

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'All'
        domain += searchbar_filters[filterby]['domain']


        channel_count = request.env['mail.channel'].search_count([])
        pager = request.website.pager(
            url="/my/messages",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            # url_args={'date_begin': date_begin, 'date_end': date_end},
            total=channel_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        messages_user = request.env['mail.channel'].search(domain, order=order, limit=None, offset=None)
        userid = request.session.uid
        chatpartnerid = request.env['res.users'].search([('id', '=', userid )]).partner_id.id
        print ("USER: " + str(userid) + ". Part: " + str(chatpartnerid) + ".")
        values.update({
            'msgchan': messages_user,
            ## 'current_user': 19,
            'current_user': chatpartnerid,
            'page_name': 'messages',
            'default_url': '/my/messages',
            ## 'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("im_livechat_rasa_bot.portal_my_messages", values)

    @http.route(['/my/messages/<int:msgid>'], type='http', auth="user", website=True)
    def my_messages_messages(self, msgid=None, **kw):
        msgids = request.env['mail.channel'].browse(msgid)
        return request.render("im_livechat_rasa_bot.my_messages_messages", {'msgids': msgids})
        