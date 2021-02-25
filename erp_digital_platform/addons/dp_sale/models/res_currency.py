from openerp import models, fields, api, SUPERUSER_ID
from openerp.exceptions import except_orm
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class DPResCurrency(models.Model):
    _inherit = "res.currency"

    @api.multi
    def name_get(self):
        result = []
        curr_obj = self
        chan_curr_id = []
        if self._context.get('order_id', False):
            sale_obj = self.env['sale.order'].browse(self._context.get('order_id'))
            curr_obj = self.env['res.currency'].search([], order='id')
            chan_curr_id = [curr.currency_id.id for curr in sale_obj.user_id.partner_id.currency_line]

        for record in curr_obj:
            string = record.name
            if self._context.get('chandlerquotation', False):
                try:
                    if record.id in chan_curr_id:
                        result.append((record.id, "%s" % (string)))
                except Exception as e:
                    _logger.info(e)
                    _logger.info('Unable to name_get res.currency')
            else:
                result.append((record.id, "%s" % (string)))
        return result
