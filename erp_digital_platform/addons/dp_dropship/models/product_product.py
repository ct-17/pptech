from openerp import models, fields, api, SUPERUSER_ID
from openerp.exceptions import except_orm, Warning
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class DPDropshipProductProduct(models.Model):
    _inherit = 'product.product'

    _sql_constraints = [
        ('default_code_unique',
        'unique(default_code)',
        'Product Code must be Unique!')
    ]