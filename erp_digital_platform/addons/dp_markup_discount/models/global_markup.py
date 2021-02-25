from openerp import models, fields, api
from openerp.tools.float_utils import float_round


class DPOrderMarkupWizard(models.TransientModel):
    _inherit = "dp.order.markup.wizard"

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

                markup_amount = (self.percent / 100.0 * sale_obj.total_before_discount) or self.amount
                for line in getattr(sale_obj, 'order_line'):

                    line.mark_up_global_amount = float_round((markup_amount * line.price_subtotal / total_price if total_price != 0.0 else 1) / line.product_uom_qty, 2)
                    remaining_discount_amount += line.mark_up_global_amount * line.product_uom_qty
                line.mark_up_global_amount = markup_amount - (remaining_discount_amount - line.mark_up_global_amount)
        return True

