from openerp import models, fields, api

class ProductTemplate(models.Model):
    _inherit = ["product.template"]

    short_description = fields.Html('Short Description')