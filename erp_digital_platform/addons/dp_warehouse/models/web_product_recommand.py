from openerp import models, fields, api


class DPWebProductRecommand(models.Model):
    _name = "dp.web.product.list"
    _rec_name = "product_id"

    product_id = fields.Many2one("product.product", "Product")
    display_product_id = fields.Many2one("product.product", "Name", required=True)
    is_suggested = fields.Boolean("Is Suggested?")
    is_substitute = fields.Boolean("Is Substitute?")


class DPProductExtended(models.Model):
    _inherit = "product.product"

    web_product_list = fields.One2many("dp.web.product.list", "product_id", "Web Products")
