from odoo import http
from odoo.http import request


class WebsiteForm(http.Controller):
    @http.route(['/booking'], type='http', auth="user", website=True)
    def event_booking(self):
        event_types = request.env['event.type'].sudo().search([])
        partners = request.env['res.partner'].sudo().search([])
        values = {}
        values.update({
            'partners': partners,
            'event_types': event_types
        })
        print(values)
        return request.render("event_management.online_event_booking_form",
                              values)

    @http.route(['/booking/submit'], type='http', auth="user", website=True)
    def submit(self, **kwargs):
        partner = request.env['res.partner'].sudo().search([
            ('id', '=', kwargs.get('partner_id'))]).name
        event_type = request.env['event.type'].sudo().search([
            ('id', '=', kwargs.get('event_type_id'))]).name
        name = "%s: " % event_type + \
               "%s / " % partner \
               + "%s:" % kwargs.get('from_date') \
               + "%s" % kwargs.get('to_date')
        # print(type(kwargs.get('partner_id')))
        duration = kwargs.get('to_date')
        print(type(kwargs.get('to_date')), 'from')
        print(kwargs.get('from_date'), 'to')
        request.env['event.booking'].sudo().create([{
            'name': name,
            'customer_id': int(kwargs.get('partner_id')),
            'type_id': int(kwargs.get('event_type_id')),
            'booking_date': kwargs.get('booking_date'),
            'start_date': kwargs.get('from_date'),
            'end_date': kwargs.get('to_date'),
            'duration': kwargs.get('duration')

        }])
        print('kkkkkkkk')
        return request.render("event_management.website_success_template")
