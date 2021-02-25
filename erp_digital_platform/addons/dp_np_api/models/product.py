# __author__ = 'BinhTT'
from openerp import models, fields, api
import logging


class DPNPproductTemplate(models.Model):
    _inherit = 'product.template'
    np_product_id = fields.Integer()