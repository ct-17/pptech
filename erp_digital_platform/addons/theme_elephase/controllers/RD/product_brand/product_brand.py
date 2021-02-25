from openerp import models, fields, api


class ProductBrand(models.Model):
    _name = 'product.brand'

    name = fields.Char('Brand Name', required=True)
    description = fields.Text('Description', translate=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Select a partner for this brand if it exists',
        ondelete='restrict'
    )
    logo = fields.Binary('Logo File')
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_get_products_count',
    )

    @api.one
    @api.depends('product_ids')
    def _get_products_count(self):
        self.products_count = len(self.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        help='Select a brand for this product'
    )

    country_id = fields.Many2one('res.country', string='Country')
    
    @api.multi
    def name_get(self):
        res = super(ProductTemplate, self).name_get()
        res2 = []
        for name_tuple in res:
            product = self.browse(name_tuple[0])
            if not product.product_brand_id:
                res2.append(name_tuple)
                continue
            res2.append((
                name_tuple[0],
                u'{} ({})'.format(name_tuple[1], product.product_brand_id.name)
            ))
        return res2


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def name_get(self):
        res = super(ProductProduct, self).name_get()
        res2 = []
        for name_tuple in res:
            product = self.browse(name_tuple[0])
            if not product.product_brand_id:
                res2.append(name_tuple)
                continue
            res2.append((
                name_tuple[0],
                u'{} ({})'.format(name_tuple[1], product.product_brand_id.name)
            ))
        return res2
