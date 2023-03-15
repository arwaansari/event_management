from odoo import models, fields, api


class CateringPage(models.Model):
    _name = 'event.catering.page'
    _description = 'Event Catering Page'

    item_id = fields.Many2one('event.catering.menu')
    description = fields.Char()
    quantity = fields.Float(default=1)
    uom_id = fields.Many2one('uom.uom', string="UoM")
    unit_price = fields.Float()
    subtotal = fields.Float(compute="_compute_subtotal", store=True)
    catering_wd_id = fields.Many2one('event.catering')
    catering_br_id = fields.Many2one('event.catering')
    catering_lu_id = fields.Many2one('event.catering')
    catering_sd_id = fields.Many2one('event.catering')
    catering_di_id = fields.Many2one('event.catering')
    catering_bv_id = fields.Many2one('event.catering')
    catering_id = fields.Many2one('event.catering')

    @api.onchange('item_id')
    def _onchange_item_id(self):
        self.unit_price = self.item_id.unit_price
        self.uom_id = self.item_id.uom_id.id

    @api.depends('unit_price', 'quantity')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.unit_price * record.quantity
