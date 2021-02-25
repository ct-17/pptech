# __author__ = 'BinhTT'
from openerp import tools, http, SUPERUSER_ID
from openerp.http import request
import logging
from openerp.addons.website_sale.controllers.main import website_sale
_logger = logging.getLogger(__name__)

class DPPricelist_website(website_sale):


    @http.route([
            '/shop',
            '/shop/page/<int:page>',
            '/shop/category/<model("product.public.category"):category>',
            '/shop/category/<model("product.public.category"):category>/page/<int:page>'
        ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        res = super(DPPricelist_website, self).shop(page, category, search, **post)
        return res

    def get_pricelist(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        sale_order = context.get('sale_order')
        if sale_order:
            pricelist = sale_order.pricelist_id
        if not sale_order or request.env.user.has_group('dp_common.group_chandler_admin'):
            partner = pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).partner_id
            pricelist = partner.property_product_pricelist
        if not pricelist:
            _logger.error('Fail to find pricelist for partner "%s" (id %s)', partner.name, partner.id)
        return pricelist

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        res = super(DPPricelist_website, self).cart_update_json(product_id, line_id, add_qty, set_qty, display)

        order = request.website.sale_get_order(force_create=1)

        res.update({'website_sale.total' : request.website._render("website_sale.total", {'order': order})})
        return res