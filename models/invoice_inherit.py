from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    catering_id = fields.Many2one('event.catering')
    event_name_id = fields.Many2one('event.booking')

    def action_post(self):
        print('confirm invoice')
        res = super(AccountMove, self).action_post()
        print(self.env['event.catering'].search(
            [('event_id', '=', self.event_name_id.id)]))
        self.env['event.catering'].search(
            [('event_id', '=', self.event_name_id.id)]).state = 'invoiced'
        self.event_name_id.state = 'Invoiced'
        return res

    @api.constrains('payment_state')
    def _compute_paid(self):
        for record in self:
            # print(record.payment_state)
            if record.payment_state == 'paid':
                record.event_name_id.paid = True
                record.event_name_id.state = 'Paid'
