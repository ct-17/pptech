# __author__ = 'BinhTT'

from openerp import models, fields, api
from openerp.exceptions import ValidationError

class sale_global_discount_wizard(models.TransientModel):
    _inherit = "global_discount.wizard"


    @api.multi
    def confirm(self):
        self.ensure_one()
        model = self._context.get('active_model')
        order = self.env[model].browse(
            self._context.get('active_id', False))
        line_attr = ''
        if self.env.context.get('active_model') in ('purchase.order', 'sale.order'):
            line_attr = 'order_line'
            if not order.order_line.ids:
                raise ValidationError('You cannot set discount whole bill for order without product')
        elif model == 'account.invoice':
            line_attr = 'invoice_line'
            if not order.invoice_line.ids:
                raise ValidationError('You cannot set discount whole bill for invoice without product')
        else:
            raise ValidationError('You cannot set discount whole bill for %s object' % model)

        discount_amount = 0.0
        if self.type == 'amount':
            discount_amount = self.amount
        if self.type == 'percent':
            if model == 'account.invoice':
                discount_amount = self.percent * sum([line.price_subtotal for line in order.invoice_line]) / 100
            else:
                discount_amount = self.percent * sum([line.price_subtotal for line in order.order_line]) / 100

        vals = {'ws_discount_percent': self.percent,
                'ws_discount_type': self.type}
        if model != 'account.invoice':
            vals.update(ws_discount_amount=discount_amount)

        order.write(vals)

        if model == 'sale.order':
            total_price = sum([line.chandler_price_subtotal for line in order.order_line])
        elif model == 'purchase.order':
            total_price = sum([line.price_subtotal for line in order.order_line])
        else:
            total_price = sum([line.price_subtotal for line in order.invoice_line])

        remaining_discount_amount = discount_amount
        line = None
        for line in getattr(order, line_attr):
            try:
                if line.item_type or line.price_unit == 0:
                    line.ws_discount = 0.0
                    continue
            except:
                pass
            # if model == 'sale.order':
            #     line.ws_discount = discount_amount * line.price_subtotal / total_price
            # elif model == 'purchase.order':
            #     line.ws_discount = discount_amount * line.price_subtotal / total_price
            # else:
            #     line.ws_discount = discount_amount * line.price_subtotal / total_price
            # else:
            if model != 'sale.order':
                line.ws_discount = discount_amount * line.price_subtotal / total_price
            else:
                line.ws_discount = discount_amount * line.chandler_price_subtotal / total_price

            remaining_discount_amount -= line.ws_discount
        line.ws_discount += remaining_discount_amount

        return True