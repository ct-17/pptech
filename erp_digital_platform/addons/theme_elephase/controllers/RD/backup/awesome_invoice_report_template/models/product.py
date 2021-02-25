from openerp import models,fields,api

class ProductProduct(models.Model):
    _inherit = 'product.template'

    width = fields.Float("Widht(m)")
    height = fields.Float("Height(m)")
    depth = fields.Float("Depth(m)")