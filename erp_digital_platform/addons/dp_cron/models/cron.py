from openerp import models, api
from dateutil.relativedelta import relativedelta
from datetime import datetime as dt
import logging
_logger = logging.getLogger(__name__)


class CronInherit(models.Model):
    _inherit = "ir.cron"

    @api.multi
    def method_direct_trigger(self):
        cron_obj = self.browse(self.ids)
        for cron in cron_obj:
            self._callback(cron.model, cron.function, cron.args, cron.id)
        return True

    @api.multi
    def method_direct_trigger_change_date(self):
        cron_obj = self.browse(self.ids)
        for cron in cron_obj:
            rd = relativedelta()
            if cron.interval_type == 'minutes':
                rd = relativedelta(minutes=cron.interval_number)
            elif cron.interval_type == 'hours':
                rd = relativedelta(hours=cron.interval_number)
            elif cron.interval_type == 'work_days':
                rd = relativedelta(weekday=cron.interval_number)
            elif cron.interval_type == 'days':
                rd = relativedelta(days=cron.interval_number)
            elif cron.interval_type == 'weeks':
                rd = relativedelta(weeks=cron.interval_number)
            elif cron.interval_type == 'months':
                rd = relativedelta(months=cron.interval_number)
            cron.nextcall = dt.now() + rd
            self._callback(cron.model, cron.function, cron.args, cron.id)
        return True