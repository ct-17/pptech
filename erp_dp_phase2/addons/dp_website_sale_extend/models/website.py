from openerp import models, fields, api
from openerp import http
from openerp.addons.web.http import request
import logging
from openerp import SUPERUSER_ID

class DPwebsiteExtend(models.Model):
    _inherit = 'website'

    @api.cr_uid_ids_context
    def sale_get_order(self, cr, uid, ids, force_create=False, code=None, update_pricelist=None, context=None):
        res = super(DPwebsiteExtend, self).sale_get_order(cr, uid or 3, ids, force_create, code, update_pricelist, context)
        sale_order_obj = self.pool['sale.order']
        sale_order_id = request.session.get('sale_order_id')
        sale_order = None

        # Test validity of the sale_order_id
        if res != None:
            if res.state=='cancel':
                sale_order_id = None
                force_create = True
        # create so if needed
        if sale_order_id == None and (force_create or code):
            # TODO cache partner_id session
            partner = self.pool['res.users'].browse(cr, SUPERUSER_ID, uid, context=context).partner_id

            for w in self.browse(cr, uid, ids):
                values = {
                    'user_id': w.user_id.id,
                    'partner_id': partner.id,
                    'pricelist_id': partner.property_product_pricelist.id,
                    'section_id': self.pool.get('ir.model.data').get_object_reference(cr, uid, 'website',
                                                                                      'salesteam_website_sales')[1],
                }
                sale_order_id = sale_order_obj.create(cr, SUPERUSER_ID, values, context=context)
                values = sale_order_obj.onchange_partner_id(cr, SUPERUSER_ID, [], partner.id, context=context)['value']
                sale_order_obj.write(cr, SUPERUSER_ID, [sale_order_id], values, context=context)
                request.session['sale_order_id'] = sale_order_id
                sale_order = sale_order_obj.browse(cr, SUPERUSER_ID, sale_order_id, context=context)
                sale_order.dp_currency_id = partner.property_product_pricelist.currency_id
            return sale_order

        return res

