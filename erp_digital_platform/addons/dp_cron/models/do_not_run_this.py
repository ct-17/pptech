from openerp import fields, models, api, _
from openerp.exceptions import Warning, except_orm
import logging, sys, psycopg2
from inspect import currentframe, getframeinfo
cf = currentframe()
filename = getframeinfo(cf).filename
_logger = logging.getLogger(__name__)


class CronInheritInherit(models.Model):
    _inherit = "ir.cron"

    counter = fields.Integer('Counter', default=1)

    @api.multi
    def method_direct_trigger(self):
        # super here so as for easy removal
        if self.name == "Clean DB - Run this and you ACCEPT RESPONSIBILITIES of data loss":
            if self.counter <= 4:
                msg_dict = {
                    1: {'header': "Alert!",
                        'body': "You are attempting to perform data cleansing on a database!\nYou need to do this action 4 more times!"},
                    2: {'header': "Warning!!",
                        'body': "You are attempting to perform data cleansing on a database!\nYou need to do this action 3 more times!"},
                    3: {'header': "Are you sure!?!?",
                        'body': "You are attempting to perform data cleansing on a database!\nYou need to do this action 2 more times!"},
                    4: {'header': "THE NEXT ACTION CANNOT BE REVERSED!",
                        'body': "BY CLICKING RUN CRON JOB 1 MORE TIME, YOU ACCEPT ALL RESPONSIBILITIES OF DELETING ALL DATA AND SYSTEM ADMIN/DEVELOPERS SHALL NOT BE HELD ACCOUNTABLE FOR THE LOSS OF DATA!!!!!!!!!!\n MAY GOD HAVE MERCY ON YOUR SOUL!"},
                }
                header = msg_dict[self.counter]['header']
                body = msg_dict[self.counter]['body']
                self._increase_counter()
                raise except_orm(_(header), _(body))
            else:
                self._reset_counter()
        res = super(CronInheritInherit, self).method_direct_trigger()
        return res

    @api.model
    def _increase_counter(self):
        self.counter += 1
        self._cr.commit()

    @api.model
    def _reset_counter(self):
        self.counter = 1


class DoNotRunThis(models.TransientModel):
    _name = 'do.not.run.this'

    @api.model
    def get_clean_db_sql(self):
        sql_list = [
            """delete from sale_order;""",
            """ALTER SEQUENCE sale_order_id_seq RESTART WITH 1;""",
            """delete from purchase_order;""",
            """ALTER SEQUENCE purchase_order_id_seq RESTART WITH 1;""",
            """delete from sale_line_stock_allocation;""",
            """ALTER SEQUENCE sale_line_stock_allocation_id_seq RESTART WITH 1;""",
            """delete from dp_chandler_temp where email not in ('kchsin@kchsin.com', 'lin.wang@xingyuan.com.sg', 'Sales@singmarmarine.com', 'ted@tkenterprises.com.sg', 'tkedward56@gmail.com') and name not in ('BTF Sales');""",
            # """ALTER SEQUENCE dp_chandler_temp_id_seq RESTART WITH 1;""",
            """delete from account_invoice;""",
            """ALTER SEQUENCE account_invoice_id_seq RESTART WITH 1;""",
            """delete from stock_pack_operation;""",
            """ALTER SEQUENCE stock_pack_operation_id_seq RESTART WITH 1;""",
            """delete from stock_picking;""",
            """ALTER SEQUENCE stock_picking_id_seq RESTART WITH 1;""",
            """delete from stock_move;""",
            """ALTER SEQUENCE stock_move_id_seq RESTART WITH 1;""",
            """delete from dp_np_api_rel;""",
            """ALTER SEQUENCE dp_np_api_rel_id_seq RESTART WITH 1;""",
            """delete from dp_np_api;""",
            """ALTER SEQUENCE dp_np_api_id_seq RESTART WITH 1;""",
            """delete from dp_shipmaster_invitation;""",
            """ALTER SEQUENCE dp_shipmaster_invitation_id_seq RESTART WITH 1;""",
            """delete from shipmaster_invitation;""",
            """ALTER SEQUENCE shipmaster_invitation_id_seq RESTART WITH 1;""",
            """delete from wkf_instance;""",
            """delete from sale_order_chandler;""",
            """ALTER SEQUENCE sale_order_chandler_id_seq RESTART WITH 1;""",
            """delete from res_users where login not in ('ppt_consult', 'ppt_dev', 'public', 'portaltemplate', 'templatechandler', 'templateshipmaster', 'kchsin@kchsin.com', 'lin.wang@xingyuan.com.sg', 'Sales@singmarmarine.com', 'ted@tkenterprises.com.sg', 'tkedward56@gmail.com', 'weilok@newport.com.sg') and login not like '%admin%';""",
            """delete from res_partner where lower(name) not like '%admin%' and lower(name) not in ('ppt consultant', 'ppt developer', 'warehouse', 'buytaxfree', 'template chandler', 'template shipmaster', 'public user', 'template user', 'new port duty free pte ltd', 'BTF Sales') and email not in ('kchsin@kchsin.com', 'lin.wang@xingyuan.com.sg', 'Sales@singmarmarine.com', 'ted@tkenterprises.com.sg', 'tkedward56@gmail.com', 'weilok@newport.com.sg');""",
        ]
        return sql_list

    @api.model
    def cron_clean_db(self):
        config_param_obj = self.env['ir.config_parameter'].search([('key', '=', 'cron_job_delete_parameter')])
        if config_param_obj.exists():
            if config_param_obj.value == 'omaemoshindeiru':
                job = self.env['do.not.run.this'].create({})
                sql_list = job.get_clean_db_sql()
                for sql in sql_list:
                    try:
                        job._cr.execute(sql)
                        _logger.warning(sql)
                    except psycopg2.InternalError as ie:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        _logger.error('dp_cron.cron_clean_db exception: {e}'.format(e=ie))
                        _logger.error('Exception Type: ' + str(exc_type))
                        _logger.error('Exception Error Description: ' + str(exc_obj))
                        _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        _logger.error('dp_cron.cron_clean_db exception: {e}'.format(e=e))
                        _logger.error('Exception Type: ' + str(exc_type))
                        _logger.error('Exception Error Description: ' + str(exc_obj))
                        _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))

                # reset sequence
                ir_seq_obj = self.env['ir.sequence'].sudo().search([('name', 'ilike', '%Order'), ('implementation', '=', 'no_gap')])
                if ir_seq_obj.exists():
                    if len(ir_seq_obj) == 2:
                        for obj in ir_seq_obj:
                            obj.sudo().write({'number_next': 1})
                    else:
                        _logger.error('dp_cron.ir_seq_obj error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                        _logger.error('Line Numnber: ' + str(cf.f_lineno) + ' Filename: ' + str(filename))