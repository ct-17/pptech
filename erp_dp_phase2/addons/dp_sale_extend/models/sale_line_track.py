# __author__ = 'BinhTT'
from openerp import models, fields, api

class DPOrderLineExtendTrack(models.Model):
    _name = 'sale.line.track'

    order_line = fields.Many2one('sale.order.line')
    is_done = fields.Boolean(default=False)
    product_id = fields.Many2one('product.product', 'Product')
    item_type_product = fields.Selection([('foc', 'FOC')])
    product_uom_qty = fields.Integer()
    product_uom = fields.Many2one('product.uom')
    price_unit = fields.Float()
    order_id = fields.Many2one('sale.order')
    discount = fields.Float()
    price_subtotal = fields.Float()

