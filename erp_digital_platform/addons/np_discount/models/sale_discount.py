# __author__ = 'BinhTT'

from openerp import models, api, fields
from openerp.osv import fields as old_fields
from datetime import datetime
import openerp.addons.decimal_precision as dp


class GtsSaleOrder(models.Model):
    _inherit = 'sale.order'

    # discount_rate = fields.Float(string='Discount Total', digits_compute=dp.get_precision('Account'),
    #                                   readonly=True,
    #                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    # discount_amount = fields.Float(string='Discount Total', digits_compute=dp.get_precision('Account'),
    #                                   readonly=True,
    #                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    # discount_id = fields.Many2one('global_discount.wizard')
    #

    #
    # untax_discount = fields.Float(string='Discount Amount', digits_compute=dp.get_precision('Account'),
    #                               readonly=True, compute='_compute_discount')

    @api.multi
    def onchange_partner_id(self, part):
        data = super(GtsSaleOrder, self).onchange_partner_id(part)
        partner = self.env['res.partner'].browse(part)

        if partner.partner_discount_type != 'none':
            data['value'].update({'ws_discount_type': partner.partner_discount_type})
            if partner.partner_discount_type == 'percent':
                data['value'].update({'ws_discount_percent': partner.partner_discount,
                                      'ws_discount_amount': 0})
            else:
                data['value'].update({'ws_discount_amount': partner.partner_discount,
                                      'ws_discount_percent': 0})
        else:
            data['value'].update({'ws_discount_type': False,
                                  'ws_discount_percent': 0,
                                  'ws_discount_amount': 0})

        return data

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
            r.total_before_discount = sum([line.price_unit * line.product_uom_qty for line in r.order_line])
            r.amount_total = r.amount_untaxed + r.amount_tax
            r.amount_discount = r.total_before_discount - r.amount_untaxed

    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        line_obj = self.pool['sale.order.line']
        price = line_obj._calc_line_base_price(cr, uid, line, context=context)
        qty = line_obj._calc_line_quantity(cr, uid, line, context=context)
        for c in self.pool['account.tax'].compute_all(
                cr, uid, line.tax_id, price * qty - line.ws_discount, 1, line.product_id,
                line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
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
                val1 += line.price_subtotal - line.ws_discount
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    total_before_discount = fields.Float(string='Total Amount',
                                         digits=dp.get_precision('Account'),
                                         compute='_compute_all_price', store=False)

    ws_discount_type = fields.Selection(selection=[('amount', 'Fixed Amount'), ('percent', 'Percentage')],
                                        string='Whole Bill Discount Type', readonly=True)
    ws_discount_amount = fields.Float(string='Whole Bill Discount', digits=dp.get_precision('Account'),
                                      readonly=True)
    ws_discount_percent = fields.Float(string='Whole Bill Discount (%)', digits=dp.get_precision('Discount'),
                                       readonly=True)
    # line_discount_amount = fields.Float(string='Discount on Lines',  digits=dp.get_precision('Account'),
    #                                     compute='_compute_all_price', store=False)
    amount_discount = fields.Float(string='Discount', digits=dp.get_precision('Account'),
                                   compute='_compute_all_price', store=False)

    # amount_untaxed = fields.Float(string='Untaxed Amount', digits=dp.get_precision('Account'),
    #                               compute='_compute_all_price', store=False,
    #                               help='The Amount after discount and without tax')
    # amount_tax = fields.Float(string='Taxes', digits=dp.get_precision('Account'), compute='_compute_all_price',
    #                           help='The Tax Amount base on Total Amount after discount', store=False)
    # amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
    #                             compute='_compute_all_price', store=False)

    _columns = {
        'amount_untaxed': old_fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'),
                                              string='Untaxed Amount',
                                              store={
                                                  'sale.order': (
                                                   lambda self, cr, uid, ids, ctx: ids, ['order_line'], 10),
                                                  'sale.order.line': (
                                                      _get_order,
                                                      ['price_unit', 'tax_id', 'discount', 'product_uom_qty',
                                                       'ws_discount', 'price_subtotal'], 10),
                                              },
                                              multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': old_fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'),
                                          string='Taxes',
                                          store={
                                              'sale.order': (lambda self, cr, uid, ids, ctx: ids, ['order_line'], 10),
                                              'sale.order.line': (
                                                  _get_order,
                                                  ['price_unit', 'tax_id', 'discount', 'product_uom_qty', 'ws_discount',
                                                   'price_subtotal'], 10),
                                          },
                                          multi='sums', help="The tax amount."),
        'amount_total': old_fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'),
                                            string='Total',
                                            store={
                                                'sale.order': (
                                                 lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                                'sale.order.line': (
                                                    _get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty',
                                                                 'ws_discount', 'price_subtotal'], 10),
                                            },
                                            multi='sums', help="The total amount."),
    }

    @api.multi
    def _prepare_proforma_invoice(self, lines):
        res = super(GtsSaleOrder, self)._prepare_proforma_invoice(lines)
        res.update({'ws_discount_type': self.ws_discount_type,
                    'ws_discount_percent': self.ws_discount_percent})
        return res

    @api.multi
    def write(self, vals):
        res = super(GtsSaleOrder, self).write(vals)
        if self.env.context.get('need_recompute_discount') and self.order_line:
            self.env['global_discount.wizard'].with_context(
                active_ids=self.ids,
                active_id=self.ids[0],
                active_model=self._name,
                need_recompute_discount=False
            ).recompute_discount()
        return res

    @api.model
    def create(self, vals):
        obj = super(GtsSaleOrder, self).create(vals)
        if obj.ws_discount_type and obj.order_line:
            self.env['global_discount.wizard'].with_context(
                active_ids=obj.ids,
                active_id=obj.ids[0],
                active_model=self._name
            ).recompute_discount()
        return obj


class NpSaleLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('item_type')
    def onchange_item_type(self):
        for r in self:
            if r.item_type == 'foc':
                r.price_unit = 0.00

    @api.multi
    @api.depends('discount', 'price_unit', 'product_uom_qty')
    def _compute_all_price(self):
        for r in self:
            # r.price_subtotal_discount_line = r.price_unit * r.product_uom_qty * (1 - r.discount / 100)
            r.discount_amount_line = r.price_unit * r.product_uom_qty * r.discount / 100
            # r.price_subtotal = self._calc_line_base_price(r) * r.product_uom_qty - r.ws_discount
            r.tax_amount = sum([tax['amount'] for tax in r.tax_id.compute_all(r.price_subtotal-r.ws_discount, 1,
                                                                              r.order_id.partner_id)['taxes']])

    @api.multi
    @api.depends('ws_discount', 'discount_amount_line')
    def _compute_discount_price(self):
        for r in self:
            r.discount_amount = r.ws_discount + r.discount_amount_line

    # discount = fields.Float(digits=dp.get_precision('Discount'))
    # total_bf_discount = fields.Float(compute="_amount_line_discount",
    #                                  string='Subtotal1', digits_compute=dp.get_precision('Account'))
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

    # def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
    #     tax_obj = self.pool.get('account.tax')
    #     cur_obj = self.pool.get('res.currency')
    #     res = {}
    #     if context is None:
    #         context = {}
    #     for line in self.browse(cr, uid, ids, context=context):
    #         price = self._calc_line_base_price(cr, uid, line, context=context)
    #         qty = self._calc_line_quantity(cr, uid, line, context=context)
    #         taxes = tax_obj.compute_all(cr, uid, line.tax_id, price * qty - line.ws_discount, 1,
    #                                     line.product_id,
    #                                     line.order_id.partner_id)
    #         cur = line.order_id.pricelist_id.currency_id
    #         res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
    #     return res
    #
    # _columns = {
    #     'price_subtotal': old_fields.function(_amount_line, string='Subtotal',
    #                                           digits_compute=dp.get_precision('Account')),
    # }

    def _prepare_order_line_proforma_invoice_line(self):
        self.ensure_one()
        res = super(NpSaleLine, self)._prepare_order_line_proforma_invoice_line()
        res.update(ws_discount=self.ws_discount)
        return res

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        res = super(NpSaleLine, self)._prepare_order_line_invoice_line(line, account_id)
        res.update(sale_line_id=line.id)
        return res

    @api.multi
    def write(self, vals):
        res = super(NpSaleLine, self).write(vals)
        if self.env.context.get('foc'):
            self.env['global_discount.wizard'].with_context(
                active_ids=self.order_id.ids,
                active_id=self.order_id.ids[0],
                active_model=self.order_id._name,
                foc=False
            ).recompute_discount()
        return res


class NpPartner(models.Model):
    _inherit = 'res.partner'

    partner_discount_type = fields.Selection(
        selection=[('none', 'Not Applicable'), ('amount', 'Fixed Amount'), ('percent', 'Percentage')],
        string='Whole Bill Discount Type', default='none')
    partner_discount = fields.Float(string='Whole Bill Discount')

    @api.onchange('partner_discount_type')
    def onchange_discount_type(self):
        if self.partner_discount_type == 'none':
            self.partner_discount = 0.00
