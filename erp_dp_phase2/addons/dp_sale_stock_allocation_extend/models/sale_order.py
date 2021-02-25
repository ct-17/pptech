from openerp import models, fields, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class DPSaleOrderStockAllocation(models.Model):
    _inherit = "sale.order"

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')

    @api.model
    def create(self, vals):
        res = super(DPSaleOrderStockAllocation, self).create(vals)
        return res