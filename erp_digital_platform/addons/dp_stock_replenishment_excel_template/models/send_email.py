from openerp import models, fields, api
from datetime import datetime
import logging, sys
import pytz
_logger = logging.getLogger('stock.replenishment')


class email(models.Model):
    _inherit = "stock.replenishment"

    @api.multi
    def stock_replishment_send_email(self):
        self.stock_replenish_send_email()
        return True

    @api.model
    def stock_replenish_send_email(self):
        try:
            _logger.info('---------------------- dp_stock_replenishment_excel_template.stock_replenish_send_email START')
            template = self.env.ref('dp_stock_replenishment_excel_template.stock_replenishment_email')
            template.send_mail(self.id, force_send=True, raise_exception=True)
            _logger.info('---------------------- dp_stock_replenishment_excel_template.stock_replenish_send_email SUCCESS')
        except Exception as e:
            _logger.info('{e}'.format(e=e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.info('stock_replenish_send_email: Unable to send stock replenish emails')


    def get_current_timestamp(self):
        date_time = str(datetime.now())
        cur_dt = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S.%f')
        cur_dt = cur_dt.replace(second=0, microsecond=0)
        cur_dt_without_second = cur_dt.strftime('%Y-%m-%d %H:%M')

        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        localized_date = datetime.strftime(pytz.utc.localize(datetime.strptime(cur_dt_without_second,
                                                                                    '%Y-%m-%d %H:%M')).astimezone(
            local), '%Y-%m-%d %H:%M')
        if self._context.get('get_YYYYMMDD', False):
            return localized_date

        dateformat = localized_date.split(' ')
        return dateformat[0] + '_' + dateformat[1]

    def get_supplier_newport_email(self):
        np = self.env['res.partner'].search([('company_code', '=', 'New Port')])
        np.ensure_one()
        return np.email