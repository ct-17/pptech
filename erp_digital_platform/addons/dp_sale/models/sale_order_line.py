from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import time
import openerp.addons.decimal_precision as dp
from openerp.http import request



class INITDPSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def __init__(self, pool, cr):
        # self.listen_channel()
        states = getattr(type(self), 'state')
        state_selection = states._attrs.get('selection', {})
        try:
            if ('draft', 'Draft') in state_selection and ('bid_received', 'Quote Received') not in state_selection:
                state_selection.insert(state_selection.index(('draft', 'Draft')), ('bid_received', 'Quote Received'))
                state_selection[state_selection.index(('done', 'Done'))] = ('done', 'Processed')
        except:
            pass
        return True


class DPOrderLine(models.Model):
    _inherit = "sale.order.line"
    order_state = fields.Selection(related='order_id.state')
    item_type_product = fields.Selection([('foc', 'FOC')])
    check_readonly = fields.Boolean()
    check_readonly_shipmaster = fields.Boolean()
    bid_status = fields.Selection(related='order_id.bid_status')
    # @api.multi
    # def _compute_item_type_readonly(self):
    #     if self._context['current_state'] == "shipmaster_confirm":
    #         return True
    #     else:
    #         return False
    #
    # @api.model
    # def _get_default_type(self):
    #     if self._context['current_state'] == "shipmaster_confirm":
    #         return 'foc'

    @api.model
    def default_get(self, fields_list):
        res = super(DPOrderLine, self).default_get(fields_list)
        if self._context.get('current_state', "") == 'shipmaster_confirm':
            res.update(item_type_product='foc', check_readonly_shipmaster=True, check_readonly=True)
        return res

    # Shipmaster/Chandler columns

    sm_qty = fields.Float("SM Requested Qty")
    sm_unit_price = fields.Float("SM Requested Price")
    sm_price_subtotal = fields.Float("SM Subtotal")

    last_selling_price = fields.Float("Last Selling Unit Price", digits=dp.get_precision('Product Price'))
    currency_and_rate = fields.Char("Currency / Rate")
    # mark_up_amount = fields.Float("Mark-up ($)")
    # mark_up_percent = fields.Float("Mark-up (%)")
    margin_amount = fields.Float("Line Margin ($)", store=False, compute='_compute_margin', digits=dp.get_precision('Product Price'))
    chandler_price_subtotal = fields.Float("Subtotal", store=False, compute='_compute_margin', digits=dp.get_precision('Product Price'))

    counter_offer_qty = fields.Float("Counter Offer Quantity")
    counter_offer_price = fields.Float("Counter Offer Unit Price")
    counter_offer_sub_total = fields.Float("Counter Offer Subtotal")

    route_id = fields.Many2one('stock.location.route', 'Route',
                               domain=[('sale_selectable', '=', True)],
                               default=lambda self: self.env['stock.location.route'].search([('name', '=', 'Drop Shipping')]))
    base_purchase_price = fields.Float(string='Base Cost Price',digits=dp.get_precision('Product Price'))
    purchase_price = fields.Float(string='Currency Cost Price')
    shipmaster_update = fields.Boolean()
    shipmaster_state = fields.Selection(related='order_id.bid_status')
    chandler_state = fields.Selection(related='order_id.state')

    @api.depends('price_unit', 'purchase_price', 'discount', 'product_uom_qty')
    def _compute_margin(self):
        for line in self:
            line.margin_amount = line.price_unit * line.product_uom_qty - (line.price_unit * line.product_uom_qty * line.discount / 100)\
                                  - (line.purchase_price*line.product_uom_qty)
            line.chandler_price_subtotal = line.price_unit * line.product_uom_qty - (
                        line.price_unit * line.product_uom_qty * line.discount / 100)

    @api.model
    def create(self, vals):
        # todo: add this context bcz system auto re-call to onchange_product_id
        ctx = {'create': True}
        if vals.get('item_type_product', False) == 'foc':
            ctx.update(item_type_product='foc')
        rtn = super(DPOrderLine, self.with_context(ctx)).create(vals)
        return rtn

    @api.multi
    def write(self, vals):
        """
        similar check function here and dp_sale_stock_allocation.sale_order_line.py
        if change logic here, need check both place
        no time to optimize and beautify it
        """
        if vals.has_key('product_uom_qty') and not self._context.get('skip_check_qty', False):
            if vals.get('product_uom_qty', False) > self.product_uom_qty:
                diff = vals['product_uom_qty'] - self.product_uom_qty
                if self.product_id.product_tmpl_id.virtual_available - diff < 0 and self.state != 'cancel':
                    raise except_orm(('Insufficient Stock'),'Not Enough Stock for %s'%(self.product_id.name))
                if self.product_id.product_tmpl_id.virtual_available< vals.get('product_uom_qty', False) and self.state != 'cancel':
                    # raise except_orm(('Insufficient Stock'), 'Not Enough Stock for %s' % (self.product_id.name))
                    return False
            if type(vals.get('product_uom_qty', False))  is int and vals.get('product_uom_qty', False) == 0:
                raise except_orm(('Item Problem'),'Please check the product "%s" have 0 quantity.\n Maybe You Want To Remove it'%(self.product_id.name))
            vals.update(shipmaster_update=True)
        rtn = super(DPOrderLine, self).write(vals)
        return rtn

    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):
        #   ___                               _ _         ____
        #  / _ \__   _____ _ ____      ___ __(_) |_ ___  | __ )  __ _ ___  ___
        # | | | \ \ / / _ \ '__\ \ /\ / / '__| | __/ _ \ |  _ \ / _` / __|/ _ \
        # | |_| |\ V /  __/ |   \ V  V /| |  | | ||  __/ | |_) | (_| \__ \  __/
        #  \___/  \_/ \___|_|    \_/\_/ |_|  |_|\__\___| |____/ \__,_|___/\___|
        #
        #  __  __           _       _
        # |  \/  | ___   __| |_   _| | ___
        # | |\/| |/ _ \ / _` | | | | |/ _ \
        # | |  | | (_) | (_| | |_| | |  __/
        # |_|  |_|\___/ \__,_|\__,_|_|\___|
        context = self._context or {}
        lang = lang or context.get('lang', False)
        if not partner_id:
            raise except_orm(_('No Customer Defined!'),
                             _('Before choosing a product,\n select a customer in the sales form.'))
        warning = False
        product_uom_obj = self.env['product.uom']
        partner_obj = self.env['res.partner']
        product_obj = self.env['product.product']
        partner = partner_obj.browse(partner_id)
        lang = partner.lang
        context_partner = context.copy()
        context_partner.update({'lang': lang, 'partner_id': partner_id})

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(product)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False

        fpos = False
        if not fiscal_position:
            fpos = partner.property_account_position or False
        else:
            fpos = self.env['account.fiscal.position'].browse(fiscal_position)

        if self._uid == SUPERUSER_ID and context.get('company_id'):
            taxes = product_obj.taxes_id.filtered(lambda r: r.company_id.id == context['company_id'])
        else:
            taxes = product_obj.taxes_id
        result['tax_id'] = [self.env['account.fiscal.position'].map_tax(taxes).id]

        if not flag:
            result['name'] = product_obj.name_get()[0][1]
            """
            commented the if product_obj.description_sale to remove description_sale from sale_order_line.name
            as description_sale has 
            <ul>
            <li>Volume: </li></br>
            <li>Alcohol: </li></br> 
            <li>Country of Origin: </li></br> 
            <li>Product Description: </li>
            </ul>
            which is not needed in the email templates 
            """
            # result['name'] = self.env['product.product'].name_get([product_obj.id])[0][1]
            # if product_obj.description_sale:
            #     result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up
        context_partner.update(uom=result.get('product_uom', False) or uom or product_obj.uom_id.id)

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            ctx = dict(
                context,
                uom=uom or result.get('product_uom'),
                date=date_order,
            )
            price = self.env['product.pricelist'].with_context(context_partner).price_get(product, qty or 1.0, context.get('user_id') or partner_id)[pricelist]
            cost_price = self.env['product.pricelist'].with_context(context_partner).price_get(product, qty or 1.0, context.get('user_id') or partner_id)[pricelist]

            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                price = self.env['account.tax']._fix_tax_included_price(price, taxes, result['tax_id'])
                if not context.get('from_product_id', False) and not context.get('create', False):
                    values = {}
                    for field in ['product_uos_qty', 'th_weight']:
                        if not result.get(field, False) is False:
                            values[field] = result[field]
                    return {'value': values, 'domain': {}, 'warning': False}
                if self._context.get('item_type_product', False) == 'foc':
                    price = 0
                result.update({'price_unit': price / (context.get('currency_rate') or 1), 'base_purchase_price': cost_price,
                               'purchase_price': cost_price / (context.get('currency_rate') or 1)})

        # product_id onchange get last selling price
        lsp = self.env['chandler.last.selling.price']
        if self._context.get('chan_partner_id') and self._context.get('sm_partner_id'):
            chan_partner_id = self.env['res.users'].browse(self._context.get('chan_partner_id')).partner_id.id
            sm_partner_id = self._context.get('sm_partner_id')
            obj = lsp.search([('chan_partner_id', '=', chan_partner_id), ('sm_partner_id', '=', sm_partner_id),
                        ('product_id', '=', product)])
        else:
            obj = lsp
        result.update({'last_selling_price': 0.00})
        result.update({'currency_and_rate': "N/A"})
        if obj.exists():
            result.update({'last_selling_price':  obj.last_selling_price})
            result.update({'currency_and_rate': obj.currency_and_rate})

        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': domain, 'warning': warning}



    # @api.multi
    # def product_id_change_with_wh(self, pricelist, product, qty=0,
    #                               uom=False, qty_uos=0, uos=False, name='', partner_id=False,
    #                               lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
    #                               flag=False, warehouse_id=False):
    #     result = super(DPOrderLine, self).product_id_change_with_wh(pricelist, product, qty,
    #                                                                     uom, qty_uos, uos, name, partner_id,
    #                                                                     lang, update_tax, date_order, packaging,
    #                                                                     fiscal_position, flag,
    #                                                                     warehouse_id)
    #
    #     try:
    #         if self._context['item_type_product'] == 'foc':
    #             result['value'].update({'price_unit': 0})
    #         return result
    #     except:
    #         return result


    @api.onchange('item_type_product')
    def item_type(self):
        if self.item_type_product == 'foc':
            self.mark_up_amount = 0
            self.mark_up_percent = 0
            self.discount = 0
            self.price_unit = 0
            self.check_readonly = True
        else:
            self.check_readonly = False
            self._get_price_unit()


    @api.multi
    def unlink(self):
        if self.bid_status in ('confirm','done','cancel','cancel_yourself','expired') and \
            self.env.ref('dp_sale.dp_shipmaster_request_quotation').id == self._context.get('params', {}).get('action', False):
            self._cr.rollback()
            raise except_orm(_('This view is readonly. You will not be able to delete any confirmed orders!'),
                             _('You can only proceed by clicking on discard and/or refresh the page'))
        if self.state in ('confirmed') and \
           self._context.get('params', {}).get('action', False) in (self.env.ref('sale.action_quotations').id, self.env.ref('sale.action_orders').id):
            self._cr.rollback()
            raise except_orm(_('Invalid action! You are trying to delete a confirmed product by ship master!'),
                             _('You can only proceed by clicking on discard and/or refresh the page'))
        res = super(DPOrderLine, self).unlink()
        return res


    @api.multi
    def update_item_type(self):
        if self.item_type_product != 'foc':
            self.item_type_product = 'foc'
            self.mark_up_amount = 0
            self.mark_up_percent = 0
            self.discount = 0
            self.price_unit = 0
            self.check_readonly = True
        else:
            self.item_type_product = False
            self.check_readonly = False
            self._get_price_unit()

        self.env.cr.commit()
        self.order_id.with_context(recompute=True).new({'total_before_discount': self.order_id.total_before_discount-self.chandler_price_subtotal})
        self.order_id.with_context(recompute=True).button_dummy()
        return True