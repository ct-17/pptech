from openerp import models, fields, api
from openerp.tools.float_utils import float_round
from openerp.tools.translate import _
from openerp.exceptions import except_orm
import logging
_logger = logging.getLogger(__name__)
import openerp.addons.decimal_precision as dp


class DPMarkupOrderLine(models.Model):
    _inherit = "sale.order.line"

    mark_up_amount = fields.Float("Mark-up ($)", default=0.0, digits=dp.get_precision('Product Price'))
    mark_up_percent = fields.Float("Mark-up (%)", default=0.0, digits=dp.get_precision('Product Price'))
    # actual = line mark up + global markup/num of line
    actual_markup = fields.Float("Whole Sale Mark-up on Line", default=0.0, store=True, compute='_compute_actual_markup')
    mark_up_global_amount = fields.Float("Global Mark-up on Line", default=0.0)

    @api.onchange('mark_up_percent', 'mark_up_amount', 'price_unit')
    def _onchange_markup_percent_amount_price_unit(self):
        context = self._context
        if context.get('markup_amount', False):
            self._get_price_unit()
            self._get_actual_markup()
            self._get_mark_up_percent()
        if context.get('markup_percent', False):
            self.mark_up_amount = self.mark_up_percent / 100 * self.purchase_price
            self._get_actual_markup()
            self._get_price_unit()
        if context.get('price_unit', False):
            self.mark_up_amount = self.price_unit - self.mark_up_global_amount - self.purchase_price
            self._get_mark_up_percent()

    # @api.onchange('mark_up_percent')
    # def _onchange_markup_percent(self):
    #     if isinstance(self.mark_up_percent, float):
    #         self._get_mark_up_value()
    #
    # @api.onchange('mark_up_amount')
    # def _onchange_mark_up_amount(self):
    #     if isinstance(self.mark_up_amount, float):
    #         self._get_mark_up_value()
    #
    # @api.onchange('price_unit')
    # def _onchange_price_unit(self):
    #     if isinstance(self.price_unit, float):
    #         self.with_context(price_unit=True)._get_mark_up_value()
    #         # if self._context.get('from_ui', False):
    #         #     self.write({'price_unit': self._origin.price_unit})
    #         #     raise except_orm(_(''), ('Change Unit Price using Mark-up ($/%)'))
    #
    # @api.model
    # def _get_mark_up_value(self):
    #     context = self.env.context
    #     if context.get('markup_percent', False):
    #         self.mark_up_amount = self.mark_up_percent / 100 * self.purchase_price
    #         self._get_actual_markup()
    #         self._get_price_unit()
    #     elif context.get('markup_amount', False):
    #         self._get_price_unit()
    #         self._get_actual_markup()
    #         self._get_mark_up_percent()
    #     elif context.get('price_unit', False):
    #         self.mark_up_amount = self.price_unit - self.mark_up_global_amount - self.purchase_price
    #         self._get_mark_up_percent()

    @api.model
    def _get_mark_up_percent(self):
        if self.purchase_price != 0:
            self.mark_up_percent = 100 * self.mark_up_amount / self.purchase_price

    @api.model
    def _get_price_unit(self):
        self.price_unit = self.mark_up_amount + self.purchase_price
        # self.price_unit = self.mark_up_global_amount + self.mark_up_amount + self.purchase_price

    @api.model
    def _get_actual_markup(self):
        self.actual_markup = (self.mark_up_global_amount + self.mark_up_amount) * self.product_uom_qty

    @api.depends('mark_up_global_amount', 'mark_up_amount')
    @api.model
    def _compute_actual_markup(self):
        for line in self:
            line.actual_markup = (line.mark_up_global_amount + line.mark_up_amount) * line.product_uom_qty

