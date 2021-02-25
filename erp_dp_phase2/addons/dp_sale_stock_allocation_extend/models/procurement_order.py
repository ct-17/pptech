from openerp import models, api


class DPProcurementOrderStockAlloc(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def run(self,  autocommit=False):
        res = super(DPProcurementOrderStockAlloc, self).run(autocommit)
        pur_obj = self.mapped('purchase_id')
        sale_obj = self.mapped(lambda x:x.sale_line_id.mapped(lambda y:y.order_id))
        sale_obj.write({'purchase_id': pur_obj.id})
        for line in sale_obj.order_line:
            line.set_stock_alloc_state(line)
        return res