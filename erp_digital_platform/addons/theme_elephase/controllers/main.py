import werkzeug
import json

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers.main import website_sale

PPG = 18 # Products Per Page
PPR = 3  # Products Per Row

class table_compute(object):
    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx+x>=PPR:
                    res = False
                    break
                row = self.table.setdefault(posy+y, {})
                if row.setdefault(posx+x) is not None:
                    res = False
                    break
            for x in range(PPR):
                self.table[posy+y].setdefault(x, None)
        return res

    def process(self, products):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        for p in products:
            x = min(max(p.website_size_x, 1), PPR)
            y = min(max(p.website_size_y, 1), PPR)
            if index>=PPG:
                x = y = 1

            pos = minpos
            while not self._check_place(pos%PPR, pos/PPR, x, y):
                pos += 1
            # if 21st products (index 20) and the last line is full (PPR products in it), break
            # (pos + 1.0) / PPR is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= PPG and ((pos + 1.0) / PPR) > maxy:
                break

            if x==1 and y==1:   # simple heuristic for CPU optimization
                minpos = pos/PPR

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos/PPR)+y2][(pos%PPR)+x2] = False
            self.table[pos/PPR][pos%PPR] = {
                'product': p, 'x':x, 'y': y,
                'class': " ".join(map(lambda x: x.html_class or '', p.website_style_ids))
            }
            if index<=PPG:
                maxy=max(maxy,y+(pos/PPR))
            index += 1

        # Format table according to HTML needs
        rows = self.table.items()
        rows.sort()
        rows = map(lambda x: x[1], rows)
        for col in range(len(rows)):
            cols = rows[col].items()
            cols.sort()
            x += len(cols)
            rows[col] = [c for c in map(lambda x: x[1], cols) if c != False]

        return rows
        # TODO keep with input type hidden
        
class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        for k,v in self.args.items():
            kw.setdefault(k,v)
        l = []
        for k,v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k,i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k,v)]))
        if l:
            path += '?' + '&'.join(l)
        return path
    
class website_sale(website_sale):

    @http.route(
        ['/shop',
         '/shop/page/<int:page>',
         '/shop/category/<model("product.public.category"):category>',
         '/shop/category/<model("product.public.category"):category>/'
         'page/<int:page>'],
        type='http', auth="public", website=True)
    def Shop(self, page=0, category=None, search='', **post):
        parent_category_ids = []
        if category:
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id
        response = super(website_sale, self).shop(page=page, category=category, search=search, **post)
        response.qcontext['parent_category_ids'] = parent_category_ids
        return response

#     @http.route([
#         '/shop',
#         '/shop/page/<int:page>',
#         '/shop/category/<model("product.public.category"):category>',
#         '/shop/category/<model("product.public.category"):category>/page/<int:page>'
#     ], type='http', auth="public", website=True)
#     def shop(self, page=0, category=None, search='', **post):
#         cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
# 
#         attrib_list = request.httprequest.args.getlist('attrib')
#         attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
#         attrib_set = set([v[1] for v in attrib_values])
# 
#         domain = self._get_search_domain(search, category, attrib_values)
# 
#         keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list)
# 
#         if not context.get('pricelist'):
#             pricelist = self.get_pricelist()
#             context['pricelist'] = int(pricelist)
#         else:
#             pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)
# 
#         product_obj = pool.get('product.template')
# 
#         url = "/shop"
#         product_count = product_obj.search_count(cr, uid, domain, context=context)
#         if search:
#             post["search"] = search
#         if category:
#             category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
#             url = "/shop/category/%s" % slug(category)
#         if attrib_list:
#             post['attrib'] = attrib_list
#         pager = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
#         product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], order=self._get_search_order(post), context=context)
#         products = product_obj.browse(cr, uid, product_ids, context=context)
# 
#         style_obj = pool['product.style']
#         style_ids = style_obj.search(cr, uid, [], context=context)
#         styles = style_obj.browse(cr, uid, style_ids, context=context)
# 
#         category_obj = pool['product.public.category']
#         category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
#         categs = category_obj.browse(cr, uid, category_ids, context=context)
# 
#         attributes_obj = request.registry['product.attribute']
#         attributes_ids = attributes_obj.search(cr, uid, [], context=context)
#         attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)
# 
#         from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
#         to_currency = pricelist.currency_id
#         compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)
# 
#         values = {
#             'search': search,
#             'category': category,
#             'attrib_values': attrib_values,
#             'attrib_set': attrib_set,
#             'pager': pager,
#             'pricelist': pricelist,
#             'products': products,
#             'bins': table_compute().process(products),
#             'rows': PPR,
#             'styles': styles,
#             'categories': categs,
#             'attributes': attributes,
#             'compute_currency': compute_currency,
#             'keep': keep,
#             'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
#             'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib',i) for i in attribs]),
#         }
#         return request.website.render("website_sale.products", values)
