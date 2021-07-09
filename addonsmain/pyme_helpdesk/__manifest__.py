# -*- coding: utf-8 -*-
{
    'name': "OPENERP -- Tickets",
    'version': "1.1.1",
    'author': "Main Informática Gandia , S.L.",
    'category': "Tools",
    'support': "jtormo@main-informatica.com",
    'summary': "HelpDesk / Sistema de Tickets",
    'description': """
        Sistema de Tickets Simple
		Basado en el HelpDesk de golubev@svami.in.ua
    """,
    'license':'LGPL-3',

    'data': [
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
        'views/helpdesk_tickets.xml',
        'views/helpdesk_team_views.xml',
        'views/helpdesk_stage_views.xml',
        'views/helpdesk_data.xml',
        'views/helpdesk_templates.xml',
        'views/project_task.xml',
        'views/email_message.xml',

    ],
    'demo': [
        'demo/helpdesk_demo.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'depends': ['base', 'mail', 'portal','project','pyme_emails', 'pyme_partner_extra',],
    'application': False,
}
