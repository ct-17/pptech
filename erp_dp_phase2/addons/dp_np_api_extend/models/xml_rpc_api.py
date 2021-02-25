import xmlrpclib
from openerp import models, fields, api, tools, _, sql_db
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from psycopg2 import IntegrityError
from openerp.exceptions import Warning, except_orm
from openerp.tools import float_round
import openerp.tools as tools
from multiprocessing import cpu_count
CPU = min(cpu_count(), 16)
import os, logging, sys, json, ast, copy, threading, psycopg2
options = tools.config.options
_logger = logging.getLogger('DP NP API Extend')


class INITDPNPAPIExtend(models.Model):
    _inherit = "dp.np.api"

    def __init__(self, pool, cr):
        states = getattr(type(self), 'state')
        state_selection = states._attrs.get('selection', {})
        if ('stock', 'Stock Replenishment') in state_selection and \
                ('sync_data_to_btf', 'Synchronize Data to BuyTaxFree') not in state_selection:
            state_selection.insert(state_selection.index(('stock', 'Stock Replenishment')), \
                                   ('sync_data_to_btf', 'Synchronize Data to BuyTaxFree'))
        if ('stock', 'Stock Replenishment') in state_selection and \
                ('sync_data_to_erp', 'Synchronize Data to ERP') not in state_selection:
            state_selection.insert(state_selection.index(('stock', 'Stock Replenishment')), \
                                   ('sync_data_to_erp', 'Synchronize Data to ERP'))
        return super(INITDPNPAPIExtend, self).__init__(pool, cr)

class INITDPNPAPIRelExtend(models.Model):
    _inherit = "dp.np.api.rel"

    def __init__(self, pool, cr):
        states = getattr(type(self), 'state')
        state_selection = states._attrs.get('selection', {})
        if ('stock', 'Stock Replenishment') in state_selection and \
                ('sync_data_to_btf', 'Synchronize Data to BuyTaxFree') not in state_selection:
            state_selection.insert(state_selection.index(('stock', 'Stock Replenishment')), \
                                   ('sync_data_to_btf', 'Synchronize Data to BuyTaxFree'))
        if ('stock', 'Stock Replenishment') in state_selection and \
                ('sync_data_to_erp', 'Synchronize Data to ERP') not in state_selection:
            state_selection.insert(state_selection.index(('stock', 'Stock Replenishment')), \
                                   ('sync_data_to_erp', 'Synchronize Data to ERP'))
        return super(INITDPNPAPIRelExtend, self).__init__(pool, cr)

class IsNotPropertyFieldException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class ModelIsNotYYYModelException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class ModelIsNotAccountAccountException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class BuyTaxFreeandNewPortERPDatabaseMatrixDoNotExistException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class ModelDoNotExistInBuyTaxFreeException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class IgnoreFieldsIfNotRequiredInBuyTaxFreeException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class FieldsNotFoundInBuyTaxFreeException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class NoRecordsFoundException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class CreateSyncRecordException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class DeleteSyncRecordException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class DPRecordsNotFoundException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class UnlinkException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class BTFMany2OneFieldIsEmptyException(Exception):
    def __init__(self, *args, **kwargs):
        pass


class WriteException(Exception):
    def __init__(self, *args, **kwargs):
        pass

"""
 _   _       _         _          ____       _                 
| \ | | ___ | |_ ___  | |_ ___   |  _ \  ___| |__  _   _  __ _ 
|  \| |/ _ \| __/ _ \ | __/ _ \  | | | |/ _ \ '_ \| | | |/ _` |
| |\  | (_) | ||  __/ | || (_) | | |_| |  __/ |_) | |_| | (_| |
|_| \_|\___/ \__\___|  \__\___/  |____/ \___|_.__/ \__,_|\__, |
                                                         |___/ 
 _____ _     _       _____ _ _      
|_   _| |__ (_)___  |  ___(_) | ___ 
  | | | '_ \| / __| | |_  | | |/ _ \
  | | | | | | \__ \ |  _| | | |  __/
  |_| |_| |_|_|___/ |_|   |_|_|\___|
Note to debug this file

Due to nature of manual data synchronization between 2 databases via xmlrpc protocols and time constraints
The exception is mainly empty due to:
    1) I am using it to jump from parts of code to other parts of code
    2) Need to enhance the exception handling rather than all the exception throwing same information into logger                

"""


class DPNPAPIExtend(models.Model):
    _inherit = "dp.np.api"

    # README FOR FUTURE REFERENCES
    # api_rel_id is the "correct" implementation,
    # dp_np_api_line is the incorrect implementation, for future usage, use api_rel_id
    api_rel_id = fields.Many2one('dp.np.api.rel')

    @api.model
    def cron_sync_data_to_btf(self):
        """
        expected data, list of dict
        [{'create_date': '2019-10-30 08:11:07',
          'data': '{"is_sync_to_btf": true, "property_stock_account_input_categ": 594, "property_account_creditor_price_difference_categ": 496, "name": "Mala", "parent_id": false, "property_account_expense_categ": false, "property_stock_journal": 9, "route_ids": [[6, false, []]], "property_account_income_categ": false, "property_stock_valuation_account_id": 15, "type": "normal", "property_stock_account_output_categ": 23, "removal_strategy_id": false}',
          'id': 17,
          'keyword': False,
          'priority': 31,
          'sync_action': 'create',
          'sync_model': 'product.category',
          'sync_model_id': 59},
         {'create_date': '2019-10-30 08:11:12',
          'data': '{"name": "Malala"}',
          'id': 18,
          'keyword': "[('name', '=', u'Mala')]",
          'priority': 32,
          'sync_action': 'write',
          'sync_model': 'product.category',
          'sync_model_id': 59},
         {'create_date': '2019-10-30 08:11:26',
          'data': False,
          'id': 19,
          'keyword': "[('name', '=', u'Malala')]",
          'priority': 33,
          'sync_action': 'unlink',
          'sync_model': 'product.category',
          'sync_model_id': 59},
         {'create_date': '2019-10-30 08:14:05',
          'data': '{"active": true, "is_sync_to_btf": true, "contact": "444444", "cr_number": "4444444444444", "name": "titanic"}',
          'id': 20,
          'keyword': False,
          'priority': 21,
          'sync_action': 'create',
          'sync_model': 'ship.agent',
          'sync_model_id': 4336},
         {'create_date': '2019-10-30 08:14:22',
          'data': '{"is_sync_to_btf": true, "code": "BANG", "name": "BANG BANG"}',
          'id': 21,
          'keyword': False,
          'priority': 11,
          'sync_action': 'create',
          'sync_model': 'np.vessel.type',
          'sync_model_id': 184},
         {'create_date': '2019-10-30 08:14:31',
          'data': '{"code": "BANG BANG"}',
          'id': 22,
          'keyword': "[('name', '=', u'BANG BANG')]",
          'priority': 12,
          'sync_action': 'write',
          'sync_model': 'np.vessel.type',
          'sync_model_id': 184},
         {'create_date': '2019-10-30 08:14:49',
          'data': '{"name": "TITANIC"}',
          'id': 23,
          'keyword': "[('name', '=', u'titanic')]",
          'priority': 22,
          'sync_action': 'write',
          'sync_model': 'ship.agent',
          'sync_model_id': 4336},
         {'create_date': '2019-10-30 08:15:04',
          'data': '{"via_desc": false, "is_sync_to_btf": true, "via": false, "name": "VESSEL_NAME", "imo_number": false, "image": "iVBORw0KGgoAAAANSUhEUgAABAAAAAQACAMAAABIw9uxAAADAFBMVEUAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAACzMPSIAAABAHRSTlMA/dCPL0+ucAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\n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\\n", "crew": false, "note": false, "flag": false, "via_group": false, "shipping_agent": false, "type": false, "nrt": false}',
          'id': 24,
          'keyword': False,
          'priority': 91,
          'sync_action': 'create',
          'sync_model': 'np.vessel',
          'sync_model_id': 33292},
         {'create_date': '2019-10-30 08:15:14',
          'data': '{"flag": "SG"}',
          'id': 25,
          'keyword': "[('name', '=', u'VESSEL_NAME')]",
          'priority': 92,
          'sync_action': 'write',
          'sync_model': 'np.vessel',
          'sync_model_id': 33292},
         {'create_date': '2019-10-30 08:21:16',
          'data': '{"track_all": true, "ean13": false, "uos_id": false, "list_price": 0, "classification": 1, "property_stock_procurement": 6, "ess_code": false, "attribute_line_ids": [], "packing_alcohol": false, "consignment_customer": [[6, false, []]], "mes_type": "fixed", "uom_id": 1, "description_purchase": false, "default_code": "FP", "property_account_income": false, "duty_free_product": false, "message_ids": false, "uos_coeff": 1, "sale_ok": true, "message_follower_ids": [[4, 3]], "purchase_ok": true, "product_manager": false, "track_outgoing": false, "company_id": 1, "use_time": 0, "state": false, "loc_rack": false, "uom_po_id": 1, "life_time": 0, "np_uom": [[6, false, []]], "sales_demand_period": 0, "is_sync_to_btf": true, "description": false, "property_account_creditor_price_difference": false, "valuation": "real_time", "track_incoming": false, "property_stock_production": 7, "weight": 0, "supplier_taxes_id": [[6, false, [14]]], "volume": 0, "route_ids": [[6, false, [5]]], "sale_delay": 7, "description_sale": false, "active": true, "property_stock_inventory": 5, "cost_method": "average", "loc_row": false, "loc_case": false, "weight_net": 0, "removal_time": 0, "image_medium": false, "name": "FakeProduct", "type": "product", "property_account_expense": false, "property_stock_account_input": false, "categ_id": 1, "packaging_ids": [], "alert_time": 0, "taxes_id": [[6, false, [5]]], "property_stock_account_output": false, "seller_ids": [], "warranty": 0}',
          'id': 29,
          'keyword': False,
          'priority': 81,
          'sync_action': 'create',
          'sync_model': 'product.template',
          'sync_model_id': 5413},
         {'create_date': '2019-10-30 08:21:16',
          'data': '{"image": false}',
          'id': 26,
          'keyword': "[('name', '=', u'FakeProduct')]",
          'priority': 82,
          'sync_action': 'write',
          'sync_model': 'product.template',
          'sync_model_id': 5413},
         {'create_date': '2019-10-30 08:21:16',
          'data': '{}',
          'id': 27,
          'keyword': "[('name', '=', u'FakeProduct')]",
          'priority': 82,
          'sync_action': 'write',
          'sync_model': 'product.template',
          'sync_model_id': 5413},
         {'create_date': '2019-10-30 08:21:16',
          'data': '{"default_code": "FP"}',
          'id': 28,
          'keyword': "[('name', '=', u'FakeProduct')]",
          'priority': 82,
          'sync_action': 'write',
          'sync_model': 'product.template',
          'sync_model_id': 5413},
         {'create_date': '2019-10-30 08:21:21',
          'data': '{"default_code": "FP11"}',
          'id': 30,
          'keyword': "[('name', '=', u'FakeProduct')]",
          'priority': 82,
          'sync_action': 'write',
          'sync_model': 'product.template',
          'sync_model_id': 5413},
         {'create_date': '2019-10-30 08:21:25',
          'data': False,
          'id': 31,
          'keyword': "[('name', '=', u'FakeProduct')]",
          'priority': 83,
          'sync_action': 'unlink',
          'sync_model': 'product.template',
          'sync_model_id': 5413},
         {'create_date': '2019-10-30 09:44:25',
          'data': '{"via_desc": false, "is_sync_to_btf": true, "via": false, "name": "AAL THELMA", "imo_number": false, "image": "iVBORw0KGgoAAAANSUhEUgAABAAAAAQACAMAAABIw9uxAAADAFBMVEUAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAACzMPSIAAABAHRSTlMA/dCPL0+ucAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\\n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\\n", "crew": false, "note": false, "flag": false, "via_group": false, "shipping_agent": false, "type": false, "nrt": false}',
          'id': 32,
          'keyword': False,
          'priority': 91,
          'sync_action': 'create',
          'sync_model': 'np.vessel',
          'sync_model_id': 33296},
         {'create_date': '2019-10-30 09:45:52',
          'data': '{"imo_number": "1231231231"}',
          'id': 33,
          'keyword': "[('name', '=', u'AAL THELMA')]",
          'priority': 92,
          'sync_action': 'write',
          'sync_model': 'np.vessel',
          'sync_model_id': 33296},
         {'create_date': '2019-10-30 10:15:58',
          'data': '{"is_sync_to_btf": false}',
          'id': 34,
          'keyword': "[('name', '=', u'AAL THELMA')]",
          'priority': 92,
          'sync_action': 'write',
          'sync_model': 'np.vessel',
          'sync_model_id': 33296}]
        """
        job = self.env['dp.np.api']
        try:
            erp_job = self.create({'state': 'sync_data_to_btf'})
            self._get_credentials_(erp_job)
            self.erp_connect(erp_job)
            sorted_erp_records = self.erp_query(erp_job,
                                        'btf.data.sync',
                                        'search_read',
                                        [[['state', 'in', ('pending', 'is_creating_in_btf')]]],
                                        {'fields': ['sync_model', 'sync_model_id', 'sync_action', 'priority', 'keyword', 'data','create_date']})
            sorted_erp_records.sort(key=lambda x: [x['priority'], x['create_date']])

            for rec in sorted_erp_records:
                try:
                    job = self.create({'state': 'sync_data_to_btf'})
                    self._get_credentials_(job)
                    self.erp_connect(job)
                    rel_obj = job.create_relation_lines({'dp_np_api_id': job.id, 'state': 'sync_data_to_btf', 'action_type': rec['sync_action'],
                                                'erp_record': json.dumps(rec)})
                    job.api_rel_id = rel_obj.id
                    action = rec['sync_action']
                    if action == 'write':
                        self.erp_action_sync_write(job, rec)
                    elif action == 'create':
                        self.erp_action_sync_create(job, rec)
                    elif action == 'unlink':
                        self.erp_action_sync_unlink(job, rec)
                    else:
                        raise Exception
                except Exception as ie:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    if job.api_rel_id.exists():
                        if job.api_rel_id.error_log is False:
                            job.api_rel_id.error_log = ''
                        job.api_rel_id.error_count += 1
                        if job.api_rel_id.error_count % 20 == 0:
                            job.api_rel_id.error_log = job.api_rel_id.error_log[:len(job.api_rel_id.error_log) / 2]
                        job.api_rel_id.error_log = str(job.api_rel_id.error_count) + '\t' + \
                                                   (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                                   '\t' + '{e}'.format(e=ie) + '\n\n' + job.api_rel_id.error_log
                    _logger.error(ie)
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                    _logger.error('cron_sync_data_to_btf: unable to query ERP database')
                    continue
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error(e)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('cron_sync_data_to_btf: unable to query ERP database')

    @api.model
    def erp_action_sync_write(self, job, rec):
        """
         _____ ____  ____    _____       ____ _____ _____
        | ____|  _ \|  _ \  |_   _|__   | __ )_   _|  ___|
        |  _| | |_) | |_) |   | |/ _ \  |  _ \ | | | |_
        | |___|  _ <|  __/    | | (_) | | |_) || | |  _|
        |_____|_| \_\_|       |_|\___/  |____/ |_| |_|
        ERP To BTF
        """

        job._cr.commit()
        if not isinstance(rec['keyword'], str):
            keyword = rec['keyword']
        else:
            keyword = ast.literal_eval(rec['keyword'])
        matrix_obj = self.get_dp_np_db_matrix('np', rec['sync_model'])
        keyword = self.change_keyword(matrix_obj, keyword)

        dp_model = matrix_obj.dp_model
        if dp_model == '':
            dp_model = rec['sync_model']
        btf_data_sync_id = rec['id']
        obj = self.env[dp_model]
        data = json.loads(rec['data'])
        try:
            _logger.info('------------------------------' + str(obj) + ' write start ---------------------------------')
            existing_obj = self.env[dp_model].search(keyword)
            if data.has_key('is_sync_to_btf'):
                if data['is_sync_to_btf'] is False:
                    raise DeleteSyncRecordException
            if data.has_key('cr_number'):
                data['crNum'] = data['cr_number']
                del data['cr_number']
            if existing_obj.exists():
                field_type = self.erp_query(job, rec['sync_model'], 'fields_get', [],
                                            {'attributes': ['string', 'relation', 'type', 'required']})
                data_to_create, field_type, job, rec = self.update_np_m2o_fields_to_dp_m2o_ids(matrix_obj, data,
                                                                                               field_type, dp_model,
                                                                                               job, rec)
                existing_obj.with_context({'from_erp': True}).write(data_to_create)
                existing_obj._cr.commit()
            else:
                raise CreateSyncRecordException
            _logger.info('------------------------------' + str(obj) + ' write end -----------------------------------')
            self.erp_query(job, 'btf.data.sync', 'write', [[btf_data_sync_id],  {'state': "done"}])
            _logger.info('-------------- ERP btf.data.sync ' + str(btf_data_sync_id) + ' write successful ------------------')

        except DeleteSyncRecordException:
            _logger.info('****************************** DeleteSyncRecordException ***********************************')
            self.erp_action_sync_unlink(job, rec)

        except CreateSyncRecordException:
            _logger.info('****************************** CreateSyncRecordException *************************************')
            # data_to_create = self.erp_query(job,
            #                                rec['sync_model'],
            #                                'read',
            #                                [rec['sync_model_id']])
            # field_type = self.erp_query(job,
            #                            rec['sync_model'],
            #                            'fields_get',
            #                            [], {'attributes': ['string', 'help', 'type']})
            # data_to_create, field_type, job, rec = self.check_np_many2one_fields(data_to_create, field_type, dp_model, job, rec)
            new_job = self.create({'state': 'sync_data_to_btf'})
            self._get_credentials_(new_job)
            self.erp_connect(new_job)
            rel_obj = new_job.create_relation_lines(
                {'dp_np_api_id': new_job.id, 'state': 'sync_data_to_btf', 'action_type': rec['sync_action'],
                 'erp_record'  : json.dumps(rec)})
            new_job.api_rel_id = rel_obj.id
            self.erp_query(job, 'btf.data.sync', 'write', [[btf_data_sync_id], {'state': "is_creating_in_btf"}])
            # dont need to write done as erp_action_sync_create will write done from there
            self._cr.commit()
            self.with_context({'erp_action_sync_write': True}).erp_action_sync_create(new_job, rec)

        except AssertionError as ae:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.dp_np_api_line.exists():
                if job.dp_np_api_line.error_log is False:
                    job.dp_np_api_line.error_log = ''
                job.dp_np_api_line.error_count += 1
                if job.dp_np_api_line.error_count % 20 == 0:
                    job.dp_np_api_line.error_log = job.dp_np_api_line.error_log[:len(job.dp_np_api_line.error_log)/2]
                job.dp_np_api_line.error_log = str(job.dp_np_api_line.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=ae) + '\n\n' + job.dp_np_api_line.error_log
            _logger.error(ae)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('dp_model: ' + str(dp_model) + ' keyword: ' + str(keyword))
            _logger.error('Obj: ' + str(obj))
            _logger.error('job: ' + str(job))
            _logger.error('rec: ' + str(rec))
            _logger.error('THIS IS DUE TO MORE THAN 1 RECORDS FOUND IN BUYTAXFREE DATABASE')
            _logger.error('erp_action_sync_write AssertionError: -------------------------------------------------------------------------')

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.dp_np_api_line.exists():
                if job.dp_np_api_line.error_log is False:
                    job.dp_np_api_line.error_log = ''
                job.dp_np_api_line.error_count += 1
                if job.dp_np_api_line.error_count % 20 == 0:
                    job.dp_np_api_line.error_log = job.dp_np_api_line.error_log[:len(job.dp_np_api_line.error_log)/2]
                job.dp_np_api_line.error_log = str(job.dp_np_api_line.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=e) + '\n\n' + job.dp_np_api_line.error_log
            _logger.error(e)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('btf_data_sync_id' + str(btf_data_sync_id) + ' dp_model: ' + str(dp_model) + ' keyword: ' + str(keyword))
            _logger.error('job: ' + str(job))
            _logger.error('rec: ' + str(rec))
            _logger.error('erp_action_sync_write Exception: -------------------------------------------------------------------------')

    @api.model
    def erp_action_sync_create(self, job, rec):
        """
         _____ ____  ____    _____       ____ _____ _____
        | ____|  _ \|  _ \  |_   _|__   | __ )_   _|  ___|
        |  _| | |_) | |_) |   | |/ _ \  |  _ \ | | | |_
        | |___|  _ <|  __/    | | (_) | | |_) || | |  _|
        |_____|_| \_\_|       |_|\___/  |____/ |_| |_|
        ERP To BTF
        """
        job._cr.commit()
        if not isinstance(rec['keyword'], str):
            keyword = rec['keyword']
        else:
            keyword = ast.literal_eval(rec['keyword'])
        matrix_obj = self.get_dp_np_db_matrix('np', rec['sync_model'])

        dp_model, add_field = matrix_obj.dp_model, matrix_obj.has_additional_fields
        if dp_model == '':
            dp_model = rec['sync_model']
        btf_data_sync_id = rec['id']
        obj = self.env[dp_model]
        if self._context.get("erp_action_sync_write", False):
            data = self.erp_query(job, rec.get('sync_model', False), 'search_read', [[['id', '=', rec.get('sync_model_id', False)]]], {'fields': []})
            if len(data) == 0 or len(data) > 1:
                data = json.loads(rec['data'])
            else:
                data = data[0]
        else:
            data = json.loads(rec['data'])
        try:
            # try to search if record is already created, if it is then erp_query has failed the previous time it run
            is_create = True
            if self.search_existing_model(dp_model, data):
                is_create = False
            if add_field:
                data.update({'source_origin': 'np', 'is_to_np': False, 'is_from_np': True,
                             'sync_status': False, 'erp_id': rec['sync_model_id']})
            if data.get('is_sync_to_btf'):
                del data['is_sync_to_btf']

            # data_to_create = self.erp_query(job, rec['sync_model'], 'read', [rec['sync_model_id']])
            """
            ----------------------------------------------- data_to_create ---------------------------------------------
            {'crew': '22333333',
             'flag': 'SG',
             'image': 'iVBORw0KGgoAAAANSUhEUgAABAAAAAQACAMAAABIw9uxAAADAFBMVEUAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAACzMPSIAAABAHRSTlMA/dCPL0+ucAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n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\n',
             'imo_number': '1111111111111111',
             'name': 'lololololololololol',
             'nrt': '22222222222222222',
             'shipping_agent': [2126, '3R BONDED WAREHOUSE PTE. LTD.'],
             'type': [24, 'NAVAL VESSEL'],
             'via': False,
             'via_desc': False,
             'via_group': False}
            ----------------------------------------------- data_to_create ---------------------------------------------
            
            ----------------------------------------------- data -------------------------------------------------------
            {u'crew': u'22333333',
             u'flag': u'SG',
             u'image': u'iVBORw0KGgoAAAANSUhEUgAABAAAAAQACAMAAABIw9uxAAADAFBMVEUAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAACzMPSIAAABAHRSTlMA/dCPL0+ucAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n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\n',
             u'imo_number': u'1111111111111111',
             u'is_sync_to_btf': True,
             u'name': u'lololololololololol',
             u'note': False,
             u'nrt': u'22222222222222222',
             u'shipping_agent': 2126,
             u'type': 24,
             u'via': False,
             u'via_desc': False,
             u'via_group': False}
            ----------------------------------------------- data -------------------------------------------------------
            """
            field_type = self.erp_query(job, rec['sync_model'], 'fields_get', [], {'attributes': ['string', 'relation', 'type', 'required']})
            if data.has_key('cr_number'):
                data['crNum'] = data['cr_number']
                del data['cr_number']
            data_to_create, field_type, job, rec = self.update_np_m2o_fields_to_dp_m2o_ids(matrix_obj, data, field_type, dp_model, job, rec)
            categ_exists = False
            if is_create:
                if dp_model == 'product.template':
                    data_to_create['website_published'] = False
                if dp_model == 'product.category':
                    categ_name = data_to_create.get('name', False)
                    if categ_name is not False:
                        if self.env['product.category'].search([('name', '=', categ_name)]):
                            categ_exists = True
                        if not self.env['product.category'].search([('name', '=', categ_name)]):
                            pub_categ_obj = self.env['product.public.category'].create({'name': categ_name, 'hidden_to_public': True})
                            data_to_create.update({'public_categ_id': pub_categ_obj.id})
                if data_to_create.has_key('message_follower_ids'):
                    del data_to_create['message_follower_ids']
                _logger.info('------------------------------' + str(obj) + ' create start ---------------------------------')
                # TODO: need to convert all foreign keys into their respective id in btf db
                is_created_locally = False
                if not categ_exists:
                    obj = self.env[dp_model].with_context({'from_erp': True}).create(data_to_create)
                    self._cr.commit()
                    is_created_locally = True
                    _logger.info('------------------------------' + str(
                        obj) + ' create end -----------------------------------')

                if is_created_locally:
                    self.erp_query(job, 'btf.data.sync', 'write', [[btf_data_sync_id],  {'state': "done"}])
                obj.sync_status = True  # turn true only if erp query and self.env.create is successful
                _logger.info('-------------- ERP btf.data.sync ' + str(btf_data_sync_id) + ' write successful ------------------')
            else:
                _logger.error('------------------------------' + str(obj) + ' is_create is False start ---------------------------------------')
                local_obj = self.env[dp_model].search(self.get_search_context_matrix(dp_model, data))
                reason = ' is_create is False, Please Debug at BuyTaxFree'
                if local_obj.exists():
                    reason = " {} already exists in BuyTaxFree with the id {}".format(data.get('name', ''), local_obj.ids)
                cancel_reason = "Cancelled due to {}".format(reason)
                self.erp_query(job, 'btf.data.sync', 'write', [[btf_data_sync_id], {'state': "is_already_in_BTF", 'reason': cancel_reason}])
                _logger.error('------------------------------' + str(obj) + ' is_create is False end -----------------------------------------')
        except AssertionError as ae:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.dp_np_api_line.exists():
                if job.dp_np_api_line.error_log is False:
                    job.dp_np_api_line.error_log = ''
                job.dp_np_api_line.error_count += 1
                if job.dp_np_api_line.error_count % 20 == 0:
                    job.dp_np_api_line.error_log = job.dp_np_api_line.error_log[:len(job.dp_np_api_line.error_log)/2]
                job.dp_np_api_line.error_log = str(job.dp_np_api_line.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=ae) + '\n\n' + job.dp_np_api_line.error_log
            _logger.error(ae)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('dp_model: ' + str(dp_model) + ' keyword: ' + str(keyword))
            _logger.error('Obj: ' + str(obj))
            _logger.error('job: ' + str(job))
            _logger.error('rec: ' + str(rec))
            _logger.error('THIS IS DUE TO MORE THAN 1 RECORDS FOUND IN BUYTAXFREE DATABASE')
            _logger.error('erp_action_sync_create AssertionError: -------------------------------------------------------------------------')
        except IntegrityError as iie:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error(iie)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('btf_data_sync_id: ' + str(btf_data_sync_id) + ' dp_model: ' + str(dp_model) + ' keyword: ' + str(keyword))
            _logger.error('job: ' + str(job))
            _logger.error('rec: ' + str(rec))
            _logger.error('erp_action_sync_create IntegrityError: -------------------------------------------------------------------------')
            self.erp_query(job, 'btf.data.sync', 'write', [[btf_data_sync_id], {'state': "is_already_in_BTF", 'reason': str(exc_obj)}])
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.dp_np_api_line.exists():
                if job.dp_np_api_line.error_log is False:
                    job.dp_np_api_line.error_log = ''
                job.dp_np_api_line.error_count += 1
                if job.dp_np_api_line.error_count % 20 == 0:
                    job.dp_np_api_line.error_log = job.dp_np_api_line.error_log[:len(job.dp_np_api_line.error_log)/2]
                job.dp_np_api_line.error_log = str(job.dp_np_api_line.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=e) + '\n\n' + job.dp_np_api_line.error_log
            _logger.error(e)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('btf_data_sync_id: ' + str(btf_data_sync_id) + ' dp_model: ' + str(dp_model) + ' keyword: ' + str(keyword))
            _logger.error('job: ' + str(job))
            _logger.error('rec: ' + str(rec))
            _logger.error('erp_action_sync_create Exception: -------------------------------------------------------------------------')

    @api.model
    def erp_action_sync_unlink(self, job, rec):
        """
         _____ ____  ____    _____       ____ _____ _____
        | ____|  _ \|  _ \  |_   _|__   | __ )_   _|  ___|
        |  _| | |_) | |_) |   | |/ _ \  |  _ \ | | | |_
        | |___|  _ <|  __/    | | (_) | | |_) || | |  _|
        |_____|_| \_\_|       |_|\___/  |____/ |_| |_|
        ERP To BTF
        """
        job._cr.commit()
        if not isinstance(rec['keyword'], str):
            keyword = rec['keyword']
        else:
            keyword = ast.literal_eval(rec['keyword'])
        matrix_obj = self.get_dp_np_db_matrix('np', rec['sync_model'])
        keyword = self.change_keyword(matrix_obj, keyword)
        dp_model = matrix_obj.dp_model
        if dp_model == '':
            dp_model = rec['sync_model']
        btf_data_sync_id = rec['id']
        obj = self.env[dp_model]
        try:
            obj = self.env[dp_model].search(keyword)
            if len(obj) == 0:
                raise NoRecordsFoundException
            if len(obj) > 1:
                raise AssertionError
            _logger.info('------------------------------' + str(obj) + ' unlink start ---------------------------------')
            obj.with_context({'from_erp': True}).unlink()
            obj._cr.commit()
            _logger.info('------------------------------' + str(obj) + ' unlink end -----------------------------------')
            self.erp_query(job, 'btf.data.sync', 'write', [[btf_data_sync_id],  {'state': "done"}])
            _logger.info('-------------- ERP btf.data.sync ' + str(btf_data_sync_id) + ' write successful ------------------')
        except NoRecordsFoundException as nre:
            self.erp_query(job, 'btf.data.sync', 'write', [[btf_data_sync_id], {'state': "cancel"}])
            _logger.info('-------------- ERP btf.data.sync ' + str(btf_data_sync_id) + ' cancel successful ------------------')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.dp_np_api_line.exists():
                if job.dp_np_api_line.error_log is False:
                    job.dp_np_api_line.error_log = ''
                job.dp_np_api_line.error_count += 1
                if job.dp_np_api_line.error_count % 20 == 0:
                    job.dp_np_api_line.error_log = job.dp_np_api_line.error_log[:len(job.dp_np_api_line.error_log)/2]
                job.dp_np_api_line.error_log = str(job.dp_np_api_line.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=nre) + '\n\n' + job.dp_np_api_line.error_log
            _logger.error(nre)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('dp_model: ' + str(dp_model) + ' keyword: ' + str(keyword))
            _logger.error('Obj: ' + str(obj))
            _logger.error('job: ' + str(job))
            _logger.error('rec: ' + str(rec))
            _logger.error('THIS IS DUE TO RECORD NOT FOUND IN BUYTAXFREE DATABASE')
            _logger.error('erp_action_sync_unlink NoRecordsFoundException: -------------------------------------------------------------------------')
        except AssertionError as ae:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.dp_np_api_line.exists():
                if job.dp_np_api_line.error_log is False:
                    job.dp_np_api_line.error_log = ''
                job.dp_np_api_line.error_count += 1
                if job.dp_np_api_line.error_count % 20 == 0:
                    job.dp_np_api_line.error_log = job.dp_np_api_line.error_log[:len(job.dp_np_api_line.error_log)/2]
                job.dp_np_api_line.error_log = str(job.dp_np_api_line.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=ae) + '\n\n' + job.dp_np_api_line.error_log
            _logger.error(ae)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('dp_model: ' + str(dp_model) + ' keyword: ' + str(keyword))
            _logger.error('Obj: ' + str(obj))
            _logger.error('job: ' + str(job))
            _logger.error('rec: ' + str(rec))
            _logger.error('THIS IS DUE TO MORE THAN 1 RECORDS FOUND IN BUYTAXFREE DATABASE')
            _logger.error('erp_action_sync_unlink AssertionError: -------------------------------------------------------------------------')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.dp_np_api_line.exists():
                if job.dp_np_api_line.error_log is False:
                    job.dp_np_api_line.error_log = ''
                job.dp_np_api_line.error_count += 1
                if job.dp_np_api_line.error_count % 20 == 0:
                    job.dp_np_api_line.error_log = job.dp_np_api_line.error_log[:len(job.dp_np_api_line.error_log)/2]
                job.dp_np_api_line.error_log = str(job.dp_np_api_line.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=e) + '\n\n' + job.dp_np_api_line.error_log
            _logger.error(e)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('btf_data_sync_id' + str(btf_data_sync_id) + ' dp_model: ' + str(dp_model) + ' keyword: ' + str(keyword))
            _logger.error('job: ' + str(job))
            _logger.error('rec: ' + str(rec))
            _logger.error('erp_action_sync_unlink Exception: -------------------------------------------------------------------------')

    @api.model
    def get_dp_np_db_matrix(self, source, model):
        """

        :param source:
        :param model:
        @return ret: corresponding model name
        @return add_fields: Boolean. additional fields
        """
        obj = self.env['dp.np.db.matrix']
        if source == 'np':
            model_search = 'np_model'
        else:
            model_search = 'dp_model'
        obj = obj.search([(model_search, '=', model)])
        return obj

    @api.model
    def get_search_context_matrix(self, model, data):
        search_name = data.get('name', '')
        if data.get('name', False) is not False:
            search_name = data.get('name', '').upper()
        db_matrix_obj = self.env['dp.np.db.matrix'].search([('dp_model', '=', model)])
        model_search_matrix = {
            'product.category': [('name', '=', search_name)],
            'product.template': [('name', '=', search_name)],
            'vessel.name'     : [('name', '=', search_name)],
            'vessel.type'     : [('name', '=', search_name), ('code', '=', data.get('code', ''))],
            'shipping.agent'  : [('name', '=', search_name)],
        }
        if db_matrix_obj.exists():
            field_lines = db_matrix_obj.field_line_ids
            if field_lines.exists():
                model_search_matrix = {
                    'product.category': self._get_search_args(field_lines, data),
                    'product.template': self._get_search_args(field_lines, data),
                    'vessel.name'     : self._get_search_args(field_lines, data),
                    'vessel.type'     : [('name', '=', search_name), ('code', '=', data.get('code', ''))],
                    'shipping.agent'  : self._get_search_args(field_lines, data),
                }
        return model_search_matrix.get(model, [])

    @api.model
    def _get_search_args(self, fields, data):
        """
        This part need to enhance. Currently I ignore many2one fields as need to query ERP db for the
        record. After query, need to check if exist in DP db, if exist, use that id instead, if not found,
        need to create that record. Then if many2one field is found again, need to do the whole process
        again.

        """
        return [(field.dp_field, '=', data.get(field.np_field, False)) for field in fields if field.is_many2one is False]


    @api.model
    def search_existing_model(self, model, data):
        ret = False
        existing_obj = self.env[model].search(self.get_search_context_matrix(model, data))
        if existing_obj.exists():
            ret = True
        return ret

    @api.model
    def change_keyword(self, matrix_obj, keyword):
        try:
            if matrix_obj.auto_capitalize_in_dp and isinstance(keyword, list):
                for tup_idx in range(len(keyword)):
                    if keyword[tup_idx][0] == 'name':
                        keyword[tup_idx] = (keyword[tup_idx][0], keyword[tup_idx][1], keyword[tup_idx][2].upper())
        except IndexError as ie:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error(ie)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('matrix_obj' + str(matrix_obj) + ' keyword: ' + str(keyword))
            _logger.error('change_keyword Exception: -------------------------------------------------------------------------')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error(e)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('matrix_obj' + str(matrix_obj) + ' keyword: ' + str(keyword))
            _logger.error('change_keyword Exception: -------------------------------------------------------------------------')
        return keyword

    @api.model
    def update_np_m2o_fields_to_dp_m2o_ids(self, matrix_obj, data_to_create, field_type, dp_model, job, rec):
        """
        ---------------------------------------------- data_to_create ----------------------------------------------
        {'__last_update': '2019-11-01 02:44:01',
         'code': 'sb',
         'create_date': '2019-11-01 02:43:54',
         'create_uid': [1, 'ELEPHAS SUPPORT'],
         'display_name': 'stealth bomber',
         'id': 188,
         'is_sync_to_btf': True,
         'name': 'stealth bomber',
         'write_date': '2019-11-01 02:44:01',
         'write_uid': [1, 'ELEPHAS SUPPORT']}
        ---------------------------------------------- data_to_create ----------------------------------------------

        ---------------------------------------------- field_type ----------------------------------------------
        {'__last_update': {'string': 'Last Modified on', 'type': 'datetime'},
         'code': {'string': 'Code', 'type': 'char'},
         'create_date': {'string': 'Created on', 'type': 'datetime'},
         'create_uid': {'string': 'Created by', 'type': 'many2one'},
         'display_name': {'string': 'Display Name', 'type': 'char'},
         'id': {'string': 'ID', 'type': 'integer'},
         'is_sync_to_btf': {'string': 'Show in BuyTaxFree', 'type': 'boolean'},
         'name': {'string': 'Name', 'type': 'char'},
         'write_date': {'string': 'Last Updated on', 'type': 'datetime'},
         'write_uid': {'string': 'Last Updated by', 'type': 'many2one'}}
        ---------------------------------------------- field_type ----------------------------------------------

        ---------------------------------------------- rec ----------------------------------------------
        {'create_date': '2019-11-01 02:44:01',
         'data': '{"is_sync_to_btf": true}',
         'id': 47,
         'keyword': "[('name', '=', u'stealth bomber')]",
         'priority': 12,
         'sync_action': 'write',
         'sync_model': 'np.vessel.type',
         'sync_model_id': 188}
        ---------------------------------------------- rec ----------------------------------------------

        """
        exclude_many2one_columns = ('create_uid','write_uid')
        has_many2one = any(k2=='type' and v2 == 'many2one' and k1 not in exclude_many2one_columns for k1,v1 in field_type.iteritems() for k2, v2 in v1.iteritems())
        has_one2many = any(k2=='type' and v2 == 'one2many' and k1 not in exclude_many2one_columns for k1,v1 in field_type.iteritems() for k2, v2 in v1.iteritems())
        has_no_many = True
        if has_many2one or has_one2many:
            has_no_many = False
        if has_many2one:
            data_to_create = self.get_np_many2one_fkey_value(exclude_many2one_columns, field_type, data_to_create, matrix_obj, job)
        if has_one2many:
            data_to_create = self.dumb_way_force_delete_one2many_fields(field_type, data_to_create)
        if has_no_many:
            pass
        data_to_create = self.check_dp_model_columns(data_to_create, dp_model)
        return data_to_create, field_type, job, rec

    @api.model
    def get_np_many2one_fkey_value(self, exclude_many2one_columns, field_type, data_to_create, matrix_obj, job):
        """
        ------------------------------------------------- field_type ---------------------------------------------------
        {'__last_update': {'string': 'Last Modified on', 'type': 'datetime'},
         'create_date': {'string': 'Created on', 'type': 'datetime'},
         'create_uid': {'relation': 'res.users',
                        'string': 'Created by',
                        'type': 'many2one'},
         'crew': {'string': 'Crew No', 'type': 'char'},
         'display_name': {'string': 'Display Name', 'type': 'char'},
         'flag': {'string': 'Flag', 'type': 'char'},
         'id': {'string': 'ID', 'type': 'integer'},
         'image': {'string': 'Image', 'type': 'binary'},
         'image_medium': {'string': 'Medium-sized image', 'type': 'binary'},
         'image_small': {'string': 'Small-sized image', 'type': 'binary'},
         'imo_number': {'string': 'IMO Number', 'type': 'char'},
         'is_sync_to_btf': {'string': 'Show in BuyTaxFree', 'type': 'boolean'},
         'name': {'string': 'Name', 'type': 'char'},
         'note': {'string': 'Notes', 'type': 'text'},
         'nrt': {'string': 'NRT', 'type': 'char'},
         'shipping_agent': {'relation': 'ship.agent',
                            'string': 'Shipping Agent',
                            'type': 'many2one'},
         'type': {'relation': 'np.vessel.type',
                 'string': 'Type',
                 'type': 'many2one'},
         'via': {'string': 'Ship Via', 'type': 'char'},
         'via_desc': {'string': 'Ship Via Desc.', 'type': 'char'},
         'via_group': {'string': 'Ship Via Grp CD', 'type': 'char'},
         'write_date': {'string': 'Last Updated on', 'type': 'datetime'},
         'write_uid': {'relation': 'res.users',
                       'string': 'Last Updated by',
                       'type': 'many2one'}}
        ------------------------------------------------- field_type ---------------------------------------------------

        ------------------------------------------------- data_to_create -----------------------------------------------
        {u'crew': u'22333333',
         'erp_id': 33304,
         u'flag': u'SG',
         u'image': u'iVBORw0KGgoAAAANSUhEUgAABAAAAAQACAMAAABIw9uxAAADAFBMVEUAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAACzMPSIAAABAHRSTlMA/dCPL0+ucAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n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\n',
         u'imo_number': u'1111111111111111',
         'is_from_np': True,
         'is_to_np': False,
         u'name': u'lololololololololol',
         u'note': False,
         u'nrt': u'22222222222222222',
         u'shipping_agent': 2126,
         'source_origin': 'np',
         'sync_status': False,
         u'type': 24,
         u'via': False,
         u'via_desc': False,
         u'via_group': False}
        ------------------------------------------------- data_to_create -----------------------------------------------
        """
        m2o = self.get_np_many2one_field_model(exclude_many2one_columns, field_type)
        for field, np_related_model in m2o:
            # for k1, v1 in field_type.iteritems():
            #     for k2, v2 in v1.iteritems():
            #         if k2 == 'type' and v2 == 'many2one' and k1 not in exclude_many2one_columns and k1 in data_to_create:
            #             field, np_related_model = k1, v1.get('relation', '')
            try:
                np_model_id = data_to_create[field]
                if isinstance(np_model_id, list):
                    if isinstance(np_model_id[0], int):
                        np_model_id = np_model_id[0]
                # dp_fields = [k for k,_ in self.env[matrix_obj.dp_model]._fields.iteritems()]
                # if field not in dp_fields:
                #     raise FieldsNotFoundInBuyTaxFreeException
                if self.get_ignore_m2o_property_field_in_model_in_btf(np_related_model):
                    # new_matrix_obj = self.get_dp_np_db_matrix('np', np_related_model)
                    # if new_matrix_obj.exists():
                    #     if np_related_model in ('account.account', 'account.journal'):
                            # data_to_create = self.dumb_way_to_handle_account_account(field, np_related_model, data_to_create, new_matrix_obj, matrix_obj)
                    del data_to_create[field]
                    continue
                        # else:
                        #     raise ModelIsNotAccountAccountException
                    # else:
                    #     raise BuyTaxFreeandNewPortERPDatabaseMatrixDoNotExistException
                if self.dumb_way_to_handle_product_template_product_category_bool(np_related_model, field):
                    data_to_create =  self.dumb_way_to_handle_product_template_product_category(data_to_create, field, np_related_model, field_type, matrix_obj, job)
                if self.dumb_way_force_ignore_fields(np_related_model, field):
                    continue

                erp_records = self.erp_query(job, np_related_model, 'search_read', [[['id', '=', np_model_id]]], {'fields': []})
                erp_dict = {}
                if matrix_obj.exists():
                    if self.check_dp_model_exists(matrix_obj.dp_model):
                        if self.env[matrix_obj.dp_model]._fields.has_key(field):
                            if self.env[matrix_obj.dp_model]._fields[field].required is False:
                                raise IgnoreFieldsIfNotRequiredInBuyTaxFreeException
                    else:
                        raise ModelDoNotExistInBuyTaxFreeException
                if not self.check_model_exist_in_buytaxfee(np_related_model):
                    del data_to_create[field]
                    continue

                if len(erp_records) == 0:
                    raise NoRecordsFoundException
                if len(erp_records) > 1:
                    raise AssertionError
                erp_dict = erp_records[0]
                search_criteria = []
                if erp_dict.has_key('name'):
                    search_criteria.append(('name', '=', erp_dict.get('name')))
                if erp_dict.has_key('code'):
                    search_criteria.append(('code', '=', erp_dict.get('code')))
                matrix_obj = self.get_dp_np_db_matrix('np', np_related_model)
                if matrix_obj.exists():
                    dp_obj = self.env[matrix_obj.dp_model].search(search_criteria)
                    if dp_obj.exists():
                        data_to_create[field] = dp_obj.id
                    else:
                        raise DPRecordsNotFoundException
                else:
                    if not self.check_dp_model_exists(matrix_obj.dp_model):
                        raise KeyError
                    else:
                        raise AssertionError
            except ModelIsNotAccountAccountException as minaae:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.info(minaae)
                _logger.info('Exception Type: ' + str(exc_type))
                _logger.info('Exception Error Description: ' + str(exc_obj))
                _logger.info('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.info('np_related_model: ' + str(np_related_model))
                _logger.info('THIS IS DUE TO THE DATABASE MATRIX IS NT ACCOUNT.ACCOUNT')
                _logger.info('get_np_many2one_fkey_value ModelIsNotAccountAccountException: -------------------------------------------------------------------------')
                continue
            except BuyTaxFreeandNewPortERPDatabaseMatrixDoNotExistException as btfanperpdbmdnee:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.info(btfanperpdbmdnee)
                _logger.info('Exception Type: ' + str(exc_type))
                _logger.info('Exception Error Description: ' + str(exc_obj))
                _logger.info('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.info('np_related_model: ' + str(np_related_model))
                _logger.info('THIS IS DUE TO THE DATABASE MATRIX OF NEWPORT ERP AND BUYTAXFREE DOES NOT EXIST')
                _logger.info('get_np_many2one_fkey_value BuyTaxFreeandNewPortERPDatabaseMatrixDoNotExistException: -------------------------------------------------------------------------')
                continue
            except ModelDoNotExistInBuyTaxFreeException as mdneibtfe:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.info(mdneibtfe)
                _logger.info('Exception Type: ' + str(exc_type))
                _logger.info('Exception Error Description: ' + str(exc_obj))
                _logger.info('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(
                    exc_tb.tb_lineno))
                _logger.info('field: ' + str(field) + ' np_related_model: ' + str(np_related_model))
                _logger.info('THIS IS DUE TO ERP MANY2ONE FIELD IS NOT REQUIRED IN BUYTAXFREE DATABASE')
                _logger.info('NO ACTION REQUIRED FROM THIS EXCEPTION')
                _logger.info(
                    'get_np_many2one_fkey_value IgnoreFieldsIfNotRequiredInBuyTaxFreeException: -------------------------------------------------------------------------')
                continue
            except DPRecordsNotFoundException as dprnfe:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('np_model_id: ' + str(np_model_id) + ' np_related_model: ' + str(np_related_model))
                _logger.error('THIS IS DUE TO ERP MANY2ONE RECORD NOT FOUND IN BUYTAXFREE DATABASE')
                if not self.get_ignore_m2o_property_field_in_model_in_btf(np_related_model):
                    _logger.info('get_np_many2one_fkey_value Creating in BuyTaxree Database: START -------------------------------------------------------------------------')
                    erp_dict = {k:v for k,v in erp_dict.iteritems() if k not in exclude_many2one_columns}
                    dp_obj = self.env[matrix_obj.dp_model].create(erp_dict)
                    self._cr.commit()
                    data_to_create[field] = dp_obj.id
                    _logger.error('BUYTAXFREE DATABASE ' + matrix_obj.dp_model + ' ' + str(erp_dict) + ' created')
                    _logger.info('get_np_many2one_fkey_value Creating in BuyTaxree Database: SUCCESS-------------------------------------------------------------------------')
                _logger.error('get_np_many2one_fkey_value DPRecordsNotFoundException: -------------------------------------------------------------------------')
                continue
            except IgnoreFieldsIfNotRequiredInBuyTaxFreeException as ifinribtfe:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.info(ifinribtfe)
                _logger.info('Exception Type: ' + str(exc_type))
                _logger.info('Exception Error Description: ' + str(exc_obj))
                _logger.info('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.info('field: ' + str(field) + ' np_related_model: ' + str(np_related_model))
                _logger.info('THIS IS DUE TO ERP MANY2ONE FIELD IS NOT REQUIRED IN BUYTAXFREE DATABASE')
                _logger.info('NO ACTION REQUIRED FROM THIS EXCEPTION')
                _logger.info('get_np_many2one_fkey_value IgnoreFieldsIfNotRequiredInBuyTaxFreeException: -------------------------------------------------------------------------')
                del data_to_create[field]
                continue
            except FieldsNotFoundInBuyTaxFreeException as fnfibtfe:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.info(fnfibtfe)
                _logger.info('Exception Type: ' + str(exc_type))
                _logger.info('Exception Error Description: ' + str(exc_obj))
                _logger.info('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.info('field: ' + str(field) + ' np_related_model: ' + str(np_related_model))
                _logger.info('THIS IS DUE TO ERP MANY2ONE FIELD DOES NOT EXIST IN BUYTAXFREE DATABASE')
                _logger.info('NO ACTION REQUIRED FROM THIS EXCEPTION')
                _logger.info('get_np_many2one_fkey_value FieldsNotFoundInBuyTaxFreeException: -------------------------------------------------------------------------')
                continue
            except NoRecordsFoundException as nre:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                if job.api_rel_id.exists():
                    if job.api_rel_id.error_log is False:
                        job.api_rel_id.error_log = ''
                    job.api_rel_id.error_count += 1
                    if job.api_rel_id.error_count % 20 == 0:
                        job.api_rel_id.error_log = job.api_rel_id.error_log[
                                                       :len(job.api_rel_id.error_log) / 2]
                    job.api_rel_id.error_log = str(job.api_rel_id.error_count) + '\t' + \
                                                   (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                                   '\t' + '{e}'.format(e=nre) + '\n\n' + job.api_rel_id.error_log
                _logger.error(nre)
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('np_model_id: ' + str(np_model_id) + ' np_related_model: ' + str(np_related_model))
                _logger.error('THIS IS DUE TO RECORD NOT FOUND IN ERP DATABASE')
                _logger.error('get_np_many2one_fkey_value NoRecordsFoundException: -------------------------------------------------------------------------')
                continue
            except KeyError as ke:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception: ' + str(ke))
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('field: '+ field + ' np_related_model: ' + np_related_model)
                _logger.error('get_np_many2one_fkey_value KeyError: -------------------------------------------------------------------------')
                continue
            except AssertionError as ae:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception: ' + str(ae))
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('field: '+ field + ' np_related_model: ' + np_related_model)
                _logger.error('get_np_many2one_fkey_value AssertionError: -------------------------------------------------------------------------')
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception: ' + str(e))
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('field: '+ field + ' np_related_model: ' + np_related_model)
                _logger.error('get_np_many2one_fkey_value Exception: -------------------------------------------------------------------------')
                continue
        return data_to_create

    @api.model
    def dumb_way_force_delete_one2many_fields(self, field_type, data_to_create):
        o2m = self.get_np_one2many_field_model(field_type)
        for key in o2m:
            if data_to_create.has_key(key):
                del data_to_create[key]
        return data_to_create

    @api.model
    def get_np_one2many_field_model(self, field_type):
        for k1, v1 in field_type.iteritems():
            for k2, v2 in v1.iteritems():
                if k2 == 'type' and v2 == 'one2many':
                    yield k1

    @api.model
    def check_dp_model_exists(self, dp_model):
        model_obj = self.env['ir.model'].search([('model', '=', dp_model)])
        if model_obj.exists():
            return True
        return False

    @api.model
    def get_np_many2one_field_model(self, exclude_many2one_columns, field_type):
        for k1, v1 in field_type.iteritems():
            for k2, v2 in v1.iteritems():
                if k2 == 'type' and v2 == 'many2one' and k1 not in exclude_many2one_columns:
                    yield (k1, v1.get('relation', ''))

    @api.model
    def check_dp_model_columns(self, data_to_create, dp_model):
        exclude_columns = ('id', 'create_uid', 'write_uid', 'create_date', 'write_date')
        dp_columns = self.env[dp_model]._columns.keys()
        matrix_obj = self.get_dp_np_db_matrix('btf', dp_model)
        data_to_create = self.convert_dp_field_to_np_field('erp_to_btf', matrix_obj, data_to_create)
        data_to_create = {k: v for k, v in data_to_create.iteritems() if k in dp_columns and k not in exclude_columns}
        return data_to_create

    @api.model
    def get_ignore_m2o_property_field_in_model_in_btf(self, np_model):
        if np_model in ('account.account', 'account.journal'):
            return True
        return False

    @api.model
    def cron_sync_data_to_erp(self):
        job = self.env['dp.np.api']
        try:
            erp_job = self.create({'state': 'sync_data_to_erp'})
            self._get_credentials_(erp_job)
            self.erp_connect(erp_job)
            sorted_erp_records = self.env['erp.data.sync'].search([('state', '=', 'pending')], order='priority, create_date')
            for rec in sorted_erp_records:
                job = self.create({'state': 'sync_data_to_erp'})
                self._get_credentials_(job)
                self.erp_connect(job)
                if rec.sync_action == 'write':
                    self.btf_action_sync_write(job, rec)
                elif rec.sync_action == 'create':
                    self.btf_action_sync_create(job, rec)
                elif rec.sync_action == 'unlink':
                    self.btf_action_sync_unlink(job, rec)
                else:
                    raise Exception
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.dp_np_api_line.exists():
                if job.dp_np_api_line.error_log is False:
                    job.dp_np_api_line.error_log = ''
                job.dp_np_api_line.error_count += 1
                if job.dp_np_api_line.error_count % 20 == 0:
                    job.dp_np_api_line.error_log = job.dp_np_api_line.error_log[:len(job.dp_np_api_line.error_log)/2]
                job.dp_np_api_line.error_log = str(job.dp_np_api_line.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=e) + '\n\n' + job.dp_np_api_line.error_log
            _logger.error(e)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('cron_sync_data_to_erp: unable to access ERP database')

    @api.model
    def btf_action_sync_write(self, job, rec):
        """
        #  ____ _____ _____   _____       _____ ____  ____
        # | __ )_   _|  ___| |_   _|__   | ____|  _ \|  _ \
        # |  _ \ | | | |_      | |/ _ \  |  _| | |_) | |_) |
        # | |_) || | |  _|     | | (_) | | |___|  _ <|  __/
        # |____/ |_| |_|       |_|\___/  |_____|_| \_\_|
        # BTF to ERP
        """
        np_model = ''
        erp_records = []
        keyword = []
        data_dict = {k: rec[k] if k != 'data' else json.loads(rec[k]) for k, v in rec._fields.iteritems()}
        matrix_obj = self.get_dp_np_db_matrix('dp', rec.sync_model)
        if not isinstance(data_dict['keyword'], str):
            keyword = ast.literal_eval(data_dict['keyword'])
        else:
            keyword = data_dict['keyword']
        keyword = self.change_keyword(matrix_obj, keyword)

        np_model = matrix_obj.np_model
        if np_model == '':
            np_model = rec['sync_model']
        data = json.loads(rec['data'])
        try:
            _logger.info('------------------------------' + str(job) + ' write start ---------------------------------')
            erp_records = self.erp_query(job, np_model, 'search_read', [keyword], {'fields': ['id']})
            if len(erp_records) == 0:
                raise CreateSyncRecordException
            if len(erp_records) > 1:
                raise AssertionError
            np_id = erp_records[0]['id']
            write_state = self.erp_query(job, np_model, 'write', [[np_id], data])
            _logger.info('------------------------------' + str(job) + ' write end -----------------------------------')
            if write_state:
                # write_state is true when it successfully perform the write function above
                rel_obj = job.create_relation_lines({'dp_np_api_id': job.id, 'state': 'sync_data_to_erp',
                                                     'np_id': np_id, 'np_model': np_model, 'action_type': 'write',
                                                     'data_sync_id': rec.id,
                                                     'dp_model': rec.sync_model, 'dp_id': rec.sync_model_id})
                job.api_rel_id = rel_obj.id
                rec.state = 'done'
                """
                self.erp_query(job, matrix_obj.np_model, 'fields_get', [], {'attributes': ['string', 'help', 'type']}) 
                returns 

                {'__last_update': {'string': 'Last Modified on', 'type': 'datetime'},
                 'active': {'string': 'Active', 'type': 'boolean'},
                 'contact': {'string': 'Contact', 'type': 'char'},
                 'cr_number': {'string': 'C R - Number', 'type': 'char'},
                 'create_date': {'string': 'Created on', 'type': 'datetime'},
                 'create_uid': {'string': 'Created by', 'type': 'many2one'},
                 'display_name': {'string': 'Display Name', 'type': 'char'},
                 'id': {'string': 'ID', 'type': 'integer'},
                 'is_sync_to_btf': {'string': 'Show in BuyTaxFree', 'type': 'boolean'},
                 'name': {'string': 'Name', 'type': 'char'},
                 'write_date': {'string': 'Last Updated on', 'type': 'datetime'},
                 'write_uid': {'string': 'Last Updated by', 'type': 'many2one'}}
                """
                fields_desc = self.erp_query(job, matrix_obj.np_model, 'fields_get', [], {'attributes': ['string', 'help', 'type', 'required']})
                rel_obj.send_btf_write_email(fields_desc)
            else:
                raise WriteException
        except CreateSyncRecordException:
            _logger.info('****************************** CreateSyncRecordException *************************************')
            data_dict = {k: rec[k] if k != 'data' else json.loads(rec[k]) for k, v in rec._fields.iteritems()}
            self.btf_action_sync_create(job, rec, data_dict)

        except WriteException as we:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.api_rel_id.exists():
                if job.api_rel_id.error_log is False:
                    job.api_rel_id.error_log = ''
                job.api_rel_id.error_count += 1
                if job.api_rel_id.error_count % 20 == 0:
                    job.api_rel_id.error_log = job.api_rel_id.error_log[:len(job.api_rel_id.error_log)/2]
                job.api_rel_id.error_log = str(job.api_rel_id.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=we) + '\n\n' + job.api_rel_id.error_log
            _logger.error(we)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('dp_model: ' + str(np_model) + ' keyword: ' + str(keyword))
            _logger.error('Obj: ' + str(erp_records))
            _logger.error('THIS IS DUE TO MORE THAN 1 RECORDS FOUND IN BUYTAXFREE DATABASE')
            _logger.error('btf_action_sync_write AssertionError: -------------------------------------------------------------------------')

        except AssertionError as ae:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.api_rel_id.exists():
                if job.api_rel_id.error_log is False:
                    job.api_rel_id.error_log = ''
                job.api_rel_id.error_count += 1
                if job.api_rel_id.error_count % 20 == 0:
                    job.api_rel_id.error_log = job.api_rel_id.error_log[:len(job.api_rel_id.error_log)/2]
                job.api_rel_id.error_log = str(job.api_rel_id.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=ae) + '\n\n' + job.api_rel_id.error_log
            _logger.error(ae)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('dp_model: ' + str(np_model) + ' keyword: ' + str(keyword))
            _logger.error('Obj: ' + str(erp_records))
            _logger.error('THIS IS DUE TO MORE THAN 1 RECORDS FOUND IN BUYTAXFREE DATABASE')
            _logger.error('btf_action_sync_write AssertionError: -------------------------------------------------------------------------')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.api_rel_id.exists():
                if job.api_rel_id.error_log is False:
                    job.api_rel_id.error_log = ''
                job.api_rel_id.error_count += 1
                if job.api_rel_id.error_count % 20 == 0:
                    job.api_rel_id.error_log = job.api_rel_id.error_log[:len(job.api_rel_id.error_log)/2]
                job.api_rel_id.error_log = str(job.api_rel_id.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=e) + '\n\n' + job.api_rel_id.error_log
            _logger.error(e)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('btf_data_sync_id' + str(np_id) + ' dp_model: ' + str(np_model) + ' keyword: ' + str(keyword))
            _logger.error('btf_action_sync_write Exception: -------------------------------------------------------------------------')

    @api.model
    def btf_action_sync_create(self, job, rec, new_context={}):
        """
        #  ____ _____ _____   _____       _____ ____  ____
        # | __ )_   _|  ___| |_   _|__   | ____|  _ \|  _ \
        # |  _ \ | | | |_      | |/ _ \  |  _| | |_) | |_) |
        # | |_) || | |  _|     | | (_) | | |___|  _ <|  __/
        # |____/ |_| |_|       |_|\___/  |_____|_| \_\_|
        # BTF to ERP

        data_dict
        {'__last_update': '2019-11-04 05:49:51',
         'create_date': '2019-11-04 05:49:51',
         'create_uid': res.users(1,),
         'data': {u'active': True,
                  u'contact': u'99988888',
                  u'crNum': u'77776666',
                  u'name': u'TITANIC'},
         'display_name': u'shipping.agent_20544',
         'id': 1,
         'init_user_id': res.users(1,),
         'keyword': False,
         'name': u'shipping.agent_20544',
         'priority': 21,
         'state': u'pending',
         'sync_action': u'create',
         'sync_model': u'shipping.agent',
         'sync_model_id': 20544,
         'write_date': '2019-11-04 05:49:51',
         'write_uid': res.users(1,)}

        ----------------------------------------------------------------------------------------------------------------
        NOTE: if args contain fields not in newport erp database, it will still be able to create and return a res_id

        {u'active': True,
        u'contact': u'123123123',
        u'cr_number': u'666777888',
        'hahaha': False,
        'lololol': True,
        u'name': 'TITANIC-THE-UNSINKABLE-HAHAHAHAHAH'}

        will still be able to create the record in newport database
        ----------------------------------------------------------------------------------------------------------------
        """
        try:
            data_dict = {k: rec[k] if k != 'data' else json.loads(rec[k]) for k,v in rec._fields.iteritems()}
            matrix_obj = self.get_dp_np_db_matrix('dp', rec.sync_model)
            data = data_dict.get('data')
            if len(new_context.items()) > 0:
                data = copy.copy(new_context)
            if matrix_obj.exists():
                args = self.convert_dp_field_to_np_field('btf_to_erp', matrix_obj, data)
                args = self.update_dp_m2o_fields_to_np_m2o_id(job, rec, data_dict, matrix_obj, args)
                res_id = self.erp_query(job, matrix_obj.np_model, 'create', args=[args])
                rel_obj = job.create_relation_lines({'dp_np_api_id': job.id, 'state': 'sync_data_to_erp',
                                            'erp_record': json.dumps(args), 'action_type': 'create',
                                            'data_sync_id': rec.id,
                                            'np_id': res_id, 'np_model': matrix_obj.np_model,
                                            'dp_model': data_dict.get('sync_model', ''),
                                            'dp_id': data_dict.get('sync_model_id', 0)})
                job.api_rel_id = rel_obj.id
                rec.state = 'done'
                """
                self.erp_query(job, matrix_obj.np_model, 'fields_get', [], {'attributes': ['string', 'help', 'type']}) 
                returns 
                
                {'__last_update': {'string': 'Last Modified on', 'type': 'datetime'},
                 'active': {'string': 'Active', 'type': 'boolean'},
                 'contact': {'string': 'Contact', 'type': 'char'},
                 'cr_number': {'string': 'C R - Number', 'type': 'char'},
                 'create_date': {'string': 'Created on', 'type': 'datetime'},
                 'create_uid': {'string': 'Created by', 'type': 'many2one'},
                 'display_name': {'string': 'Display Name', 'type': 'char'},
                 'id': {'string': 'ID', 'type': 'integer'},
                 'is_sync_to_btf': {'string': 'Show in BuyTaxFree', 'type': 'boolean'},
                 'name': {'string': 'Name', 'type': 'char'},
                 'write_date': {'string': 'Last Updated on', 'type': 'datetime'},
                 'write_uid': {'string': 'Last Updated by', 'type': 'many2one'}}
                """
                fields_desc = self.erp_query(job, matrix_obj.np_model, 'fields_get', [], {'attributes': ['string', 'help', 'type', 'required']})
                rel_obj.send_btf_create_email(fields_desc)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.api_rel_id.exists():
                if job.api_rel_id.error_log is False:
                    job.api_rel_id.error_log = ''
                job.api_rel_id.error_count += 1
                if job.api_rel_id.error_count % 20 == 0:
                    job.api_rel_id.error_log = job.api_rel_id.error_log[:len(job.api_rel_id.error_log)/2]
                job.api_rel_id.error_log = str(job.api_rel_id.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=e) + '\n\n' + job.api_rel_id.error_log
            _logger.error(e)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('btf_action_sync_create: unable to create record in ERP database')

    @api.model
    def btf_action_sync_unlink(self, job, rec):
        """
        #  ____ _____ _____   _____       _____ ____  ____
        # | __ )_   _|  ___| |_   _|__   | ____|  _ \|  _ \
        # |  _ \ | | | |_      | |/ _ \  |  _| | |_) | |_) |
        # | |_) || | |  _|     | | (_) | | |___|  _ <|  __/
        # |____/ |_| |_|       |_|\___/  |_____|_| \_\_|
        # BTF to ERP

        data_dict
        {'__last_update': '2019-11-05 04:12:09',
         'create_date': '2019-11-05 04:12:09',
         'create_uid': res.users(1,),
         'data': False,
         'display_name': u'shipping.agent_20550',
         'id': 15,
         'init_user_id': res.users(1,),
         'keyword': u"[('name', '=', u'TITANIC')]",
         'name': u'shipping.agent_20550',
         'priority': 23,
         'state': u'pending',
         'sync_action': u'unlink',
         'sync_model': u'shipping.agent',
         'sync_model_id': 20550,
         'write_date': '2019-11-05 04:12:09',
         'write_uid': res.users(1,)}
        """
        np_model = ''
        erp_records = []
        keyword = []
        try:
            data_dict = {k: rec[k] for k,v in rec._fields.iteritems()}
            matrix_obj = self.get_dp_np_db_matrix('dp', rec.sync_model)
            if not isinstance(data_dict['keyword'], str):
                keyword = ast.literal_eval(data_dict['keyword'])
            else:
                keyword = data_dict['keyword']
            keyword = self.change_keyword(matrix_obj, keyword)
            np_model = matrix_obj.np_model
            if np_model == '':
                np_model = rec.sync_model
            erp_records = self.erp_query(job, np_model, 'search_read', [keyword], {'fields': ['id']})
            if len(erp_records) == 0:
                raise NoRecordsFoundException
            if len(erp_records) > 1:
                raise AssertionError
            np_id = erp_records[0]['id']
            unlink_state = self.erp_query(job, np_model, 'unlink', [[np_id]])
            if unlink_state:
                # unlink_state return true if unlink success
                rel_obj = job.create_relation_lines({'dp_np_api_id': job.id, 'state': 'sync_data_to_erp',
                                                     'data_sync_id': rec.id,
                                                     'np_id': np_id, 'np_model': np_model, 'action_type': 'unlink',
                                                     'dp_model': rec.sync_model, 'dp_id': rec.sync_model_id})
                job.api_rel_id = rel_obj.id
                rec.state = 'done'
                """
                self.erp_query(job, matrix_obj.np_model, 'fields_get', [], {'attributes': ['string', 'help', 'type']}) 
                returns 

                {'__last_update': {'string': 'Last Modified on', 'type': 'datetime'},
                 'active': {'string': 'Active', 'type': 'boolean'},
                 'contact': {'string': 'Contact', 'type': 'char'},
                 'cr_number': {'string': 'C R - Number', 'type': 'char'},
                 'create_date': {'string': 'Created on', 'type': 'datetime'},
                 'create_uid': {'string': 'Created by', 'type': 'many2one'},
                 'display_name': {'string': 'Display Name', 'type': 'char'},
                 'id': {'string': 'ID', 'type': 'integer'},
                 'is_sync_to_btf': {'string': 'Show in BuyTaxFree', 'type': 'boolean'},
                 'name': {'string': 'Name', 'type': 'char'},
                 'write_date': {'string': 'Last Updated on', 'type': 'datetime'},
                 'write_uid': {'string': 'Last Updated by', 'type': 'many2one'}}
                """
                fields_desc = self.erp_query(job, matrix_obj.np_model, 'fields_get', [], {'attributes': ['string', 'help', 'type', 'required']})
                rel_obj.send_btf_unlink_email(fields_desc)
            else:
                raise UnlinkException
        except UnlinkException as ue:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.api_rel_id.exists():
                if job.api_rel_id.error_log is False:
                    job.api_rel_id.error_log = ''
                job.api_rel_id.error_count += 1
                if job.api_rel_id.error_count % 20 == 0:
                    job.api_rel_id.error_log = job.api_rel_id.error_log[:len(job.api_rel_id.error_log) / 2]
                job.api_rel_id.error_log = str(job.api_rel_id.error_count) + '\t' + \
                                           (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                           '\t' + '{e}'.format(e=ue) + '\n\n' + job.api_rel_id.error_log
            _logger.error('-------------- Unlink Error for  ' + str(keyword) + ' ------------------')
            _logger.error(ue)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('np_model: ' + str(np_model) + ' keyword: ' + str(keyword))
            _logger.error('erp_records: ' + str(erp_records))
            _logger.error('THIS IS DUE TO UNLINK ERROR OF RECORD IN NEWPORT ERP DATABASE')
            _logger.error('btf_action_sync_unlink UnlinkException: -------------------------------------------------------------------------')
        except NoRecordsFoundException as nre:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.api_rel_id.exists():
                if job.api_rel_id.error_log is False:
                    job.api_rel_id.error_log = ''
                job.api_rel_id.error_count += 1
                if job.api_rel_id.error_count % 20 == 0:
                    job.api_rel_id.error_log = job.api_rel_id.error_log[:len(job.api_rel_id.error_log) / 2]
                job.api_rel_id.error_log = str(job.api_rel_id.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=nre) + '\n\n' + job.api_rel_id.error_log
            _logger.error('-------------- ERP no records found for  ' + str(keyword) + ' ------------------')
            _logger.error(nre)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('np_model: ' + str(np_model) + ' keyword: ' + str(keyword))
            _logger.error('erp_records: ' + str(erp_records))
            _logger.error('THIS IS DUE TO RECORD NOT FOUND IN NEWPORT ERP DATABASE')
            _logger.error('btf_action_sync_unlink NoRecordsFoundException: -------------------------------------------------------------------------')
        except AssertionError as ae:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.api_rel_id.exists():
                if job.api_rel_id.error_log is False:
                    job.api_rel_id.error_log = ''
                job.api_rel_id.error_count += 1
                if job.api_rel_id.error_count % 20 == 0:
                    job.api_rel_id.error_log = job.api_rel_id.error_log[:len(job.api_rel_id.error_log) / 2]
                job.api_rel_id.error_log = str(job.api_rel_id.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=ae) + '\n\n' + job.api_rel_id.error_log
            _logger.error(ae)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('np_model: ' + str(np_model) + ' keyword: ' + str(keyword))
            _logger.error('erp_records: ' + str(erp_records))
            _logger.error('THIS IS DUE TO MORE THAN 1 RECORDS FOUND IN BUYTAXFREE DATABASE')
            _logger.error('btf_action_sync_unlink AssertionError: -------------------------------------------------------------------------')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            if job.api_rel_id.exists():
                if job.api_rel_id.error_log is False:
                    job.api_rel_id.error_log = ''
                job.api_rel_id.error_count += 1
                if job.api_rel_id.error_count % 20 == 0:
                    job.api_rel_id.error_log = job.api_rel_id.error_log[:len(job.api_rel_id.error_log) / 2]
                job.api_rel_id.error_log = str(job.api_rel_id.error_count) + '\t' + \
                                               (dt.now() + relativedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') + \
                                               '\t' + '{e}'.format(e=e) + '\n\n' + job.api_rel_id.error_log
            _logger.error(e)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('erp_records' + str(erp_records) + ' np_model: ' + str(np_model) + ' keyword: ' + str(keyword))
            _logger.error('btf_action_sync_unlink Exception: -------------------------------------------------------------------------')

    @api.model
    def convert_dp_field_to_np_field(self, source_target, matrix_obj, data_dict):
        if source_target == "btf_to_erp":
            for field_matrix in matrix_obj.field_line_ids:
                if data_dict.has_key(field_matrix.dp_field) and field_matrix.np_field != field_matrix.dp_field:
                    data_dict[field_matrix.np_field] = data_dict[field_matrix.dp_field]
                    del data_dict[field_matrix.dp_field]
        else:
            for field_matrix in matrix_obj.field_line_ids:
                if data_dict.has_key(field_matrix.np_field) and field_matrix.np_field != field_matrix.dp_field:
                    data_dict[field_matrix.dp_field] = data_dict[field_matrix.np_field]
                    del data_dict[field_matrix.np_field]
        return data_dict

    @api.model
    def create_relation_lines(self, context=None):
        """
        create_relation_lines is similar to _create_relation_lines. difference is this returns the dp.np.api.rel object
        """
        if context is not None:
            return self.env['dp.np.api.rel'].create(context)
        else:
            return self.env['dp.np.api.rel'].create({'dp_np_api_id': self.id})

    @api.model
    def update_dp_m2o_fields_to_np_m2o_id(self, job, rec, data_dict, matrix_obj, args):
        """
        -------------------------------------------------- data_dict ---------------------------------------------------
        {'__last_update': '2019-11-07 01:43:39',
         'create_date': '2019-11-07 01:43:39',
         'create_uid': res.users(1,),
         'data': {u'crew': u'123',
                  u'flag': u'SG',
                  u'image': False,
                  u'imo_number': u'1111111111111111111111111111111',
                  u'name': u'HAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
                  u'nrt': u'2222222222222222',
                  u'shipping_agent': 17067,
                  u'type': 363,
                  u'via': False,
                  u'via_desc': False,
                  u'via_group': False},
         'display_name': u'vessel.name_275054',
         'id': 62,
         'init_user_id': res.users(1,),
         'keyword': False,
         'name': u'vessel.name_275054',
         'priority': 91,
         'state': u'pending',
         'sync_action': u'create',
         'sync_model': u'vessel.name',
         'sync_model_id': 275054,
         'write_date': '2019-11-07 01:43:39',
         'write_uid': res.users(1,)}
        -------------------------------------------------- data_dict ---------------------------------------------------

        ------------------------------------------------- matrix_obj ---------------------------------------------------
        dp.np.db.matrix(2,)
        ------------------------------------------------- matrix_obj ---------------------------------------------------

        ---------------------------------------------------- args ------------------------------------------------------
        {u'crew': u'123',
         u'flag': u'SG',
         u'image': False,
         u'imo_number': u'1111111111111111111111111111111',
         u'name': u'HAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
         u'nrt': u'2222222222222222',
         u'shipping_agent': 17067,
         u'type': 363,
         u'via': False,
         u'via_desc': False,
         u'via_group': False}
        ---------------------------------------------------- args ------------------------------------------------------


        ----------------------------------------------- np_field_type --------------------------------------------------
        {'__last_update': {'string': 'Last Modified on', 'type': 'datetime'},
         'create_date': {'string': 'Created on', 'type': 'datetime'},
         'create_uid': {'relation': 'res.users',
                        'string': 'Created by',
                        'type': 'many2one'},
         'crew': {'string': 'Crew No', 'type': 'char'},
         'display_name': {'string': 'Display Name', 'type': 'char'},
         'flag': {'string': 'Flag', 'type': 'char'},
         'id': {'string': 'ID', 'type': 'integer'},
         'image': {'help': 'This field holds the image used as avatar for this contact, limited to 1024x1024px',
                   'string': 'Image',
                   'type': 'binary'},
         'image_medium': {'help': 'Medium-sized image of this contact. It is automatically resized as a 128x128px image, with aspect ratio preserved. Use this field in form views or some kanban views.',
                          'string': 'Medium-sized image',
                          'type': 'binary'},
         'image_small': {'help': 'Small-sized image of this contact. It is automatically resized as a 64x64px image, with aspect ratio preserved. Use this field anywhere a small image is required.',
                         'string': 'Small-sized image',
                         'type': 'binary'},
         'imo_number': {'string': 'IMO Number', 'type': 'char'},
         'is_sync_to_btf': {'string': 'Show in BuyTaxFree', 'type': 'boolean'},
         'name': {'string': 'Name', 'type': 'char'},
         'note': {'string': 'Notes', 'type': 'text'},
         'nrt': {'string': 'NRT', 'type': 'char'},
         'shipping_agent': {'relation': 'ship.agent',
                            'string': 'Shipping Agent',
                            'type': 'many2one'},
         'type': {'relation': 'np.vessel.type', 'string': 'Type', 'type': 'many2one'},
         'via': {'string': 'Ship Via', 'type': 'char'},
         'via_desc': {'string': 'Ship Via Desc.', 'type': 'char'},
         'via_group': {'string': 'Ship Via Grp CD', 'type': 'char'},
         'write_date': {'string': 'Last Updated on', 'type': 'datetime'},
         'write_uid': {'relation': 'res.users',
                       'string': 'Last Updated by',
                       'type': 'many2one'}}
        ----------------------------------------------- np_field_type --------------------------------------------------

        ----------------------------------------- exclude_many2one_columns ---------------------------------------------
        exclude_many2one_columns = ('create_uid', 'write_uid')
        many2one fields that are not required
        ----------------------------------------- exclude_many2one_columns ---------------------------------------------
        """
        exclude_many2one_columns = ('create_uid', 'write_uid')
        model = matrix_obj.dp_model
        model_id = data_dict.get('sync_model_id', 0)
        dp_obj = self.env[model].browse(model_id)
        # np_field_type = self.erp_query(job, matrix_obj.np_model, 'fields_get', [],
        #                             {'attributes': ['string', 'help', 'type', 'relation']})
        args = self.get_dp_many2one_fkey_value(exclude_many2one_columns, args, dp_obj, matrix_obj, job)
        return args

    @api.model
    def get_dp_many2one_fkey_value(self, exclude_many2one_columns, data_to_create, dp_obj, matrix_obj, job):
        m2o = self.get_dp_many2one_field_model(exclude_many2one_columns, dp_obj)
        create_data_exclude_columns = exclude_many2one_columns + ('create_date', 'write_date', '__last_update', 'id', \
                                                                  'source_origin', 'is_to_np', 'is_from_np', \
                                                                  'sync_status', 'erp_id')
        for field, dpmodel in m2o:
            """
            field, dpmodel
            ('type', 'vessel.type')
            ('shipping_agent', 'shipping.agent')
            
            """
            db_matrix_obj = self.env['dp.np.db.matrix'].search([('dp_model', '=', dpmodel)])
            dp_field_obj = dp_obj[field]
            np_field_types = self.get_erp_field_types(job, matrix_obj.np_model)
            keyword = []
            try:
                if 'name' in dp_field_obj._fields:
                    keyword.append(('name', '=', dp_field_obj.name))
                if 'code' in dp_field_obj._fields:
                    keyword.append(('code', '=', dp_field_obj.code))

                if data_to_create[field] is False and np_field_types[field] is False:
                    raise BTFMany2OneFieldIsEmptyException
                erp_records = self.erp_query(job, db_matrix_obj.np_model, 'search_read', [keyword], {'fields': ['id']})
                if len(erp_records) == 0:
                    raise NoRecordsFoundException
                if len(erp_records) > 1:
                    """
                    take last record since previous records have high chance of "errors" resulting in newer
                    records to be created
                    """
                    erp_records = [erp_records[len(erp_records)-1]]
                # below assumes erp_records return 1 record
                # TODO: to redo this part if issue arise
                np_record_id = erp_records[0]['id']

                # data_to_create[field] contains the ID of btf model, np_record_id is the corresponding
                # record in newport erp
                data_to_create[field] = np_record_id
            except BTFMany2OneFieldIsEmptyException:
                del data_to_create[field]
                continue
            except NoRecordsFoundException as nre:
                _logger.info('THIS IS DUE TO RECORD NOT FOUND IN ERP DATABASE')
                _logger.info('get_dp_many2one_fkey_value NoRecordsFoundException: -------------------------------------------------------------------------')
                _logger.info('get_dp_many2one_fkey_value Creating Record in Newport ERP Database: START -------------------------------------------------------------------------')
                not_in_erp_dp_obj = self.env[db_matrix_obj.dp_model].search(keyword)
                erp_data_create = {k: not_in_erp_dp_obj[k] for k, v in not_in_erp_dp_obj._fields.iteritems() if k not in create_data_exclude_columns}
                new_erp_job = self.create({'state': 'sync_data_to_erp'})
                self._get_credentials_(new_erp_job)
                self.erp_connect(new_erp_job)
                res_id = new_erp_job.erp_query(new_erp_job, db_matrix_obj.np_model, 'create', args=[erp_data_create])
                rel_obj = new_erp_job.create_relation_lines({'dp_np_api_id': new_erp_job.id, 'state': 'sync_data_to_erp',
                                            'erp_record': json.dumps(erp_data_create), 'action_type': 'create',
                                            'np_id': res_id, 'np_model': db_matrix_obj.np_model,
                                            'dp_model': db_matrix_obj.dp_model,
                                            'dp_id': not_in_erp_dp_obj.id})
                new_erp_job.api_rel_id = rel_obj.id
                data_to_create[field] = res_id
                _logger.info('get_dp_many2one_fkey_value Create Record in Newport ERP Database: SUCESS-------------------------------------------------------------------------')
                continue
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception: ' + str(e))
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('get_dp_many2one_fkey_value Exception: -------------------------------------------------------------------------')
        return data_to_create

    @api.model
    def get_dp_many2one_field_model(self, exclude_many2one_columns, dp_obj):
        """
        ('via', vessel.name.via, <class 'openerp.fields.Char'>, 'char', None)
        ('create_date', vessel.name.create_date, <class 'openerp.fields.Datetime'>, 'datetime', None)
        ('imo_number', vessel.name.imo_number, <class 'openerp.fields.Char'>, 'char', None)
        ('image', vessel.name.image, <class 'openerp.fields.Binary'>, 'binary', None)
        ('write_uid', vessel.name.write_uid, <class 'openerp.fields.Many2one'>, 'many2one', 'res.users')
        ('id', vessel.name.id, <class 'openerp.fields.Id'>, 'integer', None)
        ('via_desc', vessel.name.via_desc, <class 'openerp.fields.Char'>, 'char', None)
        ('create_uid', vessel.name.create_uid, <class 'openerp.fields.Many2one'>, 'many2one', 'res.users')
        ('display_name', vessel.name.display_name, <class 'openerp.fields.Char'>, 'char', None)
        ('is_to_np', vessel.name.is_to_np, <class 'openerp.fields.Boolean'>, 'boolean', None)
        ('__last_update', vessel.name.__last_update, <class 'openerp.fields.Datetime'>, 'datetime', None)
        ('crew', vessel.name.crew, <class 'openerp.fields.Char'>, 'char', None)
        ('via_group', vessel.name.via_group, <class 'openerp.fields.Char'>, 'char', None)
        ('sync_status', vessel.name.sync_status, <class 'openerp.fields.Boolean'>, 'boolean', None)
        ('type', vessel.name.type, <class 'openerp.fields.Many2one'>, 'many2one', 'vessel.type')
        ('is_from_np', vessel.name.is_from_np, <class 'openerp.fields.Boolean'>, 'boolean', None)
        ('flag', vessel.name.flag, <class 'openerp.fields.Char'>, 'char', None)
        ('write_date', vessel.name.write_date, <class 'openerp.fields.Datetime'>, 'datetime', None)
        ('shipping_agent', vessel.name.shipping_agent, <class 'openerp.fields.Many2one'>, 'many2one', 'shipping.agent')
        ('nrt', vessel.name.nrt, <class 'openerp.fields.Char'>, 'char', None)
        ('name', vessel.name.name, <class 'openerp.fields.Char'>, 'char', None)
        ('erp_id', vessel.name.erp_id, <class 'openerp.fields.Integer'>, 'integer', None)
        ('source_origin', vessel.name.source_origin, <class 'openerp.fields.Selection'>, 'selection', None)

        for k, v in dp_obj._fields.iteritems():
            print(k, v, type(v), v.type, v.comodel_name)

        returns field name and dp_model name
        """
        for k, v in dp_obj._fields.iteritems():
            if v.type == 'many2one' and k not in exclude_many2one_columns:
                yield (k, v.comodel_name)

    @api.model
    def get_erp_field_types(self, job, model):
        return self.erp_query(job, model, 'fields_get', [], {'attributes': []})

    @api.model
    def check_if_dp_field_is_property_field(self, obj, field):
        """
        return true if it is property field
        else return None
        """
        if obj._fields.has_key(field):
            if obj._fields[field]:
                if obj._fields[field].column is not None:
                    if isinstance(obj._fields[field].column._multi, str):
                        if obj._fields[field].column._multi == 'properties':
                            return True
        return False

    @api.model
    def check_model_exist_in_buytaxfee(self, model):
        new_matrix_obj = self.get_dp_np_db_matrix('np', model)
        if new_matrix_obj:
            model = new_matrix_obj.dp_model
        obj = self.env['ir.model'].search([('model', '=', model)])
        if obj.exists():
            return True
        return False

    @api.model
    def dumb_way_to_handle_product_template_product_category(self, data_to_create, field, np_related_model, field_type, matrix_obj, job):
        try:
            search_id = data_to_create[field]
            if isinstance(data_to_create[field], list):
                if isinstance(data_to_create[field][0], int):
                    search_id = data_to_create[field][0]
            erp_records = self.erp_query(job, np_related_model, 'search_read', [[['id', '=', search_id]]], {'fields': []})
            if len(erp_records) == 0:
                raise NoRecordsFoundException
            if len(erp_records) > 1:
                raise AssertionError
            erp_dict = erp_records[0]
            new_job = self.env['dp.np.api'].create({'state': 'sync_data_to_btf'})
            self._get_credentials_(new_job)
            self.erp_connect(new_job)
            rel_obj = new_job.create_relation_lines(
                        {'dp_np_api_id': new_job.id, 'state': 'sync_data_to_btf', 'action_type': 'create',
                         'erp_record': json.dumps(erp_dict)})
            new_job.api_rel_id = rel_obj.id
            new_matrix_obj = self.get_dp_np_db_matrix('np', np_related_model)

            np_categ_id = data_to_create['categ_id']
            if isinstance(np_categ_id, list):
                if isinstance(np_categ_id[0], int):
                    np_categ_id = np_categ_id[0]
            new_field_type = self.erp_query(job, np_related_model, 'fields_get', [], {'attributes': ['string', 'relation', 'type', 'required']})
            erp_records = self.erp_query(job, np_related_model, 'search_read', [[['id', '=', np_categ_id]]],{'fields': []})
            if len(erp_records) == 0:
                raise NoRecordsFoundException
            if len(erp_records) > 1:
                raise AssertionError
            erp_dict = erp_records[0]
            dp_categ_obj = self.env[new_matrix_obj.dp_model].search([('name', '=', erp_dict.get('name', ''))])
            if dp_categ_obj.exists():
                data_to_create['categ_id'] = dp_categ_obj.id
            else:
                # TODO: create product category
                categ_name = erp_dict.get('name', '')
                if categ_name != '':
                    new_dp_categ_obj = self.env[new_matrix_obj.dp_model].create({'name': categ_name})
                    data_to_create['categ_id'] = new_dp_categ_obj.id
                else:
                    raise KeyError
            # data_to_create, field_type, job, rec = self.update_np_m2o_fields_to_dp_m2o_ids(new_matrix_obj, data, new_field_type, dp_model, job, rec)
            # if is_create:
            #     _logger.info('------------------------------' + str(obj) + ' create start ---------------------------------')
            #     # TODO: need to convert all foreign keys into their respective id in btf db
            #     obj = self.env[dp_model].with_context({'from_erp': True}).create(data_to_create)
            #     self._cr.commit()
            #     _logger.info('------------------------------' + str(obj) + ' create end -----------------------------------')
            #     self.erp_query(job, 'btf.data.sync', 'write', [[btf_data_sync_id],  {'state': "done"}])
            #     obj.sync_status = True  # turn true only if erp query and self.env.create is successful
            #     _logger.info('-------------- ERP btf.data.sync ' + str(btf_data_sync_id) + ' write successful ------------------')
        except NoRecordsFoundException as nre:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error(nre)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('field: '+ field + ' np_related_model: ' + np_related_model)
            _logger.error('THIS IS DUE TO RECORD NOT FOUND IN ERP DATABASE')
            _logger.error('get_np_many2one_fkey_value NoRecordsFoundException: -------------------------------------------------------------------------')
        except KeyError as ke:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception: ' + str(ke))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('field: '+ field + ' np_related_model: ' + np_related_model)
            _logger.error('dumb_way_to_handle_product_template_product_category KeyError: -------------------------------------------------------------------------')
        except AssertionError as ae:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception: ' + str(ae))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('field: '+ field + ' np_related_model: ' + np_related_model)
            _logger.error('dumb_way_to_handle_product_template_product_category AssertionError: -------------------------------------------------------------------------')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception: ' + str(e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('field: '+ field + ' np_related_model: ' + np_related_model)
            _logger.error('dumb_way_to_handle_product_template_product_category Exception: -------------------------------------------------------------------------')
        return data_to_create

    @api.model
    def dumb_way_to_handle_product_template_product_category_bool(self, np_related_model, field):
        if np_related_model in ('product.category') and field in ('categ_id'):
            return True
        return False

    @api.model
    def dumb_way_to_handle_account_account(self, field, np_related_model, data_to_create, new_matrix_obj, matrix_obj):
        product_category = 'product.category'
        dp_field_obj = self.env[product_category]
        try:
            if matrix_obj.exists():
                if matrix_obj.dp_model in (product_category, 'account.account', 'account.journal'):
                    if self.check_if_dp_field_is_property_field(dp_field_obj, field):
                        ir_property_obj = self.env['ir.property']
                        _logger.info('Deleting ' + str(data_to_create[field]) + ' field START ----------------------------------')
                        del data_to_create[field]
                        _logger.info('Deleting field SUCCESS ----------------------------------------------------------------')
                    else:
                        _logger.info('Deleting ' + str(data_to_create[field]) + ' field START ----------------------------------')
                        del data_to_create[field]
                        _logger.info('Deleting field SUCCESS ----------------------------------------------------------------')
                        raise IsNotPropertyFieldException
                else:
                    raise ModelIsNotYYYModelException
        except IsNotPropertyFieldException as inpfe:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error(inpfe)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('categ_obj: ' + str(dp_field_obj) + ' field: ' + str(field))
            _logger.error('new_matrix_obj: ' + str(new_matrix_obj) + ' matrix_obj: ' + str(matrix_obj))
            _logger.error('dumb_way_to_handle_account_account IsNotPropertyFieldException: -------------------------------------------------------------------------')
        except ModelIsNotYYYModelException as minyyyme:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error(minyyyme)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('Model: ' + str(product_category))
            _logger.error('dumb_way_to_handle_account_account ModelIsNotYYYModelException: -------------------------------------------------------------------------')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error(e)
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('matrix_obj: ' + str(matrix_obj) + ' new_matrix_obj: ' + str(new_matrix_obj))
            _logger.error('data_to_create: ' + str(data_to_create))
            _logger.error('field: ' + str(field) + ' np_related_model: ' + str(np_related_model))
            _logger.error('dumb_way_to_handle_account_account Exception: -------------------------------------------------------------------------')
        return data_to_create

    @api.model
    def dumb_way_force_ignore_fields(self, np_related_model, field):
        if np_related_model in ('product.product') and field in ('duty_free_product'):
            return True
        return False

class DPNPAPIRelExtend(models.Model):
    _inherit = "dp.np.api.rel"

    erp_record = fields.Text('Data To Be Sync')
    np_model = fields.Char('New Port Model')
    np_id = fields.Integer('New Port Model ID')
    dp_model = fields.Char('BuyTaxFree Model')
    dp_id = fields.Integer('BuyTaxFree Model ID')
    action_type = fields.Selection([('create', 'Create'), ('write', 'Write'), \
                                    ('unlink', 'Unlink'), ('search_read', 'Search and Read'), \
                                    ('fields_get', 'Fields Get'), ('search', 'Search'), ('read', 'Read'), \
                                    ('search_count', 'Search Count'), ('check_access_rights', 'Check Access Rights'),], \
                                   'Action Type')
    data_sync_id = fields.Many2one('erp.data.sync', 'Data Sync ID')

    @api.model
    def send_btf_write_email(self, fields_dict={}):
        self.with_context({'action': 'UPDATE', 'fields_dict': fields_dict}).send_btf_crud_email()

    @api.model
    def send_btf_create_email(self, fields_dict={}):
        self.with_context({'action': 'CREATE', 'fields_dict': fields_dict}).send_btf_crud_email()

    @api.model
    def send_btf_unlink_email(self, fields_dict={}):
        self.with_context({'action': 'DELETE', 'fields_dict': fields_dict}).send_btf_crud_email()

    @api.model
    def send_btf_crud_email(self):
        try:
            action = self._context.get('action', '')
            fields_dict = self._context.get('fields_dict', {})
            action_matrix = {'CREATE': 'create', 'DELETE': 'unlink', 'UPDATE': 'write'}
            action_key = action_matrix[action]
            partner_id = self.env.user.partner_id.id
            dp_np_api_ids = [i.id for i in self]
            len_sale_ids = len(dp_np_api_ids)
            i = 0
            threads = []
            total_sale_ids_thread = len_sale_ids / CPU
            for i in range(0, CPU - 1):
                t = threading.Thread(target=self.with_context({'action': action, 'partner_id': partner_id,
                                                               'fields_dict': fields_dict,
                                                               action_key: True}).send_btf_crud_email_multithreading,
                                     args=(dp_np_api_ids[i * total_sale_ids_thread: total_sale_ids_thread * (i + 1)],))
                threads.append(t)
                t.start()
            t = threading.Thread(target=self.with_context({'action': action, 'partner_id': partner_id,
                                                           'fields_dict': fields_dict,
                                                           action_key: True}).send_btf_crud_email_multithreading,
                                 args=(dp_np_api_ids[(i + 1) * total_sale_ids_thread:],))
            t.start()
            threads.append(t)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception: ' + str(e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('Multithreading Problems --------------------------------------------------------------------------------')

    @api.model
    def send_btf_crud_email_multithreading(self, dp_np_api_ids):
        _logger.info('------------------------------------------------------ dp_np_api_extend.send_btf_crud_email_multithreading START THREAD')
        with api.Environment.manage():
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            uid = self.env.uid
            start_thread = dt.now()
            new_env = api.Environment(new_cr, uid, self.env.context.copy())
            new_self = self.with_env(new_env)
            for record in new_self.env['dp.np.api.rel'].browse(dp_np_api_ids):


                # TODO: CHANGE FORLOOP
                data_sync_obj = new_self.env['erp.data.sync'].browse(record.data_sync_id.id)
                database_matrix = new_self.env['dp.np.db.matrix'].search([('dp_model', '=', data_sync_obj.sync_model)])
                """
                record._context.get('action', '') will get keys in the below dictionary
                {'CREATE': 'create', 'DELETE': 'unlink', 'UPDATE': 'write'}
                """
                action_type = record._context.get('action', '')
                if isinstance(data_sync_obj.keyword, str) or isinstance(data_sync_obj.keyword, unicode):
                    keyword = ast.literal_eval(data_sync_obj.keyword)
                else:
                    keyword = data_sync_obj.keyword
                keyword_name = ''
                if action_type == 'CREATE':
                    data = json.loads(record.erp_record)
                elif action_type == 'UPDATE':
                    data = json.loads(data_sync_obj.data)
                    data = record.dp_np_api_id.convert_dp_field_to_np_field("btf_to_erp", database_matrix, data)
                    if len(keyword) == 1:
                        if len(keyword[0]) == 3:
                            keyword_name = keyword[0][2]
                elif action_type == 'DELETE':
                    data = {}
                    if len(keyword) == 1:
                        if len(keyword[0]) == 3:
                            keyword_name = keyword[0][2]
                else:
                    raise Exception
                fields_dict = record._context.get('fields_dict', {})
                data = self.convert_field_name_to_field_strings(data, fields_dict)
                partner_obj = new_self.env['res.partner'].browse(record._context.get('partner_id', 0))




                try:
                    send_template = new_self.env.ref('dp_np_api_extend.data_sync_from_btf_to_erp')
                    _logger.info('dp_np_api_extend.data_sync_from_btf_to_erp START')
                    send_template.with_context({'action': action_type,
                                                'partner_obj': partner_obj, 'partner_email': partner_obj.email,
                                                'action_key': record._context.get('action_key', False),
                                                'np_model': database_matrix.display_name, 'record': keyword_name,
                                                'data_sync_obj': data_sync_obj,
                                                'data': data}).send_mail(record.id, force_send=True, raise_exception=True)
                    _logger.info('dp_np_api_extend.data_sync_from_btf_to_erp SUCCESS')
                except psycopg2.InternalError:
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                    continue
                except Exception as e:
                    _logger.exception('{} While sending accepted invitation exception generated'.format(record))
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + ' Line Numnber: ' + str(exc_tb.tb_lineno))
                    new_cr.close()
                    new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                    new_env = api.Environment(new_cr, uid, self.env.context.copy())
                    new_self = self.with_env(new_env)
            finish_thread = dt.now() - start_thread
            _logger.info(('------------------------------------------------------ dp_np_api_extend.send_btf_crud_email_multithreading TIME FINISH 1 thread: %s') % (finish_thread.total_seconds()))
            new_cr.commit()
            new_cr.close()

    @api.model
    def convert_field_name_to_field_strings(self, data={}, fields_dict={}):
        for dk, dv in data.iteritems():
            if fields_dict.has_key(dk):
                data[fields_dict[dk].get('string', '')] = dv
                del data[dk]
        return data