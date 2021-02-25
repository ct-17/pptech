import logging, sys
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class DPWebsiteSale(models.Model):
    _inherit = 'sale.order'

    many_chandler = fields.One2many('sale.order.chandler', 'order_id')
    # estimated_arrival = fields.Date('Estimated Date of Arrival')
    # last_port = fields.Char('Last Port')
    # next_port = fields.Char('Next Port')
    # stay_duration = fields.Char('Stay Duration')
    vat = fields.Char('VAT')
    # street = fields.Char('Street')
    # street2 = fields.Char('Street2')
    sale_duplicate_id = fields.Many2one('sale.order', 'Duplicate From', default=None)

    @api.model
    def create(self, vals):
        return super(DPWebsiteSale, self).create(vals)

    @api.multi
    def write(self, vals):
        rtn = super(DPWebsiteSale, self).write(vals)
        if self._context.has_key('shop_payment_validate'):
            self.update_order_line_cost_price()
            self.get_last_selling_price()
        return rtn

    @api.multi
    def copy(self, default={}, context=None):
        default = dict(default or {})
        rtn = super(DPWebsiteSale, self).copy(default)
        if self._context.has_key('shop_payment_validate'):
            self.update_order_line_cost_price()
            self.get_last_selling_price()
        return rtn

    @api.model
    def update_order_line_cost_price(self):
        self.order_line.update_cost_price()

    @api.model
    def get_last_selling_price(self):
        if self.user_id.exists():
            lsp = self.env['chandler.last.selling.price']
            chan_partner_id = self.user_id.partner_id.id
            sm_partner_id = self.partner_id.id
            for line in self.order_line:
                try:
                    obj = lsp.search([('chan_partner_id', '=', chan_partner_id), ('sm_partner_id', '=', sm_partner_id), ('product_id', '=', line.product_id.id)])
                except Exception as e:
                    obj = lsp
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    _logger.error('unable to retrieve partner_id and/or product_id {sale}, {line}'.format(sale=str(self), line=str(line)))
                line.last_selling_price = 0.00
                line.currency_and_rate = "N/A"
                if obj.exists():
                    line.last_selling_price = obj.last_selling_price
                    line.currency_and_rate = obj.currency_and_rate


class DPWebsiteCheckboxSale(models.Model):
    _name = 'sale.order.chandler'

    chandler = fields.Many2one('dp.chandler.temp', 'Preferred Chandler')
    seq = fields.Integer('Sequence')
    active = fields.Boolean('Active')
    order_id = fields.Many2one('sale.order')
