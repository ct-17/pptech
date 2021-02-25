from openerp import models, fields, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _
import logging, sys
_logger = logging.getLogger(__name__)


class DPSaleOrderLineStockAllocation(models.Model):
    _inherit = "sale.order.line"

    stock_allocation_id = fields.Many2one('sale.line.stock.allocation', 'Stock Allocation', copy=False)

    @api.model
    def create(self, vals):
        res = super(DPSaleOrderLineStockAllocation, self).create(vals)
        if self._context.get('params', {}).get('action', False) not in (self.env.ref('sale.action_quotations').id, \
                                                                     self.env.ref('sale.menu_sale_order').id, \
                                                                     self.env.ref('dp_sale.dp_shipmaster_action_menu').id):
            # ensure create sale order line comes from website and not quotation/sales order/shipmaster enquiry menu
            origin_sale_order_products = res.order_id.sale_duplicate_id.order_line.mapped(lambda x:x.product_id)
            if res.product_id in origin_sale_order_products:
                self._add_to_existing_stock_alloc(res, res.order_id.sale_duplicate_id)
            else:
                self._create_new_stock_alloc(res)
        return res

    @api.model
    def _add_to_existing_stock_alloc(self, sol, origin_so):
        # if sale.line.stock.allocation does not exist
        try:
            for line in origin_so.order_line:
                if line.product_id.id == sol.product_id.id:
                    sol.stock_allocation_id = line.stock_allocation_id.id
                    sol.stock_allocation_id.product_qty = max(sol.product_uom_qty, line.product_uom_qty)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('dp_sale_stock_allocation_extend.sale_order_line _add_to_existing_stock_alloc exception: {e}'.format(e=e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))

    @api.model
    def _create_new_stock_alloc(self, sol):
        # if sale.line.stock.allocation does not exist
        try:
            stock_alloc_obj = self.env['sale.line.stock.allocation']
            sao = stock_alloc_obj.create({'state': 'ongoing',
                                          'name': sol.product_id.name_template,
                                          'product_id': sol.product_id.id,
                                          'product_qty': sol.product_uom_qty
                                          })
            sol.stock_allocation_id = sao.id
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('dp_sale_stock_allocation_extend.sale_order_line _create_new_stock_alloc exception: {e}'.format(e=e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))

    @api.model
    def _update_stock_alloc_qty(self, sol):
        # if sale.line.stock.allocation does not exist
        try:
            alloc_obj = sol.stock_allocation_id
            alloc_obj.product_qty = max(alloc_obj.order_line.mapped(lambda x: x.product_uom_qty))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('dp_sale_stock_allocation_extend.sale_order_line _update_stock_alloc_qty exception: {e}'.format(e=e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))

    @api.multi
    def write(self, vals):
        res = super(DPSaleOrderLineStockAllocation, self).write(vals)
        for line in self:
            line._update_stock_alloc_qty(line)
            self.set_stock_alloc_state(line, vals)
        return

    @api.multi
    def unlink(self):
        for line in self:
            line.with_context({'unlink': True}).set_stock_alloc_state(line)
            stock_alloc_line = self.stock_allocation_id.order_line.mapped(lambda x:x.id)
            if self.id in stock_alloc_line and len(stock_alloc_line) == 1:
                line.unlink_stock_alloc()
        res = super(DPSaleOrderLineStockAllocation, self).unlink()
        return res

    @api.model
    def unlink_stock_alloc(self):
        self.stock_allocation_id.sudo().unlink()

    @api.model
    def set_stock_alloc_state(self, line, vals={}):
        #   ___                               _ _               _                    _
        #  / _ \__   _____ _ ____      ___ __(_) |_ ___   _ __ | |__   __ _ ___  ___/ |
        # | | | \ \ / / _ \ '__\ \ /\ / / '__| | __/ _ \ | '_ \| '_ \ / _` / __|/ _ \ |
        # | |_| |\ V /  __/ |   \ V  V /| |  | | ||  __/ | |_) | | | | (_| \__ \  __/ |
        #  \___/  \_/ \___|_|    \_/\_/ |_|  |_|\__\___| | .__/|_| |_|\__,_|___/\___|_|
        #                                                |_|
        try:
            """
            order line state
            [('cancel', 'Cancelled'), ('draft', 'Draft'), ('bid_received', 'Quote Received'), ('confirmed', 'Confirmed'),
             ('exception', 'Exception'), ('done', 'Done')],
            """
            if line.order_id.state in ('chandler_draft', 'sent', 'negotiation', 'shipmaster_confirm', 'progress'):
                if not line.order_id.purchase_id.exists():
                    line.stock_allocation_id.state = 'ongoing'
                else:
                    if line.order_id.purchase_id.state == 'approved':
                        line.stock_allocation_id.state = 'done'
            if vals.get('state', False) == 'cancel' or line.state in ('cancel') or \
                    line.order_id.expire_quote_state == 'expired' or self._context.get('unlink', False) or \
                    self._context.get('bid_cancel', False):
                if not self._context.get('unlink', False) or self._context.get('bid_cancel', False):
                    if all(state == 'cancel' for state in line.stock_allocation_id.order_line.mapped(lambda x: x.state)):
                        line.stock_allocation_id.state = 'cancel'
                else:
                    if len(line.stock_allocation_id.order_line.filtered(lambda x: x.id != line.id).mapped(
                            lambda y: y.state)) > 0:
                        if all(state == 'cancel' for state in
                               line.stock_allocation_id.order_line.filtered(lambda x: x.id != line.id).mapped(
                                       lambda y: y.state)):
                            line.stock_allocation_id.state = 'cancel'
                    else:
                        line.stock_allocation_id.state = 'cancel'
            if line.order_id.state == 'draft' and line.stock_allocation_id.exists():
                line.stock_allocation_id.state = 'draft'
        except TypeError as te:
            """
            most likely due to deleting sale order line
            """
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(te))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error(
                'Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('unable to set_stock_alloc_state!')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.warning('If stock_allocation_id does not exist, this warning can be ignored')
            _logger.warning('line: ' + str(line) + ' line.stock_allocation_id: ' + str(line.stock_allocation_id))
            _logger.error(
                'Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('unable to set_stock_alloc_state!')