# __author__ = 'BinhTT'

from openerp import models, api, fields

class DPPriceProduct(models.Model):
    _inherit = 'product.template'

    @api.multi
    def get_price(self):
        for r in self:
            pricelist = self.env.context.get('pricelist', False)
            if not pricelist:
                pricelist = self.env.user.sudo().partner_id.property_product_pricelist
            else:
                pricelist = self.env['product.pricelist'].sudo().browse(pricelist)
            price = pricelist.sudo().price_get(r.product_variant_ids.id, 1.0, self.env.user.partner_id)
            r.pricelist_price = price[pricelist.id] or 0.0

    pricelist_price = fields.Float(compute="get_price")