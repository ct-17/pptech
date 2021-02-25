from openerp import models, fields, api, SUPERUSER_ID, sql_db
from openerp.http import request
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DSDF
from openerp.exceptions import except_orm, Warning
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from multiprocessing import cpu_count
CPU = min(cpu_count(), 16)
from datetime import datetime as dt
import logging, sys, random, threading,psycopg2, time
_logger = logging.getLogger(__name__)
DEFAULT_VALID_UNTIL_DAYS = 4
import openerp.addons.decimal_precision as dp


class INITDPSaleOrder(models.Model):
    _inherit = "sale.order"

    def __init__(self, pool, cr):
        # self.listen_channel()
        states = getattr(type(self), 'state')
        state_selection = states._attrs.get('selection', {})
        if ('progress', 'Sales Order') in state_selection and ('sent', 'Quotation Sent') in state_selection:
            state_selection.insert(state_selection.index(('sent', 'Quotation Sent')),
                                                ('chandler_draft', "Draft Quotation"))
            state_selection.insert(state_selection.index(('progress', 'Sales Order')),
                                                ('shipmaster_confirm', "Order Confirmed"))
            state_selection[state_selection.index(('draft', 'Draft Quotation'))] = ('draft', 'Enquiry')
            state_selection[state_selection.index(('progress', 'Sales Order'))] = ('progress', 'Processed')
            state_selection[state_selection.index(('manual', 'Sale to Invoice'))] = ('manual', 'Sale to Purchase')
        # for i in range(0, len(state_selection)):
        #     if 'progress' in state_selection[i]:
        #         state_selection[i] = ('progress', 'Order Confirmed')
        #         break
        return super(INITDPSaleOrder, self).__init__(pool, cr)


class DPSaleOrder(models.Model):
    _inherit = "sale.order"

    date_order = fields.Datetime('Date',
                                  required=True,
                                  readonly=True,
                                  select=True,
                                  states={'chandler_draft': [('readonly', False)],
                                          'sent': [('readonly', False)]},
                                  copy=False,
                                  defaults=fields.Datetime.now()
                                  )
    pending_user_id = fields.Many2one('dp.chandler.temp', 'Pending Salesperson', default=None)
    expire_quote_date = fields.Datetime("Valid Until", readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'chandler_draft': [('readonly', False)]})
    expire_quote_state = fields.Selection([('active', 'Not Expired'),
                                           ('expired', 'Expired')],
                                            "Quotation Expiry Status", default="active")
    bid_status = fields.Selection([('draft', 'Enquiry'),
                                   ('bid_received', 'Quote Received'),
                                   ('negotiation', 'Negotiation'),
                                   ('confirm', 'Purchase Confirmed'),
                                   ('done', 'Processed'),
                                   ('cancel', 'Cancelled by Chandler'),
                                   ('cancel_yourself', 'Cancelled by You'),
                                   ('expired', 'Expired')],
                                  "Bid Status", default="draft")
    bid_number = fields.Char("Bid Number")
    # markup_amount = fields.Float("Mark-up Amount")

    currency_rate = fields.Float("Rate", default=1, digits=dp.get_precision('Product Price'))
    order_line = fields.One2many('sale.order.line', 'order_id', 'Order Lines', readonly=True,
                                  # states={'chandler_draft': [('readonly', False)],
                                  #         'draft': [('readonly', False)],
                                  #         'sent': [('readonly', False)],
                                  #         'shipmaster_confirm': [('readonly', False)]},
                                  copy=True)
    show_confirm_prompt = fields.Boolean(compute='_check_confirmation_prompt')
    street = fields.Char(related='user_id.street')
    show_street = fields.Boolean(compute='compute_show_address')
    street2 = fields.Char(related='user_id.street2')
    show_street2 = fields.Boolean(compute='compute_show_address')
    zip = fields.Char(related='user_id.zip')
    show_zip = fields.Boolean(compute='compute_show_address')
    require_send_adjust_mail = fields.Boolean(default=False)

    @api.multi
    def action_cancel(self):
        self.write({'bid_status': 'expired' if self._context.get('expire', False) else 'cancel'})
        res = super(DPSaleOrder, self).action_cancel()
        # comment wait next phase
        if not self._context.get('expire', False):
            try:
                sale_ids = [sale.id for sale in self]
                len_sale_ids = len(sale_ids)
                i = 0
                threads = []
                total_sale_ids_thread = len_sale_ids / CPU
                for i in range(0, CPU - 1):
                    t = threading.Thread(target=self.with_context({'chandler': True}).send_cancel_email_multithreading,
                                         args=(sale_ids[i * total_sale_ids_thread: total_sale_ids_thread * (i + 1)],))
                    threads.append(t)
                    t.start()
                t = threading.Thread(target=self.with_context({'chandler': True}).send_cancel_email_multithreading,
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
        return res

    @api.model
    def send_cancel_email_multithreading(self, sale_id):
        _logger.info(
            '------------------------------------------------------ dp_sale.sale_order.send_cancel_email_multithreading START THREAD')
        with api.Environment.manage():
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            uid = self.env.uid
            start_thread = dt.now()
            new_env = api.Environment(new_cr, uid, self.env.context.copy())
            new_self = self.with_env(new_env)
            for record in new_self.env['sale.order'].browse(sale_id):
                try:
                    # time.sleep(random.randrange(1,5,1))
                    send_template = new_self.env.ref('dp_sale.cancel_quote_to_chandler_email')
                    _logger.info('dp_sale.cancel_quote_to_chandler_email START')
                    send_template.with_context({'email_bcc': True,
                                                'chandler': record._context.get('chandler', False)}).send_mail(record.id, force_send=True, raise_exception=True)
                    _logger.info('dp_sale.cancel_quote_to_chandler_email SUCCESS')
                    _logger.info(
                        'Sale Order: {sale_id} email template had been successfully sent'.format(sale_id=str(record)))
                except psycopg2.InternalError:
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    continue
                except Exception as e:
                    _logger.exception('{} While sending accepted invitation exception generated'.format(record))
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)

                try:
                    send_template2 = new_self.env.ref('dp_sale.cancel_quote_to_shipmaster_email')
                    # time.sleep(random.randrange(1,5,1))
                    _logger.info('dp_sale.cancel_quote_to_shipmaster_email START')
                    send_template2.with_context({'email_bcc': True,
                                                'chandler': record._context.get('chandler', False)}).send_mail(record.id,
                                                                              force_send=True,
                                                                              raise_exception=True)
                    _logger.info('dp_sale.cancel_quote_to_shipmaster_email SUCCESS')
                    _logger.info(
                        'Sale Order: {sale_id} email template had been successfully sent to {receipient}'.format(
                            sale_id=str(record), receipient=record.user_id.partner_id.email))
                except psycopg2.InternalError:
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    continue
                except Exception as e:
                    _logger.exception('{} While sending accepted invitation exception generated'.format(record))
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
            finish_thread = dt.now() - start_thread
            _logger.info((
                             '------------------------------------------------------ dp_sale.sale_order.send_cancel_email_multithreading TIME FINISH 1 thread: %s') \
                         % (finish_thread.total_seconds()))
            new_cr.commit()
            new_cr.close()
        return True

    @api.model
    @api.depends('street')
    def compute_show_address(self):
        for record in self:
            record.show_street, record.show_street2, record.show_zip = True, True, True
            if record.street in ('', None, False):
                record.show_street = False
            if record.street2 in ('', None, False):
                record.show_street2 = False
            if record.zip in ('', None, False):
                record.show_zip = False

    #overwrite base sale order write, to disable quoatation creaed email.
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order', context=context) or '/'
        if vals.get('partner_id') and any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id', 'fiscal_position']):
            defaults = self.onchange_partner_id(cr, uid, [], vals['partner_id'], context=context)['value']
            if not vals.get('fiscal_position') and vals.get('partner_shipping_id'):
                delivery_onchange = self.onchange_delivery_id(cr, uid, [], vals.get('company_id'), None, vals['partner_id'], vals.get('partner_shipping_id'), context=context)
                defaults.update(delivery_onchange['value'])
            vals = dict(defaults, **vals)
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(DPSaleOrder, self).create(cr, uid, vals, context=ctx)
        # self.message_post(cr, uid, [new_id], body=_("Quotation created"), context=ctx)
        return new_id

    @api.model
    def create(self, values):
        sale_obj = super(DPSaleOrder, self).create(values)
        if isinstance(sale_obj, object):
            if sale_obj.exists():
                if sale_obj.date_order:
                    default_days = self.env['ir.config_parameter'].search([('key', '=', 'default_valid_until_days')]).value
                    if default_days in (None, False, ''):
                        # hard code in case someone delete the key, SO still able to create without issue; fail safe
                        default_days = 7
                    expire_date = dt.strptime(sale_obj.date_order, '%Y-%m-%d %H:%M:%S')+relativedelta(days=int(default_days))
                    expire_date = expire_date.strftime('%Y-%m-%d %H:%M:%S')
                    sale_obj.expire_quote_date = expire_date
        return sale_obj

    @api.one
    def copy(self, default=None):
        self.check_expire_date_greater_than_date_order(context={'copy': True})
        self.check_expire_date_max_seven_days(context={'copy': True})
        default.update(bid_status='draft')
        res = super(DPSaleOrder, self).copy(default=default)
        res.write({'state': 'chandler_draft'})
        return res

    @api.depends('order_line', 'amount_total')
    def _check_confirmation_prompt(self):
        for record in self:
            zero_value_product = [True if (line.margin_amount <= 0 and line.item_type_product != 'foc') else False for line in record.order_line]
            total = [True if record.amount_total == 0 else False]
            comparison_lists = zero_value_product + total

            record.show_confirm_prompt = False
            if any(comparison_lists):
                record.show_confirm_prompt = True

    @api.multi
    def action_dp_quotation_send(self):
        zero_value_product = [True if (line.price_subtotal == 0 and line.item_type_product != 'foc') else False for line
                              in self.order_line]
        total = [True if self.amount_total == 0 else False]
        comparison_lists = zero_value_product + total
        if any(comparison_lists):
            raise except_orm(_('Unable to proceed!'),
                             _('You may be making a loss, kindly review your quotation again.\n Click Ok to proceed.'))
        try:
            sale_ids = [sale.id for sale in self]
            len_sale_ids = len(sale_ids)
            i = 0
            threads = []
            total_sale_ids_thread = len_sale_ids / CPU
            for i in range(0, CPU - 1):
                t = threading.Thread(target=self.send_email_multithreading,
                                     args=(sale_ids[i * total_sale_ids_thread: total_sale_ids_thread * (i + 1)],))
                threads.append(t)
                t.start()
            t = threading.Thread(target=self.send_email_multithreading,
                                 args=(sale_ids[(i + 1) * total_sale_ids_thread:],))
            t.start()
            threads.append(t)
            # chan.chandler.send_email_multithreading(request.session, sale_id, context_dict)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('Multithreading Problems')

        self.write({'state': 'sent', 'bid_status': 'bid_received'})
        self.order_line.write({'shipmaster_update': False})

    @api.model
    def send_email_multithreading(self, sale_id):
        _logger.info('------------------------------------------------------ dp_sale.sale_order.send_email_multithreading START THREAD')
        with api.Environment.manage():
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            uid = self.env.uid
            start_thread = dt.now()
            new_env = api.Environment(new_cr, uid, self.env.context.copy())
            new_self = self.with_env(new_env)
            for record in new_self.env['sale.order'].browse(sale_id):
                has_foc = any(i == 'foc' for i in record.order_line.mapped(lambda x: x.item_type_product))
                send_template = new_self.env.ref('dp_sale.chendler_send_quotation_to_shipmaster_email')
                try:
                    # time.sleep(random.randrange(1,5,1))
                    send_template.with_context({'subject': 'BUYTAXFREE {}: Quotation Received, Please Review'.format(str(record.name)),
												'email_bcc': True, 
												'has_foc': has_foc}).send_mail(record.id, force_send=True, raise_exception=True)
                    _logger.info('dp_sale.chendler_send_quotation_to_shipmaster_email SUCCESS')
                    _logger.info(
                        'Sale Order: {sale_id} email template had been successfully sent'.format(sale_id=str(record)))
                except psycopg2.InternalError:
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
                    continue
                except Exception as e:
                    _logger.exception('{} While sending accepted invitation exception generated'.format(record))
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)

                try:
                    # time.sleep(random.randrange(1,5,1))
                    send_template.with_context({'subject': 'BUYTAXFREE {}: Quotation Sent Successfully'.format(str(record.name)),
                                                'chan_email': record.user_id.partner_id.email,
                                                'email_bcc': True,
												'has_foc': has_foc}).send_mail(record.id,
                                                                                force_send=True,
                                                                                raise_exception=True)
                    _logger.info('dp_sale.chendler_send_quotation_to_shipmaster_email SUCCESS')
                    _logger.info(
                        'Sale Order: {sale_id} email template had been successfully sent to {receipient}'.format(
                            sale_id=str(record), receipient=record.user_id.partner_id.email))
                except psycopg2.InternalError:
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
                    continue
                except Exception as e:
                    _logger.exception('{} While sending accepted invitation exception generated'.format(record))
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
            finish_thread = dt.now() - start_thread
            _logger.info(('------------------------------------------------------ dp_sale.sale_order.send_email_multithreading TIME FINISH 1 thread: %s') \
                            % (finish_thread.total_seconds()))
            new_cr.commit()
            new_cr.close()
        return True

    @api.multi
    def action_dp_quotation_send_again(self):
        if self.state == 'sent' and self.bid_status == 'bid_received':
            zero_value_product = [True if (line.price_subtotal == 0 and line.item_type_product != 'foc') else False for line in self.order_line]
            total = [True if self.amount_total == 0 else False]
            comparison_lists = zero_value_product + total
            if any(comparison_lists):
                raise except_orm(_('Unable to proceed!'), _('You may be making a loss, kindly review your quotation again.\n Click Ok to proceed.'))
            else:
                try:
                    sale_ids = [sale.id for sale in self]
                    len_sale_ids = len(sale_ids)
                    i = 0
                    threads = []
                    total_sale_ids_thread = len_sale_ids / CPU
                    for i in range(0, CPU - 1):
                        t = threading.Thread(target=self.send_revised_quotation_multithreading,
                                             args=(sale_ids[i * total_sale_ids_thread: total_sale_ids_thread * (i + 1)],))
                        threads.append(t)
                        t.start()
                    t = threading.Thread(target=self.send_revised_quotation_multithreading,
                                         args=(sale_ids[(i + 1) * total_sale_ids_thread:],))
                    t.start()
                    threads.append(t)
                    # chan.chandler.send_email_multithreading(request.session, sale_id, context_dict)
                except Exception:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    _logger.error('Multithreading Problems')
        else:
            raise except_orm(_('OOPS!'),
                             _('It seems that the quotation has changed state before you can re-send revised quotation.'))
        self.order_line.write({'shipmaster_update': False})

    @api.model
    def send_revised_quotation_multithreading(self, sale_id):
        _logger.info('------------------------------------------------------ dp_sale.sale_order.send_revised_quotation_multithreading START THREAD')
        with api.Environment.manage():
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            uid = self.env.uid
            start_thread = dt.now()
            new_env = api.Environment(new_cr, uid, self.env.context.copy())
            new_self = self.with_env(new_env)
            for record in new_self.env['sale.order'].browse(sale_id):
                has_foc = any(i == 'foc' for i in record.order_line.mapped(lambda x: x.item_type_product))
                send_template = new_self.env.ref('dp_sale.revised_quotation_to_shipmaster')
                try:
                    _logger.info('dp_sale.revised_quotation_to_shipmaster START')
                    # send revised quotation to shipmaster
                    send_template.with_context({'email_bcc': True, 'has_foc': has_foc}).send_mail(record.id, force_send=True, raise_exception=True)
                    _logger.info('dp_sale.revised_quotation_to_shipmaster SUCCESS')
                    _logger.info(
                        'Sale Order: {sale_id} email template had been successfully sent'.format(sale_id=str(record)))
                except psycopg2.InternalError:
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
                    continue
                except Exception as e:
                    _logger.exception('{} While sending accepted invitation exception generated'.format(record))
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)

                try:
                    _logger.info('dp_sale.revised_quotation_to_shipmaster START')
                    # send revised quotation to chandler
                    send_template.with_context({'chan_email': record.user_id.partner_id.email,
                                                'email_bcc': True,
                                                'has_foc': has_foc}).send_mail(record.id, force_send=True,
                                                                                raise_exception=True)
                    _logger.info('dp_sale.revised_quotation_to_shipmaster SUCCESS')
                    _logger.info(
                        'Sale Order: {sale_id} email template had been successfully sent'.format(
                            sale_id=str(record)))
                except psycopg2.InternalError:
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
                    continue
                except Exception as e:
                    _logger.exception('{} While sending accepted invitation exception generated'.format(record))
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)

            finish_thread = dt.now() - start_thread
            _logger.info(('------------------------------------------------------ dp_sale.sale_order.send_revised_quotation_multithreading TIME FINISH 1 thread: %s') \
                            % (finish_thread.total_seconds()))
            new_cr.commit()
            new_cr.close()
        return True

    @api.model
    def get_np_sales_email(self):
        config_param_obj = self.env['ir.config_parameter'].search([('key', '=', 'np_sales_email_parameter')])
        if config_param_obj.exists():
            return config_param_obj.value

    @api.model
    def get_btf_support_email(self):
        config_param_obj = self.env['ir.config_parameter'].search([('key', '=', 'btf_support_email_parameter')])
        if config_param_obj.exists():
            return config_param_obj.value

    @api.model
    def get_chandler_order_url(self):
        """ This method used to generate saleorder url with specific order id.
            Change accordingly your needs.
        """
        # return self.env['ir.config_parameter'].search(
        #     [('key', '=', 'web.base.url')]).value + "/web?#id={}&view_type=form&model=sale.order".format(self.id)
        return "/web?#id={}&view_type=form&model=sale.order&action={}".format(self.id, self.env.ref('sale.action_orders').id)

    @api.model
    def get_shipmaster_order_url(self):
        """ This method used to generate saleorder url with specific order id.
            Change accordingly your needs.
        """
        # return self.env['ir.config_parameter'].search(
        #     [('key', '=', 'web.base.url')]).value + "/web?#id={}&view_type=form&model=sale.order".format(self.id)
        return "/web?#id={}&view_type=form&model=sale.order&action={}".format(self.id, self.env.ref('dp_sale_extend.dp_shipmaster_request_quotation_my_orders').id)

    @api.model
    def get_company_url(self):
        """ This method used to generate erp link.
            Change accordingly your needs.
        """
        return self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value

    @api.model
    def get_current_timestamp(self):
        """ This method used to generate current timestamp from server.(Using in email template) [Temp Method]
            Change accordingly your needs.
        """
        return str(dt.now())[:16]

    @api.model
    def get_chandler(self):
        if bool(self.pending_user_id):
            return self.pending_user_id
        else:
            return self.user_id

    @api.model
    def get_official_reply_email(self):
        return self.env['ir.config_parameter'].sudo().search([('key', '=', 'platform_administrator_email')]).value or ""

    @api.multi
    def tmp_send_mail(self):
        """ This method is temp used for testing purpose only ( email Without attachment)
            Change accordingly your needs.
        """
        # template = self.env.ref("dp_sale.confirm_order_from_web_by_shipmaster_to_chandler_email")
        # template.send_mail(self.id, force_send=True, raise_exception=True)
        has_foc = any(i == 'foc' for i in self.order_line.mapped(lambda x: x.item_type_product))
        template1 = self.env.ref('dp_sale.request_confirm_from_shipmaster_to_chandeler_email')
        template1.attachment_ids.try_remove()
        _logger.info('------------------------------------------------------ dp_sale.request_confirm_from_shipmaster_to_chandeler_email START')
        template1.with_context({'email_bcc': True, 'has_foc': has_foc}).send_mail(self.id, force_send=True, raise_exception=True)
        _logger.info('------------------------------------------------------ dp_sale.request_confirm_from_shipmaster_to_chandeler_email SUCCESS')
        template2 = self.env.ref('dp_sale.request_confirm_from_shipmaster_to_shipmaser_email')
        template2.attachment_ids.try_remove()
        _logger.info('------------------------------------------------------ dp_sale.request_confirm_from_shipmaster_to_shipmaser_email START')
        template2.with_context({'email_bcc': True, 'has_foc': has_foc}).send_mail(self.id, force_send=True, raise_exception=True)
        _logger.info('------------------------------------------------------ dp_sale.request_confirm_from_shipmaster_to_shipmaser_email SUCCESS')
        return True

    @api.multi
    def tmp_attached_send_mail(self):
        """ This method is temp used for testing purpose only (email With attachment)
            Change accordingly your needs.
        """
        return True

    @api.model
    def send_email_to_other_chandler_on_checkout(self):
        try:
            chandler_template = self.env.ref('dp_sale.notification_to_other_chander_from_shipmaster_email')
            chandler_template.with_context({'email_bcc': True}).send_mail(self.id, force_send=True, raise_exception=True)
            _logger.info('dp_sale.notification_to_other_chander_from_shipmaster_email SUCCESS')
            _logger.info('Sale Order: {sale_id} email template had been successfully sent'.format(sale_id=str(self)))
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.exception('{} While sending accepted invitation exception generated'.format(self))

    @api.model
    def send_email_to_preferred_chandler_on_checkout(self):
        try:
            chandler_template = self.env.ref('dp_sale.confirm_order_from_web_by_shipmaster_to_chandler_email')
            chandler_template.send_mail(self.id, force_send=True, raise_exception=True)
            _logger.info('dp_sale.confirm_order_from_web_by_shipmaster_to_chandler_email SUCCESS')
            _logger.info('Sale Order: {sale_id} email template had been successfully sent'.format(sale_id=str(self)))
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.exception('{} While sending accepted invitation exception generated'.format(self))

    @api.model
    def send_email_to_shipmaster_on_checkout(self):
        try:
            shipmaster_template = self.env.ref('dp_sale.confirm_order_from_web_by_shipmaster_email')
            shipmaster_template.send_mail(self.id, force_send=True, raise_exception=True)
            _logger.info('dp_sale.confirm_order_from_web_by_shipmaster_email SUCCESS')
            _logger.info('Sale Order: {sale_id} email template had been successfully sent'.format(sale_id=str(self)))
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.exception('{} While sending accepted invitation exception generated'.format(self))

    @api.model
    def send_email_to_chandler_on_quotation_expiry(self):
        try:
            template = self.env.ref('dp_sale.quotation_expired_to_chandler_email')
            template.with_context({'email_bcc': True}).send_mail(self.id, force_send=True, raise_exception=True)
            _logger.info('dp_sale.quotation_expired_to_chandler_email SUCCESS')
            _logger.info('Sale Order: {sale_id} email template had been successfully sent'.format(sale_id=str(self)))
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.exception('{} While sending accepted invitation exception generated'.format(self))

    @api.model
    def send_email_to_shipmaster_on_quotation_expiry(self):
        try:
            template = self.env.ref('dp_sale.quotation_expired_to_shipmaster_email')
            template.with_context({'email_bcc': True}).send_mail(self.id, force_send=True, raise_exception=True)
            _logger.info('dp_sale.quotation_expired_to_shipmaster_email SUCCESS')
            _logger.info('Sale Order: {sale_id} email template had been successfully sent'.format(sale_id=str(self)))
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.exception('{} While sending accepted invitation exception generated'.format(self))

    @api.multi
    def bid_confirm_order(self):
        stock_allocation_ids = self.order_line.mapped(lambda x:x.stock_allocation_id)
        stock_allocation_states = stock_allocation_ids.mapped(lambda x: x.state)
        if all(state == 'ongoing' for state in stock_allocation_states):
            self.state = 'shipmaster_confirm'
            msg_id = self.env['mail.message'].search([('res_id', '=', self.id), ('model', '=', 'sale.order')]).mapped(lambda x:x.id)
            notification = self.env['mail.notification'].sudo().search(
                [('message_id', 'in', msg_id), ('partner_id', '=', self.user_id.partner_id.id)])
            notification.write({'is_read': False})
            self.bid_status = 'confirm'
            self.order_line.sudo().write({'state': 'confirmed'})
            stock_allocation_ids.write({'state': 'done'})
            self.tmp_send_mail()
            return True
        else:
            sale_order_ids = [sol.id for sol in filter(lambda x: x.state == 'confirmed', stock_allocation_ids.mapped(lambda y: y.order_line))]
            sale_line_objs = self.env['sale.order.line'].browse(sale_order_ids)
            sale_objs = sale_line_objs.mapped(lambda x: x.order_id)
            raise except_orm(_('You have already confirmed one this order with another chandler in {sale_id}'.format(sale_id=','.join(sale.name for sale in sale_objs))),
                             _('If you wish to perform the similar order transaction with another chandler, \n'
                               'you should perform the same transaction from the website to the chandler'))

    @api.multi
    def bid_cancel(self):
        self.state = 'cancel'
        self.bid_status = 'cancel_yourself'
        self.order_line.with_context({'bid_cancel': True}).sudo().write({'state' : 'cancel'})

        try:
            sale_ids = [sale.id for sale in self]
            len_sale_ids = len(sale_ids)
            i = 0
            threads = []
            total_sale_ids_thread = len_sale_ids / CPU
            for i in range(0, CPU - 1):
                t = threading.Thread(target=self.send_cancel_email_multithreading,
                                     args=(sale_ids[i * total_sale_ids_thread: total_sale_ids_thread * (i + 1)],))
                threads.append(t)
                t.start()
            t = threading.Thread(target=self.send_cancel_email_multithreading,
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
        return True

    @api.multi
    def bid_negotiate(self):
        return True

    # @api.onchange('currency_id')
    # def _onchange_currency_id(self):
    #     if self.user_id.partner_id.currency_line:
    #         chan_curr_rate = {curr.currency_id.id:curr.sale_rate for curr in self.user_id.partner_id.currency_line} \
    #         or {self.user_id.company_id.currency_id.id: self.user_id.company_id.currency_id.rate}
    #         self.currency_rate = chan_curr_rate[self.currency_id.id] or 0.00
    #
    #         for line in self.order_line:
    #             from_currency = self.company_id.currency_id
    #
    #             ctx = {
    #                 'voucher_special_currency': from_currency.id or False,
    #                 'voucher_special_currency_rate': 1
    #             }
    #             from_currency = self.env['res.currency'].with_context(ctx).browse(from_currency.id)
    #             ctx = {
    #                 'voucher_special_currency': self.currency_id and self.currency_id.id or False,
    #                 'voucher_special_currency_rate': self.currency_rate or 1
    #             }
    #             to_currency = self.env['res.currency'].with_context(ctx).browse(self.currency_id.id)
    #             rate = to_currency.rate/from_currency.rate
    #             line.purchase_price = line.base_purchase_price / rate
    #             self.update_price_unit(line)

    @api.model
    def update_price_unit(self, line):
        line.price_unit = line.purchase_price




    @api.multi
    def _website_product_id_change(self, order_id, product_id, qty=0, line_id=None):
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
        so = self.env['sale.order'].browse(order_id)

        values = self.env['sale.order.line'].product_id_change([],
            product=product_id,
            partner_id=so.partner_id.id,
            fiscal_position=so.fiscal_position.id,
            qty=qty)['value']

        if line_id:
            line = self.env['sale.order.line'].browse(line_id)
            values['name'] = line.name
        else:
            product = self.env['product.product'].browse(product_id)
            # values['name'] = product.description_sale and "%s\n%s" % (product.display_name, product.description_sale) or product.display_name
            values['name'] = product.display_name

        values['product_id'] = product_id
        values['order_id'] = order_id
        values['from_website'] = True
        if values.get('tax_id') != None:
            values['tax_id'] = [(6, 0, values['tax_id'])]
        return values

    @api.model
    def cron_check_expire_quotation(self):
        sale_objs = self.env['sale.order'].search([('expire_quote_state', '=', 'active'),
                                                   ('state', 'in', ('draft', 'chandler_draft', 'sent'))],
                                                  order='id')
        for sale in sale_objs:
            now = dt.now()
            try:
                expiry = dt.strptime(sale.expire_quote_date, '%Y-%m-%d %H:%M:%S')
            except:
                expiry = None

            if expiry is not None:
                if now > expiry:
                    try:
                        sale.write({'expire_quote_state': 'expired'})
                        sale.with_context(expire=True).action_cancel()
                        # sale.send_email_to_chandler_on_quotation_expiry()
                        # sale.send_email_to_shipmaster_on_quotation_expiry()
                    except Exception as e:
                        sale._cr.rollback()
                        sale.write({'expire_quote_state': 'active'})
                        _logger.info(e)
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        _logger.error('Exception Type: ' + str(exc_type))
                        _logger.error('Exception Error Description: ' + str(exc_obj))
                        _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                        _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                        _logger.info('sale: {sale}, expiry: {expire}, now: {now}'.format(sale=str(sale),
                                                                                         expire=expiry.strftime('%d-%m-%Y'),
                                                                                         now=now.strftime('%d-%m-%Y')))

    @api.multi
    def write(self, vals):
        self.check_expire_date_greater_than_date_order(context={'write': {'expire_quote_date': vals.get('expire_quote_date', False)}})
        self.check_expire_date_max_seven_days(context={'write': {'expire_quote_date': vals.get('expire_quote_date', False)}})

        if 'currency_id' in vals and self.env.user.id != 1:
            return super(DPSaleOrder, self).sudo().write(vals)
        res = super(DPSaleOrder, self).write(vals)
        # function to send email to chandler if shipmaster change anything on order_line
        if self._context.get('shipmaster_form', False) and vals.get('order_line', False):
            self.require_send_adjust_mail = True
        #     self.send_email_to_chandler_on_shipmaster_quotation_adjustment()
        return res

    @api.multi
    def action_send_adjustment_email(self):
        self.send_email_to_chandler_on_shipmaster_quotation_adjustment()
        self.require_send_adjust_mail = False

    # send email on shipmaster change order line
    @api.model
    def send_email_to_chandler_on_shipmaster_quotation_adjustment(self):
        try:
            template = self.env.ref('dp_sale.adjust_order_line_to_chandler_from_shipmaster')
            template.with_context({'email_bcc': True}).send_mail(self.id, force_send=True, raise_exception=True)
            template1 = self.env.ref('dp_sale_extend.adjust_order_line_to_chandler_from_chandler_myenqiury')
            template1.send_mail(self.id, force_send=True, raise_exception=True)
            _logger.info('dp_sale.adjust_order_line_to_chandler_from_shipmaster SUCCESS')
            _logger.info('Sale Order: {sale_id} email template had been successfully sent'.format(sale_id=str(self)))
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.exception('{} While sending accepted invitation exception generated'.format(self))

    @api.onchange('expire_quote_date')
    def onchange_expire_quote_date(self):
        self.check_expire_date_greater_than_date_order()
        self.check_expire_date_max_seven_days()
        return self.expire_quote_date

    @api.model
    def check_expire_date_greater_than_date_order(self, context={}):
        msg = 'Please select a date equal/or greater than Date'
        if context.get('copy', False):
            msg = 'Unable to duplicate Order as valid until date is lesser than Date'
        compare_date = self.expire_quote_date
        if context.get('write', False):
            if context['write'].get('expire_quote_date', False):
                compare_date = context['write']['expire_quote_date']
        if compare_date and self.date_order:
            if dt.strptime(compare_date, DSDF) < dt.strptime(self.date_order, DSDF):
                raise Warning(msg)

    @api.model
    def check_expire_date_max_seven_days(self, context={}):
        default_days = self.env['ir.config_parameter'].search([('key', '=', 'default_expire_date_max_n_days')]).value
        if default_days in (None, False, ''):
            # hard code in case someone delete the key, SO still able to create without issue; fail safe
            default_days = 21
        msg = 'Please select a date equal/or greater than Date by {} days'.format(str(default_days))
        if context.get('copy', False):
            msg = 'Unable to duplicate Order as valid until date is greater than Date + {} days'.format(str(default_days))
        compare_date = self.expire_quote_date
        if context.get('write', False):
            if context['write'].get('expire_quote_date', False):
                compare_date = context['write']['expire_quote_date']
        if compare_date and self.date_order:
            if dt.strptime(compare_date, DSDF) > (dt.strptime(self.date_order, DSDF)+relativedelta(days=int(default_days))):
                raise Warning(msg)

    @api.multi
    def action_button_confirm(self):
        chan_partner_id = self.user_id.partner_id.id
        sm_partner_id = self.partner_id.id

        for order in self:
            for line in order.order_line:
                lsp = self.env['chandler.last.selling.price']
                if chan_partner_id is not False:
                    # deleted users affect this workflow.
                    lsp = lsp.search([('chan_partner_id', '=', chan_partner_id), ('sm_partner_id', '=', sm_partner_id), ('product_id', '=', line.product_id.id)],
                                        order='create_date desc')
                    if lsp.exists():
                        lsp.last_selling_price = line.price_unit
                        lsp.currency_and_rate = order.dp_currency_id.name + "/" + str(order.currency_rate)
                    else:
                        self.env['chandler.last.selling.price'].create({'chan_partner_id': chan_partner_id,
                                                                        'sm_partner_id': sm_partner_id,
                                                                        'product_id': line.product_id.id,
                                                                        'last_selling_price': line.price_unit,
                                                                        'currency_and_rate': order.dp_currency_id.name + "/" + str(order.currency_rate)})
        return super(DPSaleOrder, self).action_button_confirm()