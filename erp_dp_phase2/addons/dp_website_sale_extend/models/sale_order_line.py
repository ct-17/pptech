import logging, sys
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class DPWebsiteSaleExtendSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    line_amend_state = fields.Selection([('new', 'New'), ('decrease','Decrease'), ('increase', 'Increase')], default="new")

    @api.multi
    def write(self, vals):
        if vals.get('product_uom_qty', False) and (self._context.get('new_cancel_workflow', False) \
                                            or self._context.get('from_myenquiry', False)):
            self._new_cancel_workflow(source='write', vals=vals)
        # if self._context.get('overwrite_write_vals', False):
        #     vals = {}
        res = super(DPWebsiteSaleExtendSaleOrderLine, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        if self._context.get('from_myenquiry', False):
            self._new_cancel_workflow(source='unlink')
        res = super(DPWebsiteSaleExtendSaleOrderLine, self).unlink()
        return res

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        return super(DPWebsiteSaleExtendSaleOrderLine, self).copy(default=default)

    @api.multi
    def _new_cancel_workflow(self, source=None, vals={}):
        if source == 'unlink':
            for line in self:
                new_line_obj = line.copy()
                new_line_obj.with_context({'new_cancel_workflow': True}).write({
                    'state': 'cancel',
                    #'price_unit': 0,
                })
        if source == 'write':
            for line in self:
                if vals.get('product_uom_qty', False) and line.state != 'cancel':
                    if vals.get('product_uom_qty') <  self.product_uom_qty:
                        diff = self.product_uom_qty - vals.get('product_uom_qty')
                        self.line_amend_state = 'decrease'
                        # check for existing cancelled product
                        existing_cancelled_line = line.order_id.cancel_order_line.filtered(lambda x: x.product_id.id == line.product_id.id and x.state == 'cancel')
                        if existing_cancelled_line.exists():
                            if len(existing_cancelled_line) == 1:
                                existing_cancelled_line.with_context({'new_cancel_workflow': False,
                                                                      'overwrite_write_vals': True}).write({
                                    'product_uom_qty': existing_cancelled_line.product_uom_qty+diff,
                                    'product_uos_qty': existing_cancelled_line.product_uos_qty+diff,
                                })
                            else:
                                # incase existing cancelled line has more than 1 results
                                existing_cancelled_line.with_context({'new_cancel_workflow': False,
                                                                      'overwrite_write_vals': True})[0].write({
                                    'product_uom_qty': existing_cancelled_line.product_uom_qty+diff,
                                    'product_uos_qty': existing_cancelled_line.product_uos_qty+diff,
                                })
                            existing_cancelled_line._cr.commit()
                        else:
                            new_line_obj = line.copy()
                            new_line_obj.with_context({'new_cancel_workflow': False}).write({
                                'state': 'cancel',
                                #'price_unit': 0,
                                'product_uom_qty': diff,
                                'product_uos_qty': diff,
                            })
                    if vals.get('product_uom_qty') >  self.product_uom_qty:
                        self.line_amend_state = 'increase'


    @api.multi
    def convert_self_to_list_of_dict(self):
        vals = self.read(self._fields)
        return vals
