# -*- coding: utf-8 -*-

import base64

import werkzeug
import werkzeug.urls

from openerp import http, SUPERUSER_ID
from openerp.http import request
import time
from openerp.addons.website.models.website import slug
from openerp.addons.dp_website_sale.controllers.main import DPwebsite_sale
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import table_compute
from openerp.addons.website_sale.controllers.main import QueryURL
PPG = 20


class SortingWebsiteSale(DPwebsite_sale):

    @http.route()
    def shop(self, page=0, category=None, search='', **post):
        res=super(SortingWebsiteSale, self).shop(page, category, search, **post)
        prod_obj=request.registry['product.template']
        products=[]
        if post.get('sort_by'):
            cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

            domain = request.website.sale_product_domain()
            if search:
                for srch in search.split(" "):
                    domain += ['|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                        ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]
            if category:
                domain += [('public_categ_ids', 'child_of', int(category))]
            attrib_list = request.httprequest.args.getlist('attrib')
            attrib_values = [map(int,v.split("-")) for v in attrib_list if v]
            attrib_set = set([v[1] for v in attrib_values])

            if attrib_values:
                attrib = None
                ids = []
                for value in attrib_values:
                    if not attrib:
                        attrib = value[0]
                        ids.append(value[1])
                    elif value[0] == attrib:
                        ids.append(value[1])
                    else:
                        domain += [('attribute_line_ids.value_ids', 'in', ids)]
                        attrib = value[0]
                        ids = [value[1]]
                if attrib:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]

            keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list)

            if not context.get('pricelist'):
                pricelist = self.get_pricelist()
                context['pricelist'] = int(pricelist)
            else:
                pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)

            product_obj = pool.get('product.template')

            if request.session.get('login', None):
                # user is logged in will be able to see hidden to public products
                if category:
                    domain += [('sale_ok', '=', True), ('public_categ_ids', 'child_of', int(category)),
                              ('website_published', '=', True)]
                elif search:
                    domain += self._get_search_domain(search, category, attrib_values)
                    domain.extend([('website_published', '=', True)])
                else:
                    domain += [('sale_ok', '=', True), ('website_published', '=', True)]
                product_count = product_obj.search_count(request.cr, request.uid, domain, context=None)
            else:
                if category:
                    domain += [('sale_ok', '=', True), ('public_categ_ids', 'child_of', int(category)),
                              ('website_published', '=', True), ('hidden_to_public', '=', False)]
                elif search:
                    domain += self._get_search_domain(search, category, attrib_values)
                    domain.extend([('website_published', '=', True)])
                else:
                    domain += [('sale_ok', '=', True), ('website_published', '=', True),
                              ('hidden_to_public', '=', False)]
                product_count = product_obj.search_count(request.cr, request.uid, domain, context=None)

            url = "/shop"
            if category:
                url = "/shop/category/%s" % slug(category)
            if search:
                post["search"] = search

            # product_count = product_obj.search_count(cr, uid, domain, context=context)
            if search:
                post["search"] = search
            if category:
                category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
                url = "/shop/category/%s" % slug(category)
            if attrib_list:
                post['attrib'] = attrib_list
            pager = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
            if str(post['sort_by'])=='name_a_z':
                product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], order='name', context=context)
            elif str(post['sort_by'])=='name_z_a':
                product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], order='name desc', context=context)
            elif str(post['sort_by'])=='country_a_z':
                # this part requires dp_product_extend
                product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], order='country_name', context=context)
            elif str(post['sort_by'])=='country_z_a':
                # this part requires dp_product_extend
                product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], order='country_name desc', context=context)
            # elif str(post['sort_by'])=='price_l_h':
            #     product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], order='list_price', context=context)
            # elif str(post['sort_by'])=='price_h_l':
            #     product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], order='list_price desc', context=context)
            else:
                product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], order='website_published desc, website_sequence desc', context=context)
            products = product_obj.browse(cr, uid, product_ids, context=context)

            style_obj = pool['product.style']
            style_ids = style_obj.search(cr, uid, [], context=context)
            styles = style_obj.browse(cr, uid, style_ids, context=context)

            category_obj = pool['product.public.category']
            category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
            categs = category_obj.browse(cr, uid, category_ids, context=context)

            attributes_obj = request.registry['product.attribute']
            attributes_ids = attributes_obj.search(cr, uid, [], context=context)
            attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

            from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
            to_currency = pricelist.currency_id
            compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

            res.qcontext.update({
                        'products': products,
                        'bins': table_compute().process(products),
                        'sort_by':str(post['sort_by']),
                        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
