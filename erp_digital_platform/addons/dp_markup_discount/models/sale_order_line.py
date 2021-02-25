from datetime import datetime
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class DPMarkupDiscountSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.depends('discount', 'price_unit', 'product_uom_qty')
    def _compute_all_price(self):
        for r in self:
            r.discount_amount_line = (r.price_unit+r.mark_up_global_amount) * r.product_uom_qty * r.discount / 100
            r.tax_amount = sum([tax['amount'] for tax in r.tax_id.compute_all(r.price_subtotal, 1,
                                                                              r.order_id.partner_id)['taxes']])