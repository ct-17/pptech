import logging, sys
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class DPWebsiteSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def update_cost_price(self):
        pricelist_obj = self.mapped(lambda x: x.order_id.pricelist_id)
        for line in self:
            prices = pricelist_obj.price_get(prod_id=line.product_id.id, qty=line.product_uom_qty, partner=line.order_id.user_id.id).values()
            try:
                assert len(prices) == 1
                prices = prices[0]
            except AssertionError:
                prices = None
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('update_cost_price Problems, only 1 active pricelist version per product is expected')

            if prices is not None:
                line.write({'purchase_price': prices,
                            'base_purchase_price': prices})
