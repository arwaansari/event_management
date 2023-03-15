from odoo import models, fields, api


class EventService(models.Model):
    _name = 'event.service'
    _description = 'Event Services'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    responsible_person_id = fields.Many2one('res.users',
                                            default=lambda self: self.env.user)

    table_id = fields.One2many('event.service.table', 'service_id')
