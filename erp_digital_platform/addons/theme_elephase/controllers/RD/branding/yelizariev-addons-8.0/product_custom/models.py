from openerp import api, models, fields, SUPERUSER_ID

class product_template(models.Model):
    _inherit = 'product.template'

    customer_lead_time = fields.Integer('Customer Lead Time', default=7)
    promotion_date = fields.Date('Show as Promotion until')
    price_shop = fields.Float('Price shop')
    price_special = fields.Float('Special Price')
    price_platform1 = fields.Float('Price Platform 1')
    price_platform2 = fields.Float('Price Platform 2')

    description_shop = fields.Html('Description For Shop')
    description_shop_short = fields.Html('Short Description For Shop')
    description_platform1 = fields.Html('Description For Platform 1')
    description_platform2 = fields.Html('Description For Platform 2')
