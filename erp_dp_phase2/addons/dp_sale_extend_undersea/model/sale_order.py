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


class DPSaleOrderUnderTheSea(models.Model):
    _inherit = "sale.order"

    sm_send_amendment_flag = fields.Selection([('sm_send', 'Shipmaster Send'), ('chan_send', 'Chandler Send')])

    @api.multi
    def action_send_adjustment_email(self):
        res = super(DPSaleOrderUnderTheSea, self).action_send_adjustment_email()
        self.sm_send_amendment_flag = 'sm_send'
        return res

    @api.multi
    def action_dp_quotation_send_again(self):
        res = super(DPSaleOrderUnderTheSea, self).action_dp_quotation_send_again()
        self.sm_send_amendment_flag = 'chan_send'
        return res
