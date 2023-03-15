from odoo import models, fields, api


class Catering(models.Model):
    _name = 'event.catering'
    _description = 'Event Catering'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    event_id = fields.Many2one('event.booking', string="Event", required=True,
                               states={'confirmed': [('readonly', True)]})
    booking_date = fields.Date(related='event_id.booking_date',
                               string='Booking Date')
    start_date = fields.Date(related='event_id.start_date',
                             string='Event Start Date')
    end_date = fields.Date(related='event_id.end_date',
                           string='Event End Date')
    guest = fields.Integer(string="Guests", help="Number of guests",
                           states={'confirmed': [('readonly', True)]})
    welcome_drink = fields.Boolean(string="Welcome Drink",
                                   states={'confirmed': [('readonly', True)]})
    breakfast = fields.Boolean(string="Breakfast",
                               states={'confirmed': [('readonly', True)]})
    lunch = fields.Boolean(string="Lunch",
                           states={'confirmed': [('readonly', True)]})
    dinner = fields.Boolean(string="Dinner",
                            states={'confirmed': [('readonly', True)]})
    snacks_and_drinks = fields.Boolean(string="Snacks and Drinks", states={
        'confirmed': [('readonly', True)]})
    beverages = fields.Boolean(string="Beverages",
                               states={'confirmed': [('readonly', True)]})
    name = fields.Char(string='Sequence', required=True, readonly=True,
                       default='New',
                       states={'confirmed': [('readonly', True)]})
    grand_total = fields.Float(string="Grand Total", compute="_grand_total",
                               store=True)
    boolean = fields.Boolean()
    booking_id = fields.Many2one()

    welcome_drink_table_ids = fields.One2many('event.catering.page',
                                              'catering_wd_id',
                                              states={'confirmed': [
                                                  ('readonly', True)]})
    breakfast_table_ids = fields.One2many('event.catering.page',
                                          'catering_br_id',
                                          states={'confirmed': [
                                              ('readonly', True)]})
    lunch_table_ids = fields.One2many('event.catering.page', 'catering_lu_id',
                                      states={
                                          'confirmed': [('readonly', True)]})
    dinner_table_ids = fields.One2many('event.catering.page', 'catering_di_id',
                                       states={
                                           'confirmed': [('readonly', True)]})
    beverage_table_ids = fields.One2many('event.catering.page',
                                         'catering_bv_id',
                                         states={'confirmed': [
                                             ('readonly', True)]})
    snacks_drinks_table_ids = fields.One2many('event.catering.page',
                                              'catering_sd_id',
                                              states={'confirmed': [
                                                  ('readonly', True)]})
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('invoiced', 'Invoiced'),
        ('expired', 'Expired'),
    ], string='State', required=True, readonly=True, copy=False,
        tracking=True, default='draft')

    @api.depends('welcome_drink_table_ids.subtotal',
                 'breakfast_table_ids.subtotal', 'lunch_table_ids.subtotal',
                 'beverage_table_ids.subtotal',
                 'snacks_drinks_table_ids.subtotal',
                 'dinner_table_ids.subtotal')
    def _grand_total(self):
        for record in self:
            record.grand_total = sum(
                record.welcome_drink_table_ids.mapped('subtotal') +
                record.breakfast_table_ids.mapped('subtotal') +
                record.lunch_table_ids.mapped('subtotal') +
                record.snacks_drinks_table_ids.mapped('subtotal') +
                record.dinner_table_ids.mapped('subtotal') +
                record.beverage_table_ids.mapped('subtotal'))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New' == 'New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'event.catering')
        res = super(Catering, self).create(vals)
        return res

    def action_confirm(self):
        self.write({'state': "confirmed"})

    def action_deliver(self):
        self.write({'state': "delivered"})

    def expiry(self):
        """Draft state records will automatically move to expired state
        if start date is over"""

        self.search(
                [('state', '!=', 'expired'), ('start_date', '<=',
                 fields.Datetime.today())]).write({'state': 'expired'})
