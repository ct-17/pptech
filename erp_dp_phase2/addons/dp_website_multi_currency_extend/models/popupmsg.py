from openerp import fields, models, api


class PopupMsg(models.TransientModel):
    _name = 'sale.order.popup.msg'

    link_id = fields.Many2one('sale.order', string='Sale Order')
    msg = fields.Text(string="Infomation")

    @api.multi
    def confirm_run(self):
        ctx = self.env.context
        if ctx.get('active_id') and not self.link_id:
            sale_obj = self.env[ctx.get('model')].browse(ctx.get('active_id'))
            if sale_obj.state == 'chandler_draft':
                return sale_obj.with_context(approved=True).action_dp_quotation_send()
            else:
                # assume is in quotation_sent state
                return sale_obj.with_context(approved=True).action_dp_quotation_send_again()

    # @api.multi
    # def confirm_run_shipmaster(self):
    #     ctx = self.env.context
    #     if ctx.get('active_id') and not self.link_id:
    #         sale_obj = self.env[ctx.get('model')].browse(ctx.get('active_id'))
    #         return sale_obj.with_context(approved=True).bid_confirm_order()