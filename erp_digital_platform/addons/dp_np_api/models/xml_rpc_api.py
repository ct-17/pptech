import xmlrpclib
from openerp import models, fields, api, tools, _
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from openerp.exceptions import Warning, except_orm
from openerp.tools import float_round
import logging, sys
_logger = logging.getLogger('DP NP API')
_state = [('draft', 'Draft'), ('done', 'Done'), ('stock', 'Stock Replenishment'), ('cancel', 'Cancelled'), ('debug', 'Debug')]

import openerp.tools as tools
import os, ssl

options = tools.config.options

class ERPAPIConfiguration(models.Model):
    _name = 'dp.np.api.config'

    active = fields.Boolean('Active')
    url = fields.Char('URL')
    url_port = fields.Char('Port')
    db = fields.Char('Database')
    username = fields.Char('Username')
    password = fields.Char('Password')


class ERPAPI(models.Model):
    _name = 'dp.np.api'

    url = fields.Char('URL')
    url_port = fields.Char('Port')
    db = fields.Char('Database')
    username = fields.Char('Username')
    password = fields.Char('Password')
    dp_np_api_line = fields.One2many('dp.np.api.rel', 'dp_np_api_id')
    state = fields.Selection(_state, 'State', default='draft')

    @api.model
    def _get_credentials_(self, job):
        config_obj = self.env['dp.np.api.config'].search([('active', '=', True)], limit=1)
        try:
            if config_obj.exists():
                job.url = config_obj.url
                job.url_port = config_obj.url_port
                job.db = config_obj.db
                job.username = config_obj.username
                job.password = config_obj.password
            else:
                raise Exception
        except Exception as e:
            _logger.info('{e}'.format(e=e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.info('_get_credentials_: Unable to retrieve ERP credentials')


    @api.model
    def _create_relation_lines(self, context=None):
        # obj of the record
        if context is not None:
            self.env['dp.np.api.rel'].create(context)
        else:
            self.env['dp.np.api.rel'].create({'dp_np_api_id': self.id})

    @api.model
    def _erp_serverproxy(self, job, context={}):
        try:
            if job.url_port:
                job.erp_models = xmlrpclib.ServerProxy('{url}:{url_port}/xmlrpc/2/{type}'.format(url=job.url, url_port=job.url_port, type=context.get('type', '')))
            else:
                job.erp_models = xmlrpclib.ServerProxy('{url}/xmlrpc/2/{type}'.format(url=job.url, type=context.get('type', '')))
        except Exception as e:
            _logger.info('_get_write_uid exception: {e}'.format(e=e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('_get_write_uid: Unable to connect to {url}:{url_port}/xmlrpc/2/{type}'.format(url=job.url, url_port=job.url_port, type=context.get('type', '')))
            if job.url_port:
                _logger.error('{url}:{url_port}/xmlrpc/2/{type}'.format(url=job.url, url_port=job.url_port, type=context.get('type', '')))
            else:
                _logger.error('{url}/xmlrpc/2/{type}'.format(url=job.url, type=context.get('type', '')))
            job.erp_models = None

    @api.model
    def _erp_query(self, job=None, model=None, function=None, args=None, context=None):
        """
        ----------------------------------------------------------------------------------------------------------------
        model - string
        ----------------------------------------------------------------------------------------------------------------
        name of model/table in Odoo e.g. res.partner, res.users etc

        ----------------------------------------------------------------------------------------------------------------
        function - string
        ----------------------------------------------------------------------------------------------------------------
        check_access_rights         - check access rights to read/write/create/unlink
        search                      - retrieve all id of records
        search_count                - count number of records based on args
        read                        - retrieve all columns of records
        fields_get                  - can be used to inspect a model's fields and check which ones seem to be of interest
        name_get                    - get name of record
        search_read                 - shortcut to search followed by read
        create                      - create records
        write                       - update records
        unlink                      - delete records

        ----------------------------------------------------------------------------------------------------------------
        args - list
        ----------------------------------------------------------------------------------------------------------------
        params for function

        'res.partner', 'check_access_rights', ['read']
            - check access rights of read to res.partner
            - string in list

        'res.partner', 'search', [[['is_company', '=', True], ['customer', '=', True]]]
            - search res.partner for records where is_company = True and customer = True
            - list in list

        'res.partner', 'read', [ids]
            - get res.partner record(s) where id in [ids]
            - integers in list

        'res.partner', 'create', [{'name': "New Partner"}]
            - create record in res.partner where name = 'New Partner'
            - dictionary in list

        'res.partner', 'write', [[id], {'name': "Newer partner"}]
            - update record in res.partner where record.id = [id] set name = "Newer Parter"
            - list, dictionary in list

        'res.partner', 'name_get', [[id]]
            - get name of record where id in [id]
            - list in list
            - return [[78, "Newer partner"]]

        'res.partner', 'unlink', [[id]]
            - delete record in res.partner where id in [id]
            - list in list

        ----------------------------------------------------------------------------------------------------------------
        context - dictionary
        ----------------------------------------------------------------------------------------------------------------
        keys - expected values
        raise_exception                         - boolean
        offset                                  - integer
        limit                                   - integer
        fields                                  - list
                                                    e.g. ['name', 'country_id', 'comment']
        attributes                              - list
                                                    e.g. ['string', 'help', 'type']
                                                    e.g. return "ref_companies": {
                                                                            "type": "one2many",
                                                                            "help": "",
                                                                            "string": "Companies that refers to partner"
                                                                        }

        """
        try:
            if options.get('env', False) != 'live':
                _logger.error('Exception: This is not live system')
                return None

            if context is None:
                return job.erp_models.execute_kw(job.db, job.np_write_uid, job.password, model, function, args)
            return job.erp_models.execute_kw(job.db, job.np_write_uid, job.password, model, function, args, context)
        except Exception as e:
            _logger.error('_erp_query exception: {e}'.format(e=e))
            if job.dp_np_api_line.exists():
                if job.dp_np_api_line.error_log is False:
                    job.dp_np_api_line.error_log = ''
                job.dp_np_api_line.error_count += 1
                if job.dp_np_api_line.error_count % 20 == 0:
                    job.dp_np_api_line.error_log = job.dp_np_api_line.error_log[:len(job.dp_np_api_line.error_log)/2]
                job.dp_np_api_line.error_log = str(job.dp_np_api_line.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=e) + '\n\n' + job.dp_np_api_line.error_log
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('_erp_query job: {job}, model: {model}, function: {function}, args: {args}, context: {context}'.format(job=str(job), model=model, function=function, args=str(args), context=str(context)))
            return None

    @api.model
    def erp_query(self, job=None, model=None, function=None, args=None, context=None):
        return self._erp_query(job, model, function, args, context)

    # @api.model
    # def _create_sale_order(self):
    #     """
    #     self._context = {'purchase_order': [{'__last_update': '2019-05-22 07:50:06',
    #                                         'amount_tax': 700.0,
    #                                         'amount_total': 10700.0,
    #                                         'amount_untaxed': 10000.0,
    #                                         'bid_date': False,
    #                                         'bid_validity': False,
    #                                         'company_id': (1, u'ABC Pte Ltd'),
    #                                         'create_date': '2019-05-22 06:44:10',
    #                                         'create_uid': (1, u'admin'),
    #                                         'currency_id': (38, u'SGD'),
    #                                         'date_approve': False,
    #                                         'date_order': '2019-05-22 06:44:10',
    #                                         'dest_address_id': (11, u'shipmaster'),
    #                                         'display_name': u'PO00004',
    #                                         'fiscal_position': False,
    #                                         'id': 4,
    #                                         'incoterm_id': False,
    #                                         'invoice_count': 0,
    #                                         'invoice_ids': [],
    #                                         'invoice_method': u'order',
    #                                         'invoiced': False,
    #                                         'invoiced_rate': 0.0,
    #                                         'journal_id': (2, u'Purchase Journal (SGD)'),
    #                                         'location_id': (9, u'Partner Locations/Customers'),
    #                                         'message_follower_ids': [3],
    #                                         'message_ids': [201, 192, 191],
    #                                         'message_is_follower': True,
    #                                         'message_last_post': '2019-05-22 07:50:08',
    #                                         'message_summary': u' ',
    #                                         'message_unread': False,
    #                                         'minimum_planned_date': '2019-05-23',
    #                                         'name': u'PO00004',
    #                                         'notes': False,
    #                                         'order_line': [4],
    #                                         'origin': False,
    #                                         'partner_id': (3, u'admin'),
    #                                         'partner_ref': False,
    #                                         'payment_term_id': False,
    #                                         'picking_ids': [],
    #                                         'picking_type_id': (6, u'Dropship'),
    #                                         'pricelist_id': (2, u'Default Purchase Pricelist (SGD)'),
    #                                         'product_id': (7, u'IPad Giga'),
    #                                         'related_location_id': (9, u'Partner Locations/Customers'),
    #                                         'related_usage': u'customer',
    #                                         'shipment_count': 0,
    #                                         'shipped': False,
    #                                         'shipped_rate': 0.0,
    #                                         'state': u'confirmed',
    #                                         'total_before_discount': 10000.0,
    #                                         'validator': (1, u'admin'),
    #                                         'website_message_ids': [],
    #                                         'write_date': '2019-05-22 07:50:06',
    #                                         'write_uid': (1, u'admin'),
    #                                         'ws_discount_amount': 0.0,
    #                                         'ws_discount_percent': 0.0,
    #                                         'ws_discount_type': False}],
    #     'purchase_order_line': [{'__last_update': '2019-05-22 07:50:06',
    #                              'account_analytic_id': False,
    #                              'company_id': (1, u'ABC Pte Ltd'),
    #                              'create_date': '2019-05-22 06:44:10',
    #                              'create_uid': (1, u'admin'),
    #                              'date_order': '2019-05-22 06:44:10',
    #                              'date_planned': '2019-05-23',
    #                              'discount': 0.0,
    #                              'discount_amount': 0.0,
    #                              'discount_amount_line': 0.0,
    #                              'display_name': u'IPad Giga',
    #                              'final_price_unit': 1000.0,
    #                              'id': 4,
    #                              'invoice_lines': [],
    #                              'invoiced': False,
    #                              'move_ids': [],
    #                              'name': u'IPad Giga',
    #                              'order_id': (4, u'PO00004'),
    #                              'partner_id': (3, u'admin'),
    #                              'price_subtotal': 10000.0,
    #                              'price_unit': 1000.0,
    #                              'procurement_ids': [],
    #                              'product_id': (7, u'IPad Giga'),
    #                              'product_qty': 10.0,
    #                              'product_uom': (1, u'Unit(s)'),
    #                              'state': u'confirmed',
    #                              'tax_amount': 700.0,
    #                              'taxes_id': [18],
    #                              'write_date': '2019-05-22 07:50:06',
    #                              'write_uid': (1, u'admin'),
    #                              'ws_discount': 0.0}]}
    #     """
    #     try:
    #         self.np_sale_id = self.erp_models.execute_kw(self.db, self.np_write_uid, self.password,
    #                                         'sale.order', 'create', [{
    #                                         'partner_id': self.res_partner_ids[0],
    #                                         'declare_flag': False,
    #                                         'shipping_mark': self.np_vessel_ids[0],
    #                                         'order_type': self.order_type_ids[0],
    #         }])
    #     except:
    #         _logger.info('_create_sale_order: Unable to connect to db: {db}, user: {user}, pw: {pw}, access rights: {ar}'.format(db=self.db, user=self.username, pw=self.password, ar=self.so_create_rights))
    #         self.np_sale_id = None
    #
    # @api.model
    # def _create_sale_order_line(self, line={}):
    #     try:
    #         # if line
    #         self.np_sale_line_id = self.erp_models.execute_kw(self.db, self.np_write_uid, self.password,
    #                                                       'sale.order.line', 'create', [{
    #                                                                 'order_id': self.np_sale_id,
    #                                                                 'product_id': self.product_product_ids[0],
    #                                                                 'product_uom_qty': line.get('product_qty', 0),
    #             }])
    #     except:
    #         _logger.info('_create_sale_order_line: Unable to connect to db: {db}, user: {user}, pw: {pw}, access rights: {ar}'.format(db=self.db, user=self.username, pw=self.password, ar=self.so_create_rights))
    #         self.np_sale_line_id = None

    @api.model
    def create_sale_order(self, job, line):
        so_create_rights = False
        line.np_sale_id = None
        purchase_name = None
        success_state = False
        if line.np_write_uid is not None:
            # check access rights to create in sale order
            so_create_rights = self.erp_query(job, 'sale.order', 'check_access_rights', ['create'], {'raise_exception': False})

        if so_create_rights:
            # create entry in dp_np_api_rel
            try:
                purchase_name = line.dp_purchase_id.name
                sale_name = line.dp_purchase_id.origin
                eta = line.dp_purchase_id.estimated_arrival
                etd = line.dp_purchase_id.estimated_departure
                chand_po_num = line.dp_purchase_id.po_num or ""
                chand_so_num = line.dp_purchase_id.so_num or ""
                chand_marking_num = line.dp_purchase_id.marking_num or ""
                np_note = line.dp_purchase_id.notes or ""
                btf_so = line.dp_purchase_id.origin or ""
                order_remarks = line.dp_purchase_id.order_remarks or ""
                ws_discount_type = line.dp_purchase_id.ws_discount_type or ""
                amount_discount = line.dp_purchase_id.amount_discount or ""
                ws_discount_amount = line.dp_purchase_id.ws_discount_amount or 0
                ws_discount_percent = line.dp_purchase_id.ws_discount_percent or 0

            except:
                pass
            try:
                assert len(self.res_partner_ids) == 1
                # assert len(self.np_vessel_ids) == 1
                assert len(self.order_type_ids) == 1
                # assert len(self.next_port_id) == 1
                # assert len(self.last_port_id) == 1
                args = {
                                                'partner_id': self.res_partner_ids[0],
                                                'declare_flag': False,
                                                'order_type': self.order_type_ids[0],
                                                'ws_discount_type': False,
                                                'amount_discount': amount_discount,
                                                'declare_flag': True,
                                                'date_arrive': eta,
                                                'date_sailing': etd,
                                                'note': np_note,
                                                'loading_place': self.loading_place[0],
                                                # 'chand_so_num': ,
                                                'cpo': chand_po_num,
                                                'chand_marking_num': chand_marking_num,
                                                'origin': purchase_name,
                                                'note':order_remarks
                                                }
                if len(self.next_port_id) == 1:
                    args.update({'next_port': self.next_port_id[0]})
                if len(self.last_port_id) == 1:
                    args.update({'final_port': self.last_port_id[0]})
                if len(self.np_vessel_ids) == 1 and self.is_other_vessel_name is False:
                    args.update({'shipping_mark': self.np_vessel_ids[0],
                                'type_vessel': self.np_vessel_type[0] if self.np_vessel_type else '',
                                'crew_no': self.crew,
                                'nrt': self.nrt,
                                'flag': self.flag})
                if len(self.np_shipping_agent) == 1 and self.is_other_shipping_agent is False:
                    args.update({
                            'shipping_agent': self.np_shipping_agent[0],
                            'ship_agent_registry': line.dp_purchase_id.shipping_agent_id.crNum
                    })
                line.np_sale_id = self.erp_query(job, 'sale.order', 'create', args=[args])
                if ws_discount_type:
                    self.erp_query(job, 'sale.order', 'write',
                                   [[line.np_sale_id], {'ws_discount_type': ws_discount_type,
                                    'ws_discount_amount': ws_discount_amount, 'ws_discount_percent': ws_discount_percent}])

            except AssertionError as ae:
                _logger.error(ae)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('unable to create_sale_order {job}'.format(job=str(job)))
                _logger.error('res_partner_ids={res_partner_ids}, np_vessel_ids={np_vessel_ids}, order_type_ids={order_type_ids}'.format(res_partner_ids=str(self.res_partner_ids), np_vessel_ids=str(self.np_vessel_ids), order_type_ids=str(self.order_type_ids)))
                _logger.error('next_port, last_port can be empty')
                _logger.error('next_port={next_port_id}, last_port={last_port_id}'.format(next_port_id=str(self.next_port_id), last_port_id=str(self.last_port_id)))
            except Exception as e:
                _logger.error(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('unable to create_sale_order {job}'.format(job=str(job)))
                _logger.error('unable to create_sale_order {line}'.format(line=str(line)))

        else:
            if line.error_log is False:
                line.error_log = ''
            line.error_count += 1
            if line.error_count % 20 == 0:
                line.error_log = line.error_log[:len(line.error_log)/2]
            line.error_log = str(line.error_count) + '\t' + \
                            (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + '\t' + \
                            'partner_id : {partner_id}, shipping_mark: {shipping_mark}, order_type: {order_type}, cpo: {purchase_name}'.format(partner_id=str(self.res_partner_ids), shipping_mark=str(self.np_vessel_ids), order_type=str(self.order_type_ids), purchase_name=str(purchase_name)) + \
                            '\n' + line.error_log
            _logger.error('create_sale_order: Unable to create record in ERP db {db}, user_id {user_id} password {pw} has {rights} create sale order rights'.format(db=job.db, user_id=job.np_write_uid, pw=job.password, rights=so_create_rights))

        if line.np_sale_id is not None and line.np_sale_id != 0:
            for oline in line.dp_purchase_id.order_line:
                self.np_sale_line_id = None
                try:
                    self.product_product_ids = self.erp_query(job, 'product.product', 'search',
                                                            [[['default_code', '=', oline.product_id.default_code]]],
                                                            {'limit': 1}) or None
                except Exception as e:
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    _logger.error('job: {job}, product_id: {product_id}}'.format(job=str(job), product_id = str(oline.product_id)))
                if self.product_product_ids is not None:
                    self.np_sale_line_id = self.erp_query(job, 'sale.order.line', 'create', [{
                                                                    'order_id': line.np_sale_id,
                                                                    'product_id': self.product_product_ids[0],
                                                                    'product_uom_qty': oline.product_qty,
                                                                    'price_unit': oline.price_unit,
                                                                    'item_type': False if oline.price_unit else 'foc',
                                                                    'ws_discount': oline.ws_discount,
                                            }])
                else:
                    if line.error_log is False:
                        line.error_log = ''
                    line.error_count += 1
                    if line.error_count % 20 == 0:
                        line.error_log = line.error_log[:len(line.error_log)/2]
                    line.error_log = str(line.error_count) + '\t' + \
                                    (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                     '\t' + oline.product_id.default_code + ' ' + oline.product_id.name_template + \
                                     '\n' + line.error_log
                    _logger.error('create_sale_order: unable to find product {code} {name} in erp database '.format(code=oline.product_id.default_code, name=oline.product_id.name_template))
                self.all_np_sale_line_ids.append(self.np_sale_line_id)
                if self.np_sale_line_id is None:
                    _logger.error('create_sale_order: Unable to create line in sale order in ERP db {db}, user {user_id} password {pw}, product_product_ids {product_product_ids}, np_sale_line_id {np_sale_line_id}'.format(db=job.db, user_id=line.np_write_uid, pw=job.password, product_product_ids=str(self.product_product_ids), np_sale_line_id=self.np_sale_line_id))

            if len(self.all_np_sale_line_ids) > 0 and \
                    (None not in self.all_np_sale_line_ids):
                success_state = True
        elif line.np_sale_id == 0:
            _logger.error('Unable to create SO in ERP, please check ERP Logs')
            if line.error_log is False:
                line.error_log = ''
            line.error_count += 1
            if line.error_count % 20 == 0:
                line.error_log = line.error_log[:len(line.error_log)/2]
            line.error_log = str(line.error_count) + '\t' + \
                            (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + '\t' + \
                             'Unable to create SO in ERP, please check ERP Logs' + '\n' + line.error_log
        return success_state

    @api.model
    def erp_connect(self, job):
        # get write uid in erp server
        self._erp_serverproxy(job, {'type': 'common'})

        try:
            if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
                ssl._create_default_https_context = ssl._create_unverified_context
            job.np_write_uid = job.erp_models.authenticate(job.db, job.username, job.password, {})
        except Exception as e:
            _logger.error('_authenticate exception: {e}'.format(e=e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('_authenticate: Unable to connect to db: {db}, user: {user}, pw: {pw}'.format(db=job.db, user=job.username, pw=job.password))
            if job.url_port:
                _logger.error('{url}:{url_port}/xmlrpc/2/{type}'.format(url=job.url, url_port=job.url_port, type='common'))
            else:
                _logger.error('{url}/xmlrpc/2/{type}'.format(url=job.url, type='common'))
            job.np_write_uid = None

        # get erp models to initiate calling to database tables
        self._erp_serverproxy(job, {'type': 'object'})

        if job.erp_models is None:
            _logger.error('Error Connecting to ERP', 'Please contact System Administrator regarding this issue')

    @api.model
    def create_cron_job(self):
        # create entry in dp_np_api_rel
        if self._context.get('purchase_id', False):
            self._create_relation_lines({
                'dp_np_api_id': self.id,
                'dp_purchase_id': self._context.get('purchase_id', None),
            })

    @api.model
    def run_cron(self):
        cron_jobs = self.sudo().search([('state', '=', 'draft')])
        if self._context.get('direct_from_make_po', False):
            cron_jobs = self
        for job in cron_jobs:
            self._get_credentials_(job)
            try:
                self.partner_code = job.dp_np_api_line.dp_purchase_id.so_id.partner_id.company_code
            except Exception as e:
                self.partner_code = ''
                _logger.error(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('unable to retrieve partner code for job {job}'.format(job=str(job)))
            self.order_type = 'local'
            vessel_name = job.dp_np_api_line.dp_purchase_id.vessel_name.name or 'REMOVAL'
            vessel_type = job.dp_np_api_line.dp_purchase_id.vessel_id.name
            shipping_agent = job.dp_np_api_line.dp_purchase_id.shipping_agent_id.name
            lport_obj = job.dp_np_api_line.dp_purchase_id.last_port_id
            nport_obj = job.dp_np_api_line.dp_purchase_id.next_port_id
            partner_obj = job.dp_np_api_line.dp_purchase_id.dest_address_id

            # self.np_vessel_id = 'REMOVAL'
            if any(cred is None for cred in [job.url, job.url_port, job.db, job.username, job.password]):
                _logger.error(job.url, job.url_port, job.db, job.username, job.password)
            self.erp_connect(job)

            for line in job.dp_np_api_line:
                self.res_partner_ids = self.order_type_ids = self.np_vessel_ids = []
                self.res_partner_ids = self.erp_query(job, 'res.partner', 'search', [[['code', '=', partner_obj.parent_id.company_code if partner_obj.parent_id.company_code else self.partner_code], ['customer', '=', True]]], {'limit': 1})
                self.order_type_ids = self.erp_query(job, 'order.type', 'search', [[['type', '=', self.order_type]]], {'limit': 1})
                self.np_vessel_ids = self.erp_query(job, 'np.vessel', 'search', [[['name', '=', vessel_name]]], {'limit': 1})
                self.np_vessel_type = self.erp_query(job, 'np.vessel.type', 'search', [[['name', '=', vessel_type]]], {'limit': 1})
                self.np_shipping_agent = self.erp_query(job, 'ship.agent', 'search', [[['name', '=', shipping_agent]]], {'limit': 1})
                self.next_port_id = self.erp_query(job, 'custom.port', 'search', [[['name', '=', nport_obj.name],['code', '=', nport_obj.code]]], {'limit': 1})
                self.last_port_id = self.erp_query(job, 'custom.port', 'search', [[['name', '=', lport_obj.name],['code', '=', lport_obj.code]]], {'limit': 1})
                if self.order_type:
                    penjuru_id = self.erp_query(job, 'custom.loading.place', 'search', [[['description', 'like', '%NEW PORT DUTY FREE PTE LTD%']]], {'limit': 1})
                    self.loading_place = penjuru_id

                if not self.np_vessel_ids and vessel_name.upper() != 'OTHERS':
                    self.np_vessel_ids = self.erp_query(job, 'np.vessel', 'search', [[['name', '=', 'BUYTAXFREE']]],
                                                        {'limit': 1})

                self.is_other_vessel_name = False
                if vessel_name.upper() == 'OTHERS':
                    self.is_other_vessel_name = True
                self.is_other_shipping_agent = False
                if shipping_agent:
                    if shipping_agent.upper() == 'OTHERS':
                        self.is_other_shipping_agent = True

                if (any(ids is None for ids in [self.res_partner_ids, self.order_type_ids, self.np_vessel_ids]) or  \
                        any(len(ids) == 0 for ids in [self.res_partner_ids, self.order_type_ids, self.np_vessel_ids])) \
                        and vessel_name.upper() != 'OTHERS':
                    _logger.error('res_partner_ids {res_partner_ids}, order_type_ids {order_type_ids}, np_vessel_ids {np_vessel_ids}'.format(res_partner_ids=str(self.res_partner_ids), order_type_ids=str(self.order_type_ids), np_vessel_ids=str(self.np_vessel_ids)))
                    _logger.error('Error searching records in ERP')
                if self.np_vessel_ids:
                    if len(self.np_vessel_ids) == 1 and self.is_other_vessel_name is False:
                        vessel_name_obj = job.dp_np_api_line.dp_purchase_id.vessel_name
                        self.crew = vessel_name_obj.crew
                        self.nrt = vessel_name_obj.nrt
                        self.flag = vessel_name_obj.flag

                self.all_np_sale_line_ids = []
                create_state = self.create_sale_order(job, line)

                if create_state is False:
                    unlink_line_ids = [idx is not None for idx in self.all_np_sale_line_ids]
                    self.erp_query(job, 'sale.order.line', 'unlink', args=[unlink_line_ids])
                    self.erp_query(job, 'sale.order', 'unlink', args=[[line.np_sale_id]])
                    # Fail to create SO
                    job.write({'state': 'draft'})
                    line.write({'state': 'draft'})
                else:
                    # succeed in create so
                    job.write({'state': 'done'})
                    line.write({'state': 'done'})

    @api.model
    def cron_check_stock_replenishment(self):
        stocks = self.create({'state': 'stock'})
        self._get_credentials_(stocks)
        if any(cred is None for cred in [stocks.url, stocks.url_port, stocks.db, stocks.username, stocks.password]):
            _logger.info(stocks.url, stocks.url_port, stocks.db, stocks.username, stocks.password)
        self.erp_connect(stocks)

        try:
            """
            code
                self.erp_query(stocks, 'sale.order', 'search', [[['dp_flag', '=', True]]], {'limit': 1})
            return: sale order id
                [17423]




            code
                self.erp_query(stocks, 'sale.order.line', 'search_read',
                                [[['order_id', 'in', self.erp_query(stocks, 'sale.order', 'search',
                                                                    [[['dp_flag', '=', True]]], {'limit': 1})]]],
                                {'fields': ['product_id', 'product_uom_qty', 'product_uom']})
            return sale order line fields
                [{'id': 93572,
                'product_id': [3285, 'AML-HP'],
                'product_uom': [40, '1'],
                'product_uom_qty': 1000.0},
                {'id': 93573,
                'product_id': [4491, 'ARK-MOU-50'],
                'product_uom': [32, '1'],
                'product_uom_qty': 1000.0},
                {'id': 93574,
                'product_id': [5110, 'ARK-MOU-20'],
                'product_uom': [32, '1'],
                'product_uom_qty': 1000.0},
                {'id': 93575,
                'product_id': [3981, 'HEIB-33'],
                'product_uom': [51, '0,4166666'],
                'product_uom_qty': 1000.0},
                {'id': 93576,
                'product_id': [3982, 'HEIC-33'],
                'product_uom': [51, '0,4166666'],
                'product_uom_qty': 1000.0},
                {'id': 93577,
                'product_id': [4010, 'TIGB-33'],
                'product_uom': [51, '0,4166666'],
                'product_uom_qty': 1000.0},
                {'id': 93578,
                'product_id': [4011, 'TIGC-33'],
                'product_uom': [51, '0,4166666'],
                'product_uom_qty': 1000.0}]


            code
                self.erp_query(stocks, 'product.uom', 'search_read',
                                                [[['id', 'in', [d['product_uom'][0] for d in np_sale_line]]]],
                                                {'fields': ['name', 'factor']})
            return product uom factor
                [{'factor': 0.08333333333333333, 'id': 32, 'name': 'CTN12'},
                {'factor': 0.041666666666666664, 'id': 51, 'name': 'CTN24'},
                {'factor': 0.02, 'id': 40, 'name': 'CTN50'}]



            code
                self.erp_query(stocks, 'product.product', 'search_read',
                                [[['id', 'in', [d['product_id'][0] for d in np_sale_line]]]],
                                {'fields': ['default_code', 'name_template']})
            return product code
                [{'default_code': 'AML-HP',
                'id': 3285,
                'name_template': 'AMERICAN LEGEND KSF'},
                {'default_code': 'ARK-MOU-20',
                'id': 5110,
                'name_template': 'KWEICHOW MOUTAI CHIEW 53% '},
                {'default_code': 'ARK-MOU-50',
                'id': 4491,
                'name_template': 'KWEICHOW MOUTAI CHIEW 53%'},
                {'default_code': 'HEIB-33',
                'id': 3981,
                'name_template': 'HEINEKEN BEER (BOTTLE)'},
                {'default_code': 'HEIC-33',
                'id': 3982,
                'name_template': 'HEINEKEN BEER (CAN)'},
                {'default_code': 'TIGB-33',
                'id': 4010,
                'name_template': 'TIGER BEER (BOTTLE)'},
                {'default_code': 'TIGC-33', 'id': 4011, 'name_template': 'TIGER BEER'}]


            code
                [dic['default_code'] for dic in np_product]
            return product codes
                ['AML-HP', 'ARK-MOU-20', 'ARK-MOU-50', 'HEIB-33', 'HEIC-33', 'TIGB-33', 'TIGC-33']
            """
            product_objs = self.env['product.template'].search([])
            product_codes = product_objs.mapped('default_code')
            np_product = self.erp_query(stocks,
                                    'product.product',
                                    'search_read',
                                    [[['default_code', 'in', product_codes]]],
                                    {'fields': ['default_code', 'available_qty']})

            # np_sale_line = self.erp_query(stocks,
            #                                'sale.order.line',
            #                                'search_read',
            #                                 [[['order_id', 'in', np_sale]]],
            #                                {'fields': ['product_id', 'product_uom_qty', 'product_uom'], 'context':{'default_code_only': True,
            #                                                                                                        'factor_only': True}})

            for line in np_product:
                product_obj = product_objs.filtered(lambda x:x.default_code == line.get('default_code'))
                product_obj.dp_allocated_qty = int(line.get('available_qty') * (product_obj.percent_allocate /100))
                if not product_obj.np_product_id:
                    product_obj.np_product_id = line.get('id')



            line = self._create_relation_lines({
                'dp_np_api_id': self.id,
                'state': 'stock'
            })

            sr_obj = self.env['stock.replenishment'].create({})
            try:
                sr_obj.stock_replenish_send_email()
            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                if line.error_log is False:
                    line.error_log = ''
                line.error_count += 1
                if line.error_count % 20 == 0:
                    line.error_log = line.error_log[:len(line.error_log)/2]
                line.error_log = str(line.error_count) + '\t' + \
                                (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                 '\t' +  str(exc_type) + ' ' + str(exc_obj) + \
                                 '\t' +  str(exc_tb.tb_frame.f_code.co_filename) + ' ' +  str(exc_tb.tb_lineno) + \
                                 '\n' + line.error_log
        except Exception as e:
            _logger.error(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('cron_check_stock_replenishment: unable to query ERP database')
            _logger.error('{ids}'.format( ids=str(self.erp_query(stocks, 'sale.order', 'search',
                                                                [[['dp_flag', '=', True]]], {'limit': 1}))))

    @api.model
    def cron_debug_erp_query(self, param_dict={}):
        """
        Arguments for debugging erp query (sample)
        ([{'model': 'res.users', 'id': 1}])
        """
        try:
            if param_dict.has_key('model') and param_dict.has_key('id'):
                job = self.create({'state': 'debug'})
                line = job.dp_np_api_line.create({'dp_np_api_id': self.id, 'state':'debug'})

                self._get_credentials_(job)
                if any(cred is None for cred in
                       [job.url, job.url_port, job.db, job.username, job.password]):
                    _logger.info(job.url, job.url_port, job.db, job.username, job.password)
                self.erp_connect(job)
                model = param_dict.get('model', '')
                id = param_dict.get('id', '')
                return_data = self.erp_query(job, model, 'search_read', [[['id', '=', id]]],
                                                      {'limit': 1})
                line.write({'error_log': str(return_data).replace(",", ",\n")})
        except:
            _logger.info('cron_debug_erp_query error. please debug on debug cron  -_-|||')

    # @api.model
    # def data_compiler(self, **kwargs):
    #     somedata = []
    #     if kwargs.has_key('sale_line') and kwargs.has_key('product'):
    #         # compile_data = [ for]
    #         self._data_compiler(kwargs['sale_line'], kwargs['product'], 'product_id')
    #     return somedata
    #
    # @api.model
    # def _data_compiler(self, list1, list2, key):
    #     for dict1 in list1:
    #         if dict1.has_key(key):
    #             pass
    #     pass

class ERPAPIRelationTable(models.Model):
    _name = 'dp.np.api.rel'

    dp_np_api_id = fields.Many2one('dp.np.api', 'DP NP API Key')
    np_write_uid = fields.Integer('Newport ERP User ID')
    dp_purchase_id = fields.Many2one('purchase.order', 'BUYTAXFREE Purchase ID')
    np_sale_id = fields.Integer('Newport ERP Sale ID')
    state = fields.Selection(_state, 'State', default='draft')
    overwrite_state = fields.Selection(_state, 'Overwrite State')
    overwrite_flag = fields.Boolean(default=False)
    error_count = fields.Integer('Error Counter', default=0)
    error_log = fields.Text('Error', default='')

    @api.multi
    def action_enable_overwrite_state(self):
        if self.overwrite_flag is False:
            self.overwrite_flag = True

    @api.multi
    def action_overwrite_state(self):
        if self.overwrite_flag is True:
            self.state = self.overwrite_state
            self.dp_np_api_id.state = self.overwrite_state
            self.overwrite_flag = False