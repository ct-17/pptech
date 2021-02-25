from openerp import models, fields, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _
import logging, sys
_logger = logging.getLogger(__name__)


class DPSaleOrderLineStockAllocation(models.Model):
    _inherit = "sale.order.line"

    stock_allocation_id = fields.Many2one('sale.line.stock.allocation', 'Stock Allocation', copy=False)

    # @api.model
    # def create(self, vals):
    #     res = super(DPSaleOrderLineStockAllocation, self).create(vals)
    #     return res
    #
    # @api.multi
    # def write(self, vals):
    #     res = super(DPSaleOrderLineStockAllocation, self).write(vals)
    #     for line in self:
    #         self.set_stock_alloc_state(line, vals)
    #     return
    #
    # @api.multi
    # def unlink(self):
    #     for line in self:
    #         line.with_context({'unlink': True}).set_stock_alloc_state(line)
    #     res = super(DPSaleOrderLineStockAllocation, self).unlink()
    #     return res
    #
    # @api.model
    # def set_stock_alloc_state(self, line, vals={}):
    #     try:
    #         """
    #         order line state
    #         [('cancel', 'Cancelled'), ('draft', 'Draft'), ('bid_received', 'Quote Received'), ('confirmed', 'Confirmed'),
    #          ('exception', 'Exception'), ('done', 'Done')],
    #         """
    #         if vals.get('state', False) == 'confirmed' or line.state == 'confirmed':
    #             line.stock_allocation_id.state = 'done'
    #         if vals.get('state', False) == 'cancel' or line.state in ('cancel') or line.order_id.expire_quote_state == 'expired' or self._context.get('unlink', False) or self._context.get('bid_cancel', False):
    #             if not self._context.get('unlink', False) or self._context.get('bid_cancel', False):
    #                 if all(state == 'cancel' for state in line.stock_allocation_id.order_line.mapped(lambda x: x.state)):
    #                     line.stock_allocation_id.state = 'cancel'
    #             else:
    #                 if len(line.stock_allocation_id.order_line.filtered(lambda x: x.id != line.id).mapped(lambda y: y.state)) > 0:
    #                     if all(state == 'cancel' for state in line.stock_allocation_id.order_line.filtered(lambda x: x.id != line.id).mapped(lambda y: y.state)):
    #                         line.stock_allocation_id.state = 'cancel'
    #                 else:
    #                     line.stock_allocation_id.state = 'cancel'
    #         if line.order_id.state == 'draft' and line.stock_allocation_id.exists():
    #             line.stock_allocation_id.state = 'draft'
    #
    #     except TypeError as te:
    #         """
    #         most likely due to deleting sale order line
    #         """
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         _logger.error('Exception Type: ' + str(te))
    #         _logger.error('Exception Type: ' + str(exc_type))
    #         _logger.error('Exception Error Description: ' + str(exc_obj))
    #         _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
    #         _logger.error('unable to set_stock_alloc_state!')
    #     except Exception as e:
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         _logger.error('Exception Type: ' + str(e))
    #         _logger.error('Exception Type: ' + str(exc_type))
    #         _logger.error('Exception Error Description: ' + str(exc_obj))
    #         _logger.error(
    #             'Line Numnber: ' + str(exc_tb.tb_lineno) + 'Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
    #         _logger.error('unable to set_stock_alloc_state!')