from openerp import models, api, sql_db
from datetime import datetime as dt
from multiprocessing import cpu_count
CPU = min(cpu_count(), 16)
import logging, sys, time, random, threading,psycopg2
_logger = logging.getLogger(__name__)


class email(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def wkf_confirm_order(self):
        res = super(email, self).wkf_confirm_order()
        self._cr.commit()
        try:
            purchase_ids = [purchase.id for purchase in self]
            len_purchase_ids = len(purchase_ids)
            i = 0
            threads = []
            total_purchase_ids_thread = len_purchase_ids / CPU
            for i in range(0, CPU - 1):
                t = threading.Thread(target=self.send_email_multithreading,
                                     args=(purchase_ids[i * total_purchase_ids_thread: total_purchase_ids_thread * (i + 1)],))
                threads.append(t)
                t.start()
            t = threading.Thread(target=self.send_email_multithreading,
                                 args=(purchase_ids[(i + 1) * total_purchase_ids_thread:],))
            t.start()
            threads.append(t)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('Multithreading Problems')
        return res

    @api.model
    def send_email_multithreading(self, purchase_id):
        _logger.info('------------------------------------------------------ dp_email_template.purchase_order.send_email_multithreading START THREAD')
        with api.Environment.manage():
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            uid = self.env.uid
            start_thread = dt.now()
            new_env = api.Environment(new_cr, uid, self.env.context.copy())
            new_self = self.with_env(new_env)
            for record in new_self.env['purchase.order'].browse(purchase_id):
                # time.sleep(random.randrange(5,10,1))
                template_chandler = None
                # try:
                #     template_chandler = new_self.env.ref('dp_purchase.confirm_chandler_quote_to_chandler_email')
                #     template_chandler.with_context({'email_bcc': True}).send_mail(record.id, force_send=True, raise_exception=True)
                #     _logger.info('dp_purchase.confirm_chandler_quote_to_chandler_email SUCCESS')
                #     _logger.info('Purchase Order: {purchase_id} email template had been successfully sent'.format(purchase_id=str(record)))
                # except psycopg2.InternalError:
                #     new_cr.close()
                #     new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                #     new_env = api.Environment(new_cr, uid, self.env.context.copy())
                #     new_self = self.with_env(new_env)
                #     continue
                # except Exception as e:
                #     _logger.exception('{} While sending accepted invitation exception generated'.format(record))
                #     _logger.error(e)
                #     exc_type, exc_obj, exc_tb = sys.exc_info()
                #     _logger.error('Exception Type: ' + str(exc_type))
                #     _logger.error('Exception Error Description: ' + str(exc_obj))
                #     _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                #     _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                #     _logger.error('template_chandler: {}'.format(template_chandler or None))
                #     new_cr.close()
                #     new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                #     new_env = api.Environment(new_cr, uid, self.env.context.copy())
                #     new_self = self.with_env(new_env)

                # time.sleep(random.randrange(5,10,1))
                template_newport = None
                try:
                    pdf = new_self.env['report'].sudo().get_pdf(new_self, 'dp_purchase_template.np_purchase_order_template')
                    attachment = new_self.env['ir.attachment'].create({'type'       : 'binary', 'name': self.name + '.pdf',
                                                                   'datas_fname': self.name + '.pdf',
                                                                   'datas'      : pdf.encode('base64')})
                    template_newport = new_self.env.ref('dp_purchase.confirm_chandler_quote_to_newport_email')

                    template_newport.attachment_ids = [(6, 0, [attachment.id])]
                    template_newport.send_mail(record.id, force_send=True, raise_exception=True)
                    _logger.info('dp_purchase.confirm_chandler_quote_to_newport_email SUCCESS')
                    _logger.info('Purchase Order: {purchase_id} email template had been successfully sent'.format(
                        purchase_id=str(record)))

                    _logger.info('dp_purchase.btf_sales_confirm_order_email_send_to_shipmaster_email START')
                    template = new_self.env.ref(
                        'dp_purchase.btf_sales_confirm_order_email_send_to_shipmaster_email')
                    pdf = new_self.env['report'].sudo().get_pdf(new_self,
                                                                    'dp_purchase_template.np_purchase_order_template')
                    attachment = new_self.env['ir.attachment'].create({'type': 'binary', 'name': self.name + '.pdf',
                                                                           'datas_fname': self.name + '.pdf',
                                                                           'datas': pdf.encode('base64')})
                    template.attachment_ids = [(6, 0, [attachment.id])]
                    template.send_mail(new_self.id, force_send=True, raise_exception=True)
                    _logger.info(
                        'dp_purchase.btf_sales_confirm_order_email_send_to_shipmaster_email SUCCESS')

                    # template_shipmaster =  new_self.env.ref('dp_purchase.confirm_chandler_quote_to_chandler_email')
                    # template_shipmaster.send_mail(record.id, force_send=True, raise_exception=True)
                    # _logger.info('dp_purchase.confirm_chandler_quote_to_shipmaster_email SUCCESS')
                    # _logger.info('Purchase Order: {purchase_id} email template had been successfully sent'.format(
                    #     purchase_id=str(record)))
                except psycopg2.InternalError:
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
                    continue
                except Exception as e:
                    _logger.exception(
                        '{} While sending accepted invitation exception generated'.format(record))
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    _logger.error('template_newport: {}'.format(template_newport))
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
            finish_thread = dt.now() - start_thread
            _logger.info(('------------------------------------------------------ dp_email_template.purchase_order.send_email_multithreading TIME FINISH 1 thread: %s') \
                            % (finish_thread.total_seconds()))
            new_cr.commit()
            new_cr.close()
        return True