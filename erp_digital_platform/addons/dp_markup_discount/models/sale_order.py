from datetime import datetime
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
from openerp.osv import fields as old_fields


class DPMarkupDiscountSaleOrder(models.Model):
    _inherit = "sale.order"

    # amount_tax = fields.Float(compute='_compute_all_price', digits= dp.get_precision("Account"),
    #                         string="Taxes", store=True, help="The amount without tax.")
    # amount_untaxed = fields.Float(compute='_compute_all_price', digits= dp.get_precision("Account"),
    #                         string="Untaxed Amount", store=True, help="The amount without tax.")
    # amount_total = fields.Float(compute='_compute_all_price', digits= dp.get_precision("Account"),
    #                         string="Total", store=True, help="The total amount.")
    # margin = fields.Float(compute='ess_product_margin', store=True)
    is_discounted = fields.Boolean(compute="_check_discount_more_than_zero")

    @api.multi
    @api.depends('amount_discount')
    def _check_discount_more_than_zero(self):
        for rec in self:
            rec.is_discounted = False
            if isinstance(rec.amount_discount, float):
                if rec.amount_discount > 0:
                    rec.is_discounted = True


    def ess_product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}

        for record in self.pool.get('sale.order').browse(cr, uid, ids, context=context):
            res[record.id] = {'margin': 0.0}
            margin = 0
            for line in record.order_line:
                if line.state == 'cancel':
                    continue
                margin += line.chandler_price_subtotal - line.ws_discount + (
                            line.product_uom_qty * line.mark_up_global_amount) \
                                 - (line.purchase_price * line.product_uom_qty)
            res[record.id]['margin'] = margin
        return res


    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    _columns = {
        'amount_untaxed': old_fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'),
                                              string='Untaxed Amount',
                                              store={
                                                  'sale.order': (
                                                      lambda self, cr, uid, ids, ctx: ids, ['order_line'], 10),
                                                  'sale.order.line': (
                                                      _get_order,
                                                      ['price_unit', 'tax_id', 'discount', 'product_uom_qty',
                                                       'ws_discount', 'price_subtotal', 'mark_up_global_amount', 'purchase_price'], 10),
                                              },
                                              multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': old_fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'),
                                          string='Taxes',
                                          store={
                                              'sale.order': (lambda self, cr, uid, ids, ctx: ids, ['order_line'], 10),
                                              'sale.order.line': (
                                                  _get_order,
                                                  ['price_unit', 'tax_id', 'discount', 'product_uom_qty', 'ws_discount',
                                                   'price_subtotal', 'mark_up_global_amount', 'purchase_price'], 10),
                                          },
                                          multi='sums', help="The tax amount."),
        'amount_total': old_fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'),
                                            string=' Grand Total',
                                            store={
                                                'sale.order': (
                                                    lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                                'sale.order.line': (
                                                    _get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty',
                                                                 'ws_discount', 'price_subtotal', 'mark_up_global_amount'], 10),
                                            },
                                            multi='sums', help=""),
        'margin': old_fields.function(ess_product_margin, string='Margin',
                                      help="It gives profitability by calculating the difference between the Unit Price and the cost price.",
                                      store={
                                          'sale.order.line': (
                                          _get_order, ['margin', 'purchase_price', 'order_id', 'ws_discount',
                                                       'mark_up_global_amount', 'discount'], 20),
                                          'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 20),
                                      }, digits_compute=dp.get_precision('Product Price'), multi='sums'),
                                          }
    ess_margin = fields.Float(compute='_compute_all_price', store=False, string='Margin', digits_compute=dp.get_precision('Account'))
    ess_net_margin = fields.Float(compute='_compute_all_price', store=False, string='Margin', digits_compute=dp.get_precision('Account'))

    @api.multi
    @api.depends('order_line')
    def _compute_all_price(self):
        # overwrite function in np_discount
        for r in self:
            r.amount_tax = sum([line.tax_amount for line in r.order_line])
            r.amount_untaxed = sum([line.chandler_price_subtotal - line.ws_discount + (line.product_uom_qty*line.mark_up_global_amount) for line in r.order_line])
            r.total_before_discount = sum([line.chandler_price_subtotal for line in r.order_line])
            r.amount_total = r.amount_untaxed + r.amount_tax
            r.amount_discount = sum([line.ws_discount for line in r.order_line])
            r.ess_margin = sum([line.chandler_price_subtotal
                                 - (line.purchase_price * line.product_uom_qty) for line in r.order_line])
            r.ess_net_margin = r.ess_margin - r.amount_discount

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        # overwrite function in np_discount
        res = super(DPMarkupDiscountSaleOrder, self)._amount_all(cr, uid, ids, field_name, arg, context=context)

        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal - line.ws_discount + (line.product_uom_qty*line.mark_up_global_amount)
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    # @api.depends('order_line.margin', 'order_line.purchase_price', 'order_line.order_id', 'order_line.price_unit', 'order_line.tax_id',
    #              'order_line.discount', 'order_line.product_uom_qty',
    #              'order_line.ws_discount', 'order_line.price_subtotal', 'order_line.mark_up_global_amount')
    # @api.model
    # def ess_product_margin(self):
    #     for record in self:
    #         record.margin = 0
    #         for line in record.order_line:
    #             if line.state == 'cancel':
    #                 continue
    #             record.margin += line.price_subtotal - line.ws_discount + (line.product_uom_qty*line.mark_up_global_amount) \
    #                         - (line.purchase_price * line.product_uom_qty)

    @api.multi
    def write(self, vals):
        res = super(DPMarkupDiscountSaleOrder, self).write(vals)
        if self.env.context.get('need_recompute_discount') and self.order_line:
            self.env['dp.order.markup.wizard'].with_context(
                active_ids=self.ids,
                active_id=self.ids[0],
                active_model=self._name,
                need_recompute_discount=False
            ).recompute_markup()
        return res