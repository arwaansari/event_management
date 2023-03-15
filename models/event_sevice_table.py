from odoo import models, fields, api


class ServiceTable(models.Model):
    _name = 'event.service.table'
    _description = 'Service Table'

    description = fields.Text(string="Description")
    quantity = fields.Integer(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    subtotal = fields.Float(compute="_compute_subtotal")
    total = fields.Float()

    service_id = fields.Many2one('event.service')

    @api.depends('unit_price', 'quantity')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.unit_price * record.quantity
