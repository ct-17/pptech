from openerp import models, fields, api, SUPERUSER_ID, sql_db
from openerp.http import request
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DSDF
from openerp.exceptions import except_orm, Warning
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from datetime import datetime as dt
import logging, sys, random, threading,psycopg2, time
_logger = logging.getLogger(__name__)


class DPIRValues(models.Model):
    _inherit = "ir.values"

    @api.model
    def _drop_print_quotation_if_not_superadmin(self, action_slot, model, res):
        if model == 'sale.order' and action_slot == 'client_print_multi':
            order_entry = self.env.ref('dp_sale_template.order_entry_pdf')
            body_template = self.env.ref('dp_sale_template.np_sale_order_body_template')
            is_stock_user = self.user_has_groups('dp_common.group_super_admin')
            res = [r for r in res if r[0] not in (order_entry.id, body_template.id) or is_stock_user]
        return res

    @api.model
    def get_actions(self, action_slot, model, res_id=False):
        res = super(DPIRValues, self).get_actions(action_slot, model, res_id=res_id)
        res = self._drop_print_quotation_if_not_superadmin(action_slot, model, res)
        return res