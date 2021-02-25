# -*- encoding: utf-8 -*-
# __author__ = 'BinhTT'
from openerp import  fields, models, api
from openerp.tools import float_round
from openerp.tools.translate import _
from openerp.exceptions import except_orm


class NoPopupException(Exception):
     def __init__(self, *args, **kwargs):
         pass


class Currency_SO_Extend(models.Model):
    _inherit = 'sale.order'

    currency_readonly_filter = fields.Char(related='dp_currency_id.name')
    is_sale_order_edited_exchange_rate = fields.Boolean(default=False, compute='check_sale_order_edited_exchange_rate')

    @api.depends('dp_currency_id', 'currency_rate')
    def check_sale_order_edited_exchange_rate(self):
        for rec in self:
            rec.is_sale_order_edited_exchange_rate = False
            if rec.dp_currency_id.name != 'SGD':
                for cur in  rec.user_id.partner_id.currency_line:
                    if cur.currency_id.name == rec.dp_currency_id.name:
                        if cur.sale_rate != rec.currency_rate:
                            rec.is_sale_order_edited_exchange_rate = True

    @api.multi
    def action_dp_quotation_send(self):
        if self.currency_rate == 0:
            raise except_orm(_('Unable to proceed!'),
                             _('Currency rate should not be 0, kindly review your quotation again.\n Click Ok to proceed.'))
        try:
            if self and not self._context.get('approved', False):
                new_msg = self.get_new_msg('send')
                if len(new_msg) == 0:
                    raise NoPopupException
                ctx = {
                    'action_ids': self.ids,
                    'action_id': self.id,
                    'model':  self._name,
                }
                view_id = self.env.ref('dp_website_multi_currency_extend.sale_order_msg_popup_confirm').id
                new_view = self.get_popup_window(msg='', view_id=view_id, name='Confirm Message')
                ctx.update({'default_msg': new_msg})
                new_view.update(context=ctx)
                return new_view
            raise NoPopupException
        except NoPopupException:
            res = super(Currency_SO_Extend, self).action_dp_quotation_send()
            return res

    @api.multi
    def action_dp_quotation_send_again(self):
        if self.currency_rate == 0:
            raise except_orm(_('Unable to proceed!'),
                             _('Currency rate should not be 0, kindly review your quotation again.\n Click Ok to proceed.'))
        if self and not self._context.get('approved', False):
            ctx = {
                'action_ids': self.ids,
                'action_id': self.id,
                'model':  self._name,
            }
            view_id = self.env.ref('dp_website_multi_currency_extend.sale_order_msg_popup_confirm').id
            new_view = self.get_popup_window(msg='', view_id=view_id, name='Confirm Message')
            ctx.update({'default_msg': self.get_new_msg('send_again')})
            new_view.update(context=ctx)
            return new_view
        res = super(Currency_SO_Extend, self).action_dp_quotation_send_again()
        return res

    # @api.multi
    # def bid_confirm_order(self):
    #     if self and not self._context.get('approved', False) and self.negotiation_type == 'chandler_send':
    #         ctx = {
    #             'action_ids': self.ids,
    #             'action_id': self.id,
    #             'model':  self._name,
    #         }
    #         view_id = self.env.ref('dp_website_multi_currency_extend.shipmaster_sale_order_msg_popup_confirm').id
    #         new_view = self.get_popup_window(msg='', view_id=view_id, name='Confirm Message')
    #         ctx.update({'default_msg': self.get_shipmaster_confirm_order_msg()})
    #         new_view.update(context=ctx)
    #         return new_view
    #     res = super(Currency_SO_Extend, self).bid_confirm_order()
    #     return res

    @api.model
    def get_popup_window(self, msg, view_id, name=None):
        if name is None:
            name = _('')
        return {
            'context': {'default_msg': msg, },
            'name': name,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'sale.order.popup.msg',
            'target': 'new',
            'type': 'ir.actions.act_window'
        }

    # @api.model
    # def get_shipmaster_confirm_order_msg(self):
    #     newline, msg = '\n', ''
    #     msg1 = "Clicking on confirm will apply counter offer quantity into quantity and counter offer unit price into unit price"
    #     msg = msg1+newline
    #     for line in self.order_line:
    #         msg += '\n{product}\n{counter_qty} -> {original_qty}\n{counter_price} -> {original_price}\n'.format(
    #             product=line.product_id.name,
    #             counter_qty=str(line.counter_offer_qty), original_qty=str(line.product_uom_qty),
    #             counter_price=str(line.counter_offer_price), original_price=str(line.price_unit),
    #         )
    #     return msg

    @api.model
    def get_new_msg(self, context=''):
        newline, msg, msg_second_last_line = '\n', '', ''
        add1, add2 = False, False
        msg1 = "Warning!\nYour profit margin or total amount is less than $0. Kindly review your quotations again."
        msg2 = "Reminder!\nYou have changed your currency rate."
        if context == 'send_again':
            msg_second_last_line = 'Warning!\nAre you sure you want to send this revised quotation?'
            resend_no_warning = 'Are you sure you want to send this revised quotation?'
        elif context == 'send':
            msg_second_last_line = 'Are you sure you want to proceed?'
        msg_lastline = 'Click Confirm to proceed, Cancel to return.'

        if self.show_confirm_prompt:
            msg += msg1 + newline
            add1 = True
            if context == 'send_again':
                msg += resend_no_warning + newline
            if self.is_sale_order_edited_exchange_rate:
                msg += newline
        if self.is_sale_order_edited_exchange_rate:
            msg += msg2 + newline
            add2 = True

        if add2 and not add1 and context == 'send_again':
            msg += newline + msg_second_last_line + newline + msg_lastline
        if add1 and not add2 and context == 'send_again' and resend_no_warning not in msg:
            msg += resend_no_warning + newline + msg_lastline
        if not add1 and not add2:
            msg += msg_second_last_line + newline
        if not msg_lastline in msg:
            msg += msg_lastline
        return msg

    @api.onchange('dp_currency_id', 'currency_rate')
    def _onchange_currency_id(self):
        #   ___                               _ _               _                    _
        #  / _ \__   _____ _ ____      ___ __(_) |_ ___   _ __ | |__   __ _ ___  ___/ |
        # | | | \ \ / / _ \ '__\ \ /\ / / '__| | __/ _ \ | '_ \| '_ \ / _` / __|/ _ \ |
        # | |_| |\ V /  __/ |   \ V  V /| |  | | ||  __/ | |_) | | | | (_| \__ \  __/ |
        #  \___/  \_/ \___|_|    \_/\_/ |_|  |_|\__\___| | .__/|_| |_|\__,_|___/\___|_|
        #                                                |_|
        #      _                    _
        #   __| |_ __     ___  __ _| | ___
        #  / _` | '_ \   / __|/ _` | |/ _ \
        # | (_| | |_) |  \__ \ (_| | |  __/
        #  \__,_| .__/___|___/\__,_|_|\___|
        #       |_| |_____|
        # overwrite phase1 dp_sale
        if self._context.get('edit_currency_rate', False):
            if self.currency_rate == 0:
                raise except_orm(_('Error!'), _('Rate cannot be 0'))
        if self.user_id.partner_id.currency_line and self.dp_currency_id or self.currency_rate:
            chan_curr_rate = {curr.currency_id.id: curr.sale_rate for curr in self.user_id.partner_id.currency_line} \
                             or {self.user_id.company_id.currency_id.id: self.user_id.company_id.currency_id.rate}

            if not self._context.get('edit_currency_rate', False):
                # if user manually enter currency rate, it will not go into here
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
