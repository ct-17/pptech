# __author__ = 'BinhTT'

from openerp import models, fields, api
from openerp.osv import fields as old_fields
import openerp.addons.decimal_precision as dp


class NpPurchase(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    @api.depends('order_line')
    def _compute_all_price(self):
        for r in self:
            total_amount = 0.0
            line_discount_amount = 0.0
            amount_tax = 0.0
            # total_amount = sum([line.price_subtotal for line in r.order_line])
            # r.line_discount_amount = sum([line.discount_amount for line in r.order_line])
            r.amount_tax = sum([line.tax_amount for line in r.order_line])
            r.amount_untaxed = sum([line.price_subtotal - line.ws_discount for line in r.order_line])
            r.total_before_discount = sum([line.price_unit * line.product_qty for line in r.order_line])
            r.amount_total = r.amount_untaxed + r.amount_tax
            r.amount_discount = r.total_before_discount - r.amount_untaxed

    # discount_rate = fields.Float(string='Discount Total', digits_compute=dp.get_precision('Account'),
    #                              readonly=True,
    #                              states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    # discount_amount = fields.Float(string='Discount Total', digits_compute=dp.get_precision('Account'),
    #                                   readonly=True,
    #                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    # discount_id = fields.Many2one('global_discount.wizard')

    # total_before_discount = fields.Float(string='Total Amount before Discount',
    #                                      digits_compute=dp.get_precision('Account'),
    #                                      readonly=True,
    #                                      states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    total_before_discount = fields.Float(string='Total Amount',
                                         digits=dp.get_precision('Account'),
                                         compute='_compute_all_price', store=True)

    # untax_discount = fields.Float(string='Discount Amount', digits_compute=dp.get_precision('Account'),
    #                               readonly=True, compute='_compute_discount')

    ws_discount_type = fields.Selection(selection=[('amount', 'Fixed Amount'), ('percent', 'Percentage')],
                                        string='Whole Bill Discount Type', readonly=True)
    ws_discount_amount = fields.Float(string='Whole Bill Discount', digits=dp.get_precision('Account'),
                                      readonly=True)
    ws_discount_percent = fields.Float(string='Whole Bill Discount (%)', digits=dp.get_precision('Discount'),
                                       readonly=True)

    # amount_untaxed = fields.Float(string='Untaxed Amount', digits=dp.get_precision('Account'),
    #                               compute='_compute_all_price', store=False,
    #                               help='The Amount after discount and without tax')
    # amount_tax = fields.Float(string='Taxes', digits=dp.get_precision('Account'), compute='_compute_all_price',
    #                           help='The Tax Amount base on Total Amount after discount', store=False)
    # amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
    #                             compute='_compute_all_price', store=False)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        line_obj = self.pool['purchase.order.line']
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal - line.ws_discount
                line_price = line_obj._calc_line_base_price(cr, uid, line,
                                                            context=context)
                line_qty = line_obj._calc_line_quantity(cr, uid, line,
                                                        context=context)
                for c in self.pool['account.tax'].compute_all(
                        cr, uid, line.taxes_id, line_price * line_qty - line.ws_discount, 1,
                        line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {

        'amount_untaxed': old_fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                              string='Untaxed Amount',
                                              store={
                                                  'purchase.order.line': (_get_order, None, 10),
                                              }, multi="sums", help="", track_visibility='always'),
        'amount_tax': old_fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
                                          store={
                                              'purchase.order.line': (_get_order, None, 10),
                                          }, multi="sums", help="The tax amount"),
        'amount_total': old_fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Grand Total',
                                            store={
                                                'purchase.order.line': (_get_order, None, 10),
                                            }, multi="sums", help="")
    }

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None):
        res = super(NpPurchase, self)._prepare_order_line_move(
            cr, uid, order, order_line, picking_id, group_id, context
        )
        price_unit = order_line.final_price_unit
        if order_line.taxes_id:
            taxes = self.pool['account.tax'].compute_all(cr, uid, order_line.taxes_id, price_unit, 1.0,
                                                         order_line.product_id, order.partner_id)
            price_unit = taxes['total']
        if order_line.product_uom.id != order_line.product_id.uom_id.id:
            price_unit *= order_line.product_uom.factor / order_line.product_id.uom_id.factor
        if order.currency_id.id != order.company_id.currency_id.id:
            # we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id,
                                                               order.company_id.currency_id.id, price_unit, round=False,
                                                               context=context)

        for vals in res:
            vals.update(price_unit=price_unit)

        return res

    # @api.one
    # @api.depends('discount_rate')
    # def _compute_discount(self):
    #     self.untax_discount = self.total_before_discount - self.amount_untaxed


class NpPurchaseLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    @api.depends('discount', 'price_unit', 'product_qty')
    def _compute_all_price(self):
        for r in self:
            # r.price_subtotal_discount_line = r.price_unit * r.product_qty * (1 - r.discount / 100)
            r.discount_amount_line = r.price_unit * r.product_qty * r.discount / 100
            # r.price_subtotal = self._calc_line_base_price(r) * r.product_qty - r.ws_discount
            r.tax_amount = sum([tax['amount'] for tax in r.taxes_id.compute_all(r.price_subtotal, 1,
                                                                                r.order_id.partner_id)['taxes']])

    @api.multi
    @api.depends('ws_discount', 'discount_amount_line')
    def _compute_discount_price(self):
        for r in self:
            r.discount_amount = r.ws_discount + r.discount_amount_line

    @api.multi
    @api.depends('price_unit', 'ws_discount', 'discount', 'product_qty')
    def _compute_final_price_unit(self):
        for r in self:
            r.final_price_unit = (r.price_unit * r.product_qty * (1 - r.discount / 100) - r.ws_discount) /r.product_qty

    discount = fields.Float(string='Discount (%)', igits=dp.get_precision('Discount'),
                            readonly=True, states={'draft': [('readonly', False)]})

    # total_bf_discount = fields.Float(compute="_amount_line_discount",
    #                                  string='Subtotal', digits_compute= dp.get_precision('Account'))
    # show_discount = fields.Float(digits=(12, 6), string='Discount')

    discount_amount = fields.Float(string='Discount Amount', compute='_compute_discount_price',
                                   store=False, digits=dp.get_precision('Account'))
    discount_amount_line = fields.Float(string='Discount Amount', compute='_compute_all_price',
                                        store=False, digits=dp.get_precision('Account'))
    # price_subtotal = fields.Float(string='Subtotal', compute='_compute_all_price',
    #                               digits=dp.get_precision('Account'),
    #                               help='The Amount after discount on line and whole bill', store=False)
    ws_discount = fields.Float(string='Whole Sale Discount Amount on Line')
    # price_subtotal_discount_line = fields.Float(string='Price Subtotal', digits=dp.get_precision('Account'),
    #                                             compute='_compute_all_price',
    #                                             help="The Amount after discount on line", store=False)
    tax_amount = fields.Float(string='Taxed Amount', digits=dp.get_precision('Account'), compute='_compute_all_price',
                              help='The Tax Amount base on price_subtotal_after_ws_discount', store=False)
    final_price_unit = fields.Float(string='Price Unit', digits=dp.get_precision('Account'),
                                    compute='_compute_final_price_unit')

    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            line_price = self._calc_line_base_price(cr, uid, line,
                                                    context=context)
            line_qty = self._calc_line_quantity(cr, uid, line,
                                                context=context)
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line_price,
                                        line_qty, line.product_id,
                                        line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'price_subtotal': old_fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account'))
    }
    # @api.onchange('show_discount')
    # def onchange_show_discount(self):
    #     if self.show_discount:
    #         self.discount = self.show_discount
    #
    # @api.model
    # @api.depends('price_unit', 'discount', 'product_qty',
    #              'product_id', 'order_id.partner_id', 'order_id.currency_id')
    # def _amount_line_discount(self):
    #     for line in self:
    #         line_price = line.price_unit * (1 - (line.show_discount or 0.0) / 100.0)
    #         line_qty = self._calc_line_quantity(line)
    #         taxes = line.taxes_id.compute_all(line_price,
    #                                     line_qty, line.product_id,
    #                                     line.order_id.partner_id)
    #         cur = line.order_id.pricelist_id.currency_id
    #         line.total_bf_discount = cur.round(taxes['total'])
    #     return
    #

    @api.model
    def _calc_line_base_price(self, line):
        """Return the base price of the line to be used for tax calculation.

        This function can be extended by other modules to modify this base
        price (adding a discount, for example).
        """
        return line.price_unit * (1 - (line.discount or 0.0) / 100.0)

    #
    # @api.model
    # def create(self, vals):
    #     obj = super(NpPurchaseLine, self).create(vals)
    #     obj._resolve_price_unit()
    #
    # @api.multi
    # def write(self, vals):
    #     r = super(NpPurchaseLine, self).write(vals)
    #     if not self.env.context.get('resolved_price_unit', False):
    #         self._resolve_price_unit()
    #     return r
    #
    # @api.multi
    # def _resolve_price_unit(self):
    #     """
    #     Resolve price_unit on purchase order line
    #     :return:
    #     """
    #     # if self.env.context.get('resolve_price_unit'):
    #     # ctx = self.env.context.copy()
    #     # del ctx['resolve_price_unit']
    #     for r in self:
    #         price_unit = (r.origin_price_unit * r.product_qty * (1 - r.discount / 100) - r.ws_discount) / r.product_qty
    #         r.with_context(resolved_price_unit=True).write({'price_unit': price_unit})
