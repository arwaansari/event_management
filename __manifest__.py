{
    'name': 'Event Management',
    'sequence': '-1',
    'version': '16.0.1.0.0',
    'installable': True,
    'application': True,

    'depends': ['base', 'mail', 'sale', 'account'],
    'assets': {
        'web.assets_backend': [
            'event_management/static/src/js/event_report_xlsx.js'
        ],
        'web.assets_frontend': [
            'event_management/static/src/js/website.js'
        ]
    },
    'data': ['security/ir.model.access.csv',
             'wizard/report_wizard_view.xml',
             'data/website_menu.xml',
             'data/event_type_data.xml',
             'reports/event_report.xml',
             'views/event_type.xml',
             'views/event_booking.xml',
             'views/event_service.xml',
             'views/event_service_table.xml',
             'views/catering.xml',
             'views/catering_menu.xml',
             'views/account_move_view.xml',
             'views/website_template.xml',
             'views/success_template.xml',
             'views/portal_view.xml',
             'views/event_menu.xml']
}
