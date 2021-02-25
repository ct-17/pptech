from openerp import models, api, fields
from dateutil.relativedelta import relativedelta
from datetime import datetime as dt
import logging
_logger = logging.getLogger(__name__)


class StockLevelIndicatorConfig(models.Model):
    _name = "indicator.config"

    product_template_id = fields.Many2one('product.template', 'Product')
    img = fields.Binary('Image File')
    lower = fields.Float('Lower Limit %', default=0)
    upper = fields.Float('Upper Limit %', default=0)
    name = fields.Char('Name')