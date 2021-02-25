from openerp import models, fields, api
from datetime import datetime

class ProductProduct(models.Model):
    _inherit = 'product.template'

    dp_uom = fields.Many2many(comodel_name='product.uom')
    virtual_available = fields.Float(string='Forecast Quantity', compute='_compute_virtual_available')
    dp_minimum_qty = fields.Float("Minimum Quantity")
    dp_maximum_qty = fields.Float("Maximum Quantity")
    dp_allocated_qty = fields.Float("Sellable Quantity")
    percent_allocate = fields.Float('% ERP Available Sellable')
    publish_time = fields.Datetime('Publish Time')

    @api.model
    def publish_products(self):
        now = datetime.now()
        products = self.search([('website_published', '=', False),
                                ('publish_time', '<=', now.strftime('%Y-%m-%d %H:%M:%S'))])
        products.write({'website_published': True})

    @api.multi
    def _compute_virtual_available(self):
        slsa = self.env['sale.line.stock.allocation']
        for product in self:
            if isinstance(product.dp_allocated_qty, float):
                qty = slsa.search([('product_id', 'in', product.product_variant_ids.ids), ('state', 'not in', ('draft', 'done', 'cancel'))]).mapped(lambda x: x.product_qty)
                product.virtual_available = product.dp_allocated_qty - sum(qty)

    def default_description_sale(self):
        value = """
            <ul>
            <li>Volume: </li></br>
            <li>Alcohol: </li></br> 
            <li>Country of Origin: </li></br> 
            <li>Product Description: </li>
            </ul> 
        """
        return value

    description_sale = fields.Html(default=default_description_sale)

