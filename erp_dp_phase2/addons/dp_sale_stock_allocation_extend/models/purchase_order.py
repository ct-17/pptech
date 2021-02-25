from openerp import models, api


class DPPurchaseOrderStockAlloc(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def write(self, vals):
        res = super(DPPurchaseOrderStockAlloc, self).write(vals)
        if vals.get('state', False):
            if vals.get('state') == 'approved':
                for line in self.so_id.order_line:
                    line.set_stock_alloc_state(line)
        if self.state == 'approved':
            for line in self.so_id.order_line:
                line.set_stock_alloc_state(line)
        return res