from odoo import models, fields, http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class EventManagement(models.Model):
    _name = 'event.type'
    _description = 'Event Types'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    code = fields.Char()
    image = fields.Binary()


class EventBookingPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        count = request.env['event.booking'].\
            search_count([('customer_id', '=', partner.id)])
        if 'booking_count' in counters:
            values['booking_count'] = count
        return values
        print(counters)
        print(values)

    @http.route(['/my/bookings'], type='http', auth="user", website=True)
    def event_booking_view(self):
        partner = request.env.user.partner_id
        bookings = request.env['event.booking'].sudo().\
            search([('customer_id', '=', partner.id)])
        values = {}
        values.update({
            'partners': partner,
            'bookings': bookings
        })
        return request.render('event_management.portal_my_event_bookings', values)

