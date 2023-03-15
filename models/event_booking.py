from odoo import models, fields, api
from odoo.exceptions import UserError


class EventBooking(models.Model):
    _name = "event.booking"
    _description = "Event Booking"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', tracking=True,
                       default='New', store=True, compute='_compute_name')
    type_id = fields.Many2one('event.type', string='Type', default='',
                              required=True,
                              states={'Confirmed': [('readonly', True)]})
    customer_id = fields.Many2one('res.partner', string='Customer',
                                  required=True,
                                  states={'Confirmed': [('readonly', True)]})
    address = fields.Char(related="customer_id.contact_address",
                          string='Address')
    booking_date = fields.Date(string='Booking Date',
                               states={'Confirmed': [('readonly', True)]})
    start_date = fields.Date(string='Event Start Date',
                             states={'Confirmed': [('readonly', True)]})
    end_date = fields.Date(string='Event End Date', required=True,
                           states={'Confirmed': [('readonly', True)]})
    duration = fields.Integer(string='Duration', compute='_compute_duration',
                              readonly=True, store=True)
    image = fields.Binary(related='type_id.image')
    catering_id = fields.One2many('event.catering', 'event_id')
    catering_page_id = fields.Many2one('event.catering.page')
    # sale_order = fields.Many2one('sale.order')
    invoice_count = fields.Integer(compute="_compute_invoice_count")
    cat_service_count = fields.Integer(compute="_compute_cat_service_count")
    paid = fields.Boolean()
    invoice_btn_visibility = fields.Boolean()
    catering_btn_visibility = fields.Boolean()

    state = fields.Selection(selection=[
        ('Draft', 'Draft'),
        ('Confirmed', 'Confirmed'),
        ('Invoiced', 'Invoiced'),
        ('Paid', 'Paid')
    ], string='State', required=True, readonly=True, copy=False,
        tracking=True, default='Draft')

    @api.depends('type_id', 'customer_id', 'start_date', 'end_date')
    def _compute_name(self):
        for record in self:
            print(record.type_id)
            print(record.customer_id)
            print(record.start_date)
            print(record.end_date)
            if record.type_id and record.customer_id and record.start_date \
                    and record.end_date:
                record.name = "%s: " % record.type_id.name \
                              + "%s / " % record.customer_id.name \
                              + "%s:" % record.start_date \
                              + "%s" % record.end_date
            else:
                record.name = 'New'

    @api.depends('end_date', 'start_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                diff = record.end_date - record.start_date
                record.duration = diff.days + 1
            else:
                record.duration = 0

    @api.onchange('end_date')
    def end_date_check(self):
        if self.end_date < self.start_date:
            raise UserError('Sorry, End date must be greater than start date')

    def action_open_catering_form(self):
        self.invoice_btn_visibility = True
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'event.catering',
            'view_id': self.env.ref('event_management.event_catering_form').id,
            'context': {'default_event_id': self.id,
                        'default_booking_date_catering': self.booking_date,
                        'default_start_date_catering': self.start_date,
                        'default_end_date_catering': self.end_date,
                        'default_boolean': True}
        }

    def action_confirm(self):
        self.state = 'Confirmed'
        self.catering_id.state = 'confirmed'

    def action_open_invoice(self):
        print(self.id, 'ooo')
        self.invoice_btn_visibility = False
        self.catering_btn_visibility = True
        catering = self.env['event.catering'].search(
            [('event_id', '=', self.id)])
        print(catering, 'aa')
        list1 = []
        for record in catering.welcome_drink_table_ids + \
                catering.breakfast_table_ids + \
                catering.lunch_table_ids + \
                catering.snacks_drinks_table_ids + \
                catering.beverage_table_ids +\
                catering.dinner_table_ids:
            vals = {
                'name': record.item_id.name,
                'quantity': record.quantity,
                'price_unit': record.item_id.unit_price,
                'price_subtotal': record.subtotal
            }
            vals = (0, 0, vals)
            list1.append(vals)

        # for record in catering.welcome_drink_table_ids + \
        #         catering.breakfast_table_ids + \
        #         catering.lunch_table_ids + \
        #         catering.snacks_drinks_table_ids + \
        #         catering.dinner_table_ids + \
        #         catering.beverage_table_ids:
        #     print(record.item_id.id, 'item')
        #     print(record, 'rec')
        #     vals = {
        #         'name': record.item_id.name,
        #         'quantity': record.quantity,
        #         'price_unit': record.item_id.unit_price,
        #         'price_subtotal': record.subtotal
        #     }
        #     vals = (0, 0, vals)
        #     list1.append(vals)
        #     print(list1)



        # for record in catering.welcome_drink_table_ids:
        #     print(record.item_id.id, 'item')
        #     print(record, 'rec')
        #     vals = {
        #         'name': record.item_id.name,
        #         'quantity': record.quantity,
        #         'price_unit': record.item_id.unit_price,
        #         'price_subtotal': record.subtotal
        #     }
        #     vals = (0, 0, vals)
        #     list1.append(vals)

        # for record in catering.breakfast_table_ids:
        #     print(record.item_id.id, 'item')
        #     vals = {
        #         'name': record.item_id.name,
        #         'quantity': record.quantity,
        #         'price_unit': record.item_id.unit_price,
        #         'price_subtotal': record.subtotal
        #     }
        #     vals = (0, 0, vals)
        #     list1.append(vals)
        #
        # for record in catering.lunch_table_ids:
        #     print(record.item_id.name, 'item')
        #     vals = {
        #         'name': record.item_id.name,
        #         'quantity': record.quantity,
        #         'price_unit': record.item_id.unit_price,
        #         'price_subtotal': record.subtotal
        #     }
        #     vals = (0, 0, vals)
        #     list1.append(vals)
        #
        # for record in catering.snacks_drinks_table_ids:
        #     print(record.item_id.name, 'item')
        #     vals = {
        #         'name': record.item_id.name,
        #         'quantity': record.quantity,
        #         'price_unit': record.item_id.unit_price,
        #         'price_subtotal': record.subtotal
        #     }
        #     vals = (0, 0, vals)
        #     list1.append(vals)
        #
        # for record in catering.dinner_table_ids:
        #     print(record.item_id.name, 'item')
        #     vals = {
        #         'name': record.item_id.name,
        #         'quantity': record.quantity,
        #         'price_unit': record.item_id.unit_price,
        #         'price_subtotal': record.subtotal
        #     }
        #     vals = (0, 0, vals)
        #     list1.append(vals)
        #
        # for record in catering.beverage_table_ids:
        #     print(record.item_id.name, 'item')
        #     vals = {
        #         'name': record.item_id.name,
        #         'quantity': record.quantity,
        #         'price_unit': record.item_id.unit_price,
        #         'price_subtotal': record.subtotal
        #     }
        #     vals = (0, 0, vals)
        #     list1.append(vals)

        print('list:', list1)
        print(self.customer_id.id, 'k')
        print(self.customer_id.id, 'k')

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'partner_id': self.customer_id.id,
            'catering_id': self.id,
            'payment_reference': self.name,
            'event_name_id': self.id,
            'invoice_line_ids': list1
        })
        # print(record.welcome_drink_table_ids, 'wel')
        print(self.name, 'id')

        return {
            'name': 'Invoice',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_id': invoice.id
        }

    def get_invoice(self):
        print(self.name, 'event')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('payment_reference', '=', self.name)],
            'context': "{'create': False}"
        }

    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count(
                [('payment_reference', '=', self.name)])
            print(record.invoice_count, 'count')

    def get_catering_service(self):
        print(self.name, 'event')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Catering Service',
            'view_mode': 'tree,form',
            'res_model': 'event.catering',
            'domain': [('event_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def _compute_cat_service_count(self):
        for record in self:
            record.cat_service_count = self.env['event.catering'].search_count(
                [('event_id', '=', self.id)])
            print(record.cat_service_count, 'count')
