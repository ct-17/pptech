from openerp import models, fields, api
from openerp.tools.float_utils import float_round


class DPOrderMarkupWizard(models.TransientModel):
    _name = "dp.order.markup.wizard"

    type = fields.Selection([('amount', 'Fixed Amount'), ('percent', 'Percentage')],
                            required=True, default='percent')
    amount = fields.Float('Fixed Amount', required=True)
    percent = fields.Integer('Percentage', required=True)


    @api.multi
    def confirm(self):
        active_model = self._context.get('active_model', False)
        active_id = self._context.get('active_id', False)
        remaining_discount_amount = 0
        if active_model and active_id:
            sale_obj = self.env[active_model].browse(active_id)
            if sale_obj.exists():
                total_price = sum([line.price_subtotal for line in sale_obj.order_line])

                sale_obj.is_global_markup = True
                sale_obj.global_markup_type = self.type
                sale_obj.global_markup_percent = self.percent
                sale_obj.global_markup_amount = self.amount

                markup_amount = (self.percent / 100.0 * sale_obj.amount_total) or self.amount
                for line in getattr(sale_obj, 'order_line'):

                    line.mark_up_global_amount = float_round((markup_amount * line.price_subtotal / total_price if total_price != 0.0 else 1) / line.product_uom_qty, 2)
                    remaining_discount_amount += line.mark_up_global_amount * line.product_uom_qty
                line.mark_up_global_amount = markup_amount - (remaining_discount_amount - line.mark_up_global_amount)
        return True

    @api.multi
    def remove(self):
        active_model = self._context.get('active_model', False)
        active_id = self._context.get('active_id', False)
        if active_model and active_id:
            sale_obj = self.env[active_model].browse(active_id)
            if sale_obj.exists():
                sale_obj.is_global_markup = False
                sale_obj.global_markup_type = self.type
                sale_obj.global_markup_amount = 0
                sale_obj.global_markup_percent = 0

    @api.model
    def recompute_markup(self):
        active_model = self.env.context.get('active_model')
        obj = self.env[active_model].browse(self.env.context.get('active_id'))
        if obj.global_markup_type:
            wiz = self.create({
                'type': obj.global_markup_type,
                'amount': obj.global_markup_amount,
                'percent': obj.global_markup_percent
            })
            return wiz.confirm()
        else:
            if active_model in ('sale.order', 'purchase.order'):
                obj.order_line.write({'mark_up_global_amount': 0})
            if active_model == 'account.invoice':
                obj.invoice_line.write({'mark_up_global_amount': 0})
        return True
