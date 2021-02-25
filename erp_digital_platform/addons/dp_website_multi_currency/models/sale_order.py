# __author__ = 'BinhTT'
from openerp import  fields, models, api
from openerp.tools import float_round

class Currency_SO(models.Model):
    _inherit = 'sale.order'
    dp_currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'chandler_draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', related='')

    @api.onchange('dp_currency_id')
    def _onchange_currency_id(self):
        if self.user_id.partner_id.currency_line and self.dp_currency_id:
            chan_curr_rate = {curr.currency_id.id: curr.sale_rate for curr in self.user_id.partner_id.currency_line} \
                             or {self.user_id.company_id.currency_id.id: self.user_id.company_id.currency_id.rate}

            self.currency_rate = chan_curr_rate[self.dp_currency_id.id] or 0.00

            for line in self.order_line:
                from_currency = self.company_id.currency_id

                ctx = {
                    'voucher_special_currency': from_currency.id or False,
                    'voucher_special_currency_rate': 1
                }
                from_currency = self.env['res.currency'].with_context(ctx).browse(from_currency.id)
                ctx = {
                    'voucher_special_currency': self.dp_currency_id and self.dp_currency_id.id or False,
                    'voucher_special_currency_rate': self.currency_rate or 1
                }
                to_currency = self.env['res.currency'].with_context(ctx).browse(self.dp_currency_id.id)
                rate = to_currency.rate / from_currency.rate
                line.purchase_price = line.base_purchase_price / rate
                if line.item_type_product != 'foc':
                    line.mark_up_amount = line.mark_up_percent / 100 * float_round(line.purchase_price, 2)
                    line.mark_up_percent = line.mark_up_percent
                    line.discount = line.discount
                    self.update_price_unit(line)

    @api.model
    def update_price_unit(self, line):
        line._get_price_unit()


class Currency_SO_line(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def default_get(self, fields_list):
        res = super(Currency_SO_line, self).default_get(fields_list)
        return res

    # @api.multi
    # def product_id_change(self, pricelist, product, qty=0,
    #                       uom=False, qty_uos=0, uos=False, name='', partner_id=False,
    #                       lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
    #                       flag=False):
    #
    #     res = super(Currency_SO_line, self).product_id_change(pricelist, product, qty,
    #                       uom, qty_uos, uos, name, partner_id,
    #                       lang, update_tax, date_order, packaging, fiscal_position,
    #                       flag)
    #     context = self._context.copy()
    #     price = self.env['product.pricelist'].price_get(product, qty or 1.0, context.get('user_id') or partner_id)[
    #         pricelist]
    #
    #     return res


class Currencywebsite(models.Model):
    _inherit = 'website'

    @api.cr_uid_ids_context
    def sale_get_order(self, cr, uid, ids, force_create=False, code=None, update_pricelist=None, context=None):
        res = super(Currencywebsite, self).sale_get_order(cr, uid or 3, ids, force_create, code, update_pricelist, context)
        if res and force_create != False:
            partner = self.pool['res.users'].browse(cr, 1, uid, context=context).partner_id
            res.dp_currency_id = partner.property_product_pricelist.currency_id
        return res