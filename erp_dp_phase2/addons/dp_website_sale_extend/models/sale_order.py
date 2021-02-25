import logging, sys
from openerp import models, fields, api

from datetime import datetime as dt
from multiprocessing import cpu_count
import threading
CPU = min(cpu_count(), 16)

from openerp import models, fields, api, _, sql_db
from openerp.exceptions import Warning, except_orm

_logger = logging.getLogger(__name__)


class DPWebsiteSaleExtendSale(models.Model):
    _inherit = 'sale.order'

    order_line = fields.One2many('sale.order.line', 'order_id', 'Order Lines', readonly=True,
                                  # states={'chandler_draft': [('readonly', False)],
                                  #         'draft': [('readonly', False)],
                                  #         'sent': [('readonly', False)],
                                  #         'shipmaster_confirm': [('readonly', False)]},
                                  domain=[('state','!=','cancel')],
                                  copy=True)
    cancel_order_line = fields.One2many('sale.order.line', 'order_id', 'Order Lines', readonly=True,
                                          # states={'chandler_draft': [('readonly', False)],
                                          #         'draft': [('readonly', False)],
                                          #         'sent': [('readonly', False)],
                                          #         'shipmaster_confirm': [('readonly', False)]},
                                          copy=True)
    @api.model
    def sanitize_data(self, data):
        """
        excepted data
        [[2, 10],[3, 0], ...]

        :param data:
        :return:
        return data: [[2, 10],[3, 0], ...]
        return flag: True if all of data inner list value is integer
                    False if otherwise
        if data is integer already, nothing will happen, if data is string/unicode will convert to integer
        """
        try:
            # checker: True when inner_data is integer, False if is not integer,
            # will raise Exception when unable to cast as integer

            checker = [True if isinstance(inner_data, int) else False for lis in data for inner_data in lis]
            # if all of data is integer
            # checker = [True, True, True, True] if all is integer
            if all(bul is True for bul in checker):
                return data, True
            raise ValueError
        except ValueError:
            try:
                # if all of data is string/unicode
                checker = [True if isinstance(inner_data, unicode) or isinstance(inner_data, str) else False for lis in data for inner_data in lis]
                if all(bul is True for bul in checker):
                    data = [[int(inner_data) for inner_data in lis] for lis in data]
                    # if all of data is string/unicode and convertable to integer,
                    # if not convertable will raise ValueError
                    return data, True
            except ValueError as ve:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('DATA IS ALPHANUMERIC!! ONLY INTEGER DATA IS EXPECTED')
                _logger.error('ValueError: {ve}'.format(ve=ve))
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('data: ' + str(data))
                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            except Exception as ie:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('DEBUGGING REQUIRED - UNCAUGHT INNER EXCEPTION!!')
                _logger.error('Exception: {ie}'.format(ie=ie))
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('data: ' + str(data))
                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('DEBUGGING REQUIRED - UNCAUGHT EXCEPTION!!')
            _logger.error('Exception: {e}'.format(e=e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('data: ' + str(data))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))

        return [[]], False

    @api.model
    def check_sale_order_line_id(self, data):
        """
        this function checks if line id parsed belong to sale order (incase line id is parsed wrongly)
        :param data:
        :return:
        """
        checker = [lis[0] in self.order_line._ids for lis in data]

        # checker
        # True when id is in sale.order_line._ids
        # False otherwise
        if all(flag is True for flag in checker):
            return True
        return False

    @api.model
    def pre_write_sanitize(self, order_line_ids):
        """
        vals on sale order write
        {'cancel_order_line': [[1, 257, {}], [1, 258, {}], [1, 259, {}]],
         'order_line': [[1, 251, {'delay': 7, 'product_uom_qty': 9, 'product_uos_qty': 9}], // increase 3 to 9
                        [1, 252, {'delay': 7, 'product_uom_qty': 1, 'product_uos_qty': 1}], // decrease 3 to 1
                        [2, 250, False],                                                    // delete
                        [0, False, {'base_purchase_price': 14.8,                            // add new item
                                      'check_readonly': False,
                                      'check_readonly_shipmaster': False,
                                      'currency_and_rate': 'N/A',
                                      'delay': 7,
                                      'discount': 0,
                                      'item_type_product': False,
                                      'mark_up_amount': 29985.2,
                                      'mark_up_global_amount': 0,
                                      'mark_up_percent': 202602.7,
                                      'name': '[33SCW-75] 33 SOUTH CHARDONNAY',
                                      'price_unit': 30000,
                                      'product_id': 1421,
                                      'product_packaging': False,
                                      'product_uom_qty': 10,
                                      'product_uos': False,
                                      'product_uos_qty': 10,
                                      'route_id': 6,
                                      'sequence': 11,
                                      'shipmaster_update': False,
                                      'th_weight': 0,
                                      'ws_discount': 0}]]}


        e.g. order_line_ids data
        'order_line_ids': [[2, 10],[3, 0]]
        order_line_ids => [[id, qty],[id, qty], ...]

        :return:
        """
        data, sanitize_flag = self.sanitize_data(order_line_ids)
        try:
            if sanitize_flag is False:
                raise Exception
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception: {e}'.format(e=e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('order_line_ids structure is not desired !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            _logger.error('order_line_ids: ' + str(order_line_ids))
            _logger.error('flag: ' + str(sanitize_flag) + '\tdata: ' + str(data))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))

        line_flag = self.check_sale_order_line_id(data)
        try:
            if line_flag is False:
                raise Exception
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception: {e}'.format(e=e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('sale order line ids parsed do not belong to sale order!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            _logger.error('self: ' + str(self))
            _logger.error('self.order_line: ' + str(self.order_line))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))

        order_line = [[2, lis[0], False] if lis[1] == 0 else [1, lis[0], {'product_uom_qty': lis[1], 'product_uos_qty': lis[1]}] for lis in data]
        # above list comprehension does the for loop below
        # for lis in data:
        #     if lis[1] == 0:
        #         order_line.append([2, lis[0], False])
        #     else:
        #         order_line.append([1, lis[0], {'product_uom_qty': lis[1], 'product_uos_qty': lis[1]}])

        # filter away cancel order line with more than 0 product_qty (fix cancel line where it will not add qty)
        cancel_line = self.cancel_order_line.filtered(lambda x:x.state == 'cancel')
        new_ol = []
        for lis in order_line:
            if isinstance(lis[2], dict):
                if lis[2]['product_uom_qty'] > 0 and lis[1] not in cancel_line._ids:
                    new_ol.append(lis)
            if isinstance(lis[2], bool):
                new_ol.append(lis)
        order_line = new_ol
        # order_line = [[v for v in lis] for lis in order_line if lis[2]['product_uom_qty'] > 0 and lis[1] not in cancel_line._ids]

        write_val = {
            'order_line': order_line
        }
        self.with_context({'from_myenquiry': True, 'need_recompute_discount': True}).write(write_val)
        self._cr.commit()
        self.send_cancel_workflow_email()
        # send_email_to_preferred_chandler_on_checkout()

    @api.model
    def send_cancel_workflow_email(self):
        try:
            t = threading.Thread(target=self.send_cancel_workflow_email_multithreading,
                                 args=([self.id]))
            t.start()
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('Multithreading Problems')

    @api.model
    def send_cancel_workflow_email_multithreading(self, sale_ids):
        _logger.info('------------------------------------------------------ dp_website_sale_extend.send_cancel_workflow_email_multithreading START THREAD')
        with api.Environment.manage():
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            uid = self.env.uid
            start_thread = dt.now()
            new_env = api.Environment(new_cr, uid, self.env.context.copy())
            self = self.with_env(new_env)
            for record in self.env['sale.order'].browse(sale_ids):
                newer_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                uid = self.env.uid
                newer_env = api.Environment(newer_cr, uid, self.env.context.copy())
                self = self.with_env(newer_env)

                _logger.info('send_invitation_to_chandler: send_email_to_preferred_chandler_on_checkout START')
                record.send_email_to_chandler_on_shipmaster_quotation_adjustment()
                _logger.info('send_invitation_to_chandler: send_email_to_preferred_chandler_on_checkout COMPLETE ')
                newer_cr.commit()
                newer_cr.close()

            finish_thread = dt.now() - start_thread
            _logger.info(('------------------------------------------------------ dp_website_sale_extend.send_cancel_workflow_email_multithreading TIME FINISH 1 thread: %s') \
                            % (finish_thread.total_seconds()))
            new_cr.commit()
            new_cr.close()
        return True

    @api.multi
    def write(self, vals):
        res = super(DPWebsiteSaleExtendSale, self).write(vals)
        if not self.order_line.exists() and self._context.get('cancel_orderline_until_all_cancel', True) \
                and self._context.get('from_myenquiry', False):
            self.with_context({'cancel_orderline_until_all_cancel': False}).write({'bid_status': 'cancel_yourself',
                        'state': 'cancel'})
        return res

    @api.multi
    def action_button_confirm(self):
        res = super(DPWebsiteSaleExtendSale, self).action_button_confirm()
        self.bid_status = 'done'
        self.order_line.write({'state': 'done'})
        self.btf_confirm_sale_email_chandler()
        return res

    @api.model
    def btf_confirm_sale_email_chandler(self):
        try:
            t = threading.Thread(target=self.send_shipmaster_email_on_btf_confirm_email_multithreading,
                                 args=([self.id]))
            t.start()
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('Multithreading Problems')

    @api.model
    def send_shipmaster_email_on_btf_confirm_email_multithreading(self, sale_ids):
        # _logger.info('------------------------------------------------------ dp_website_sale_extend.btf_sales_confirm_order_email_send_to_shipmaster_email START THREAD')
        # with api.Environment.manage():
        #     new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        #     uid = self.env.uid
        #     start_thread = dt.now()
        #     new_env = api.Environment(new_cr, uid, self.env.context.copy())
        #     new_self = self.with_env(new_env)
        #     for record in self.env['sale.order'].browse(sale_ids):
        #         newer_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
        #         uid = self.env.uid
        #         newer_env = api.Environment(newer_cr, uid, self.env.context.copy())
        #         new_self = self.with_env(newer_env)

                # send email when btf sales confirm order, email send to shipmaster
                # record.send_email_to_chandler_on_shipmaster_quotation_adjustment()
                # _logger.info('dp_website_sale_extend.btf_sales_confirm_order_email_send_to_shipmaster_email START')
                # template = new_self.new_env.ref('dp_website_sale_extend.btf_sales_confirm_order_email_send_to_shipmaster_email')
                # pdf = new_self.new_env['report'].sudo().get_pdf(new_self, 'dp_purchase_template_extend.np_purchase_order_template')
                # attachment = new_self.new_env['ir.attachment'].create({'type': 'binary', 'name': 'Report.pdf',
                #                                                    'datas_fname': 'Report.pdf',
                #                                                    'datas': pdf.encode('base64')})
                # template.attachment_ids = [(6, 0, [attachment.id])]
                # template.send_mail(new_self.id, force_send=True, raise_exception=True)
        #         # _logger.info('dp_website_sale_extend.btf_sales_confirm_order_email_send_to_shipmaster_email SUCCESS')
        #         newer_cr.commit()
        #         newer_cr.close()
        #
        #     finish_thread = dt.now() - start_thread
        #     _logger.info(('------------------------------------------------------ dp_website_sale_extend.btf_sales_confirm_order_email_send_to_shipmaster_email TIME FINISH 1 thread: %s') \
        #                     % (finish_thread.total_seconds()))
        #     new_cr.commit()
        #     new_cr.close()
        return True
