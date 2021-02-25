from openerp import models, fields, api, SUPERUSER_ID
from openerp.exceptions import except_orm, Warning
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class DPDropshipProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def set_dropship_true(self):
        return self.env['stock.location.route'].search([('name', 'in', ('Buy', 'Drop Shipping'))]).ids

    route_ids = fields.Many2many('stock.location.route', 'stock_route_product', 'product_id', 'route_id', 'Routes',
                                  default=set_dropship_true,
                                  copy=True,
                                  domain="[('product_selectable', '=', True)]",
                                  help="Depending on the modules installed, this will allow you to define the route of the product: whether it will be bought, manufactured, MTO/MTS,...")
