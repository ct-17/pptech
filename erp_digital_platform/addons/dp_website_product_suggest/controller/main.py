from openerp import http
from openerp import models, fields, api
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.http import request
from openerp.addons.website.models.website import slug
import werkzeug
import openerp
import re
import unicodedata
from openerp.osv import orm, osv, fields
from openerp.tools import html_escape as escape, ustr, image_resize_and_sharpen, image_save_for_web, image_resize_image
from openerp.tools.safe_eval import safe_eval
from openerp.addons.web.http import request


try:
    import slugify as slugify_lib
except ImportError:
    slugify_lib = None

class DPwebsite_product_suggest(website_sale):
    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        res = super(DPwebsite_product_suggest, self).product(product, category, search, **kwargs)
        current_suggest_product = product.product_variant_ids.suggest_product
        res.qcontext.update({'suggest_products': current_suggest_product})
        return res

def slugify(s, max_length=None):
    """ Transform a string to a slug that can be used in a url path.

    This method will first try to do the job with python-slugify if present.
    Otherwise it will process string by stripping leading and ending spaces,
    converting unicode chars to ascii, lowering all chars and replacing spaces
    and underscore with hyphen "-".

    :param s: str
    :param max_length: int
    :rtype: str
    """
    s = ustr(s)
    if slugify_lib:
        # There are 2 different libraries only python-slugify is supported
        try:
            return slugify_lib.slugify(s, max_length=max_length)
        except TypeError:
            pass
    uni = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub('[\W_]', ' ', uni).strip().lower()
    slug = re.sub('[-\s]+', '-', slug)

    return slug[:max_length]

def slug(value):
    if isinstance(value, orm.browse_record):
        # [(id, name)] = value.name_get()
        id, name = value.id, value.display_name
    else:
        # assume name_search result tuple
        id, name = value
    slugname = slugify(name or '').strip().strip('-')
    if not slugname:
        return str(id)
    return "%s-%d" % (slugname, id)