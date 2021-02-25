from datetime import datetime
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class DPMarkupSaleOrder(models.Model):
    _inherit = "sale.order"

    # markup_amount = fields.Float("Mark-up Amount")
    global_markup_type = fields.Selection([('amount', 'Fixed Amount'), ('percent', 'Percentage')],
                                          'Whole Bill Mark-up Type', readonly=True)
    global_markup_amount = fields.Float('Whole Bill Mark-up', readonly=True)
    global_markup_percent = fields.Integer('Whole Bill Mark-up (%)', readonly=True)
    is_global_markup = fields.Boolean()
    markup_amount = fields.Float("Whole Bill Mark-up Amount", compute='_compute_markup_amount', readonly=True)

    @api.depends('order_line')
    def _compute_markup_amount(self):
        for rec in self:
            rec.markup_amount = sum([line.mark_up_global_amount*line.product_uom_qty for line in rec.order_line])


