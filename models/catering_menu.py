from odoo import models, fields


class CateringMenu(models.Model):
    _name = 'event.catering.menu'
    _description = 'Catering Menu'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    category = fields.Selection(string='Category',
                                selection=[('welcome_drink', 'Welcome Drink'),
                                           ('breakfast', 'Breakfast'),
                                           ('lunch', 'Lunch'),
                                           ('dinner', 'Dinner'),
                                           ('snacks_and_drinks',
                                            'Snacks and Drinks'),
                                           ('beverages', 'Beverages')])
    image = fields.Image()
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure")
    unit_price = fields.Integer(string="Unit Price")
