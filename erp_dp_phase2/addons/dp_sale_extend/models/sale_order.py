from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning
from openerp.tools.translate import _
from multiprocessing import cpu_count
CPU = min(cpu_count(), 16)
import logging, threading, sys
_logger = logging.getLogger(__name__)
import openerp.addons.decimal_precision as dp
from openerp.http import request
import ast



class INITDPSaleOrderExtend(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(help="")
    po_num = fields.Char('Chandler PO No')
    so_num = fields.Char('Chandler SO No')
    marking_num = fields.Char('Chandler Marking No')
    estimated_departure = fields.Date('Estimated Date of Departure')
    parent_partner_id = fields.Many2one(related="partner_id.parent_id", string='Parent Company')

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if self._name == 'sale.order':
            if context:
                if context.get('params', False):
                    if context.get('params').get('action', False):
                        action_id = context['params']['action']
                        try:
                            if type(action_id) == int:
                                unicode_context_dict= self.pool.get('ir.actions.act_window').browse(cr, uid, action_id).context
                            else:
                                return super(INITDPSaleOrderExtend, self).read(cr, uid, ids, fields, context, load)
                        except:
                            return super(INITDPSaleOrderExtend, self).read(cr, uid, ids, fields, context, load)
                        context_dict = ast.literal_eval(unicode_context_dict)
                        user_id = self.pool.get('res.users').browse(cr, uid, uid)
                        if context_dict.get('shipmaster_form', False):
                            if user_id.has_group('dp_common.group_shipmaster'):
                                pass
                            else:
                                raise except_orm("Warning", 'You do not have access to this page')
                        if context_dict.get('chandler_form', False):
                            if user_id.has_group('dp_common.group_chandler'):
                                pass
                            else:
                                raise except_orm("Warning", 'You do not have access to this page')
        return super(INITDPSaleOrderExtend, self).read(cr, uid, ids, fields, context, load)

    def __init__(self, pool, cr):
        # self.listen_channel()
        states = getattr(type(self), 'bid_status')
        state_selection = states._attrs.get('selection', {})
        if ('expired', 'Expired') in state_selection and \
                ('confirm_others', "Order Fulfilled With Other Chandler") not in state_selection:
            state_selection.insert(state_selection.index(('expired', 'Expired')),
                                                ('confirm_others', "Order Fulfilled With Other Chandler"))

        return super(INITDPSaleOrderExtend, self).__init__(pool, cr)


class DPSaleOrderExtend(models.Model):
    _inherit = "sale.order"

    @api.multi
    def bid_confirm_order(self):
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
        all_sales = self.search(['|', ('sale_duplicate_id', '=', self.id), ('id', '=', self.id)], order='id')
        forbidden_states = ('shipmaster_confirm', 'progress', 'manual', 'shipping_except', 'invoice_except', 'done')
        if all(sale.state not in forbidden_states for sale in all_sales):
            self.state = 'shipmaster_confirm'
            msg_id = self.env['mail.message'].search([('res_id', '=', self.id), ('model', '=', 'sale.order')]).mapped(lambda x:x.id)
            notification = self.env['mail.notification'].sudo().search(
                [('message_id', 'in', msg_id), ('partner_id', '=', self.user_id.partner_id.id)])
            notification.write({'is_read': False})
            self.bid_status = 'confirm'
            self.order_line.sudo().write({'state': 'confirmed'})
            # for line in self.order_line:
            #     if line.counter_offer_qty > 0 and line.counter_offer_price > 0:
            #         line.write({'product_uom_qty': line.counter_offer_qty, 'price_unit': line.counter_offer_price})

            # comment out shipmaster send email when confirm order
            # self.tmp_send_mail()

            # find duplicate orders
            # origin source sale order
            sale_id = self.id
            if self.sale_duplicate_id.exists():
                # duplicated sale order
                sale_id = self.sale_duplicate_id.id

            self._cr.execute("""select id from sale_order where id = {} or sale_duplicate_id = {} order by id""".format(sale_id,sale_id))
            cancel_id = filter(lambda x: x != self.id, [lst[0] for lst in self._cr.fetchall()])
            if len(cancel_id) > 0:
                # if duplicate sale order found, if not found cancel_id will be of length 0
                cancel_obj = self.env['sale.order'].browse(cancel_id)
                cancel_obj.bid_cancel()
            return True
        else:
            sale_order_ids = [sol.id for sol in filter(lambda x: x.state in forbidden_states, all_sales)]
            sale_line_objs = self.env['sale.order.line'].browse(sale_order_ids)
            sale_objs = sale_line_objs.mapped(lambda x: x.order_id)
            raise except_orm(_('You have already confirmed one this order with another chandler in {sale_id}'.format(sale_id=','.join(sale.name for sale in sale_objs))),
                             _('If you wish to perform the similar order transaction with another chandler, \n'
                               'you should perform the same transaction from the website to the chandler'))

    @api.multi
    def bid_cancel(self):
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
        # change self.state to record.state as it is using api.multi
        for rec in self:
            rec.state = 'cancel'
            rec.bid_status = 'cancel_yourself'
            rec.order_line.with_context({'bid_cancel': True}).sudo().write({'state': 'cancel'})

            try:
                sale_ids = [sale.id for sale in rec]
                len_sale_ids = len(sale_ids)
                i = 0
                threads = []
                total_sale_ids_thread = len_sale_ids / CPU
                for i in range(0, CPU - 1):
                    t = threading.Thread(target=rec.send_cancel_email_multithreading,
                                         args=(sale_ids[i * total_sale_ids_thread: total_sale_ids_thread * (i + 1)],))
                    threads.append(t)
                    t.start()
                t = threading.Thread(target=rec.send_cancel_email_multithreading,
                                     args=(sale_ids[(i + 1) * total_sale_ids_thread:],))
                t.start()
                threads.append(t)
            except Exception:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('Multithreading Problems')

    def check_bid_status_to_action(self):
        return 'dp_sale_extend.dp_shipmaster_request_quotation_my_orders'