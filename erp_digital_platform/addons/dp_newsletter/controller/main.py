from openerp import models, fields, api
from openerp import http
import logging
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website.controllers.main import Website

from openerp import SUPERUSER_ID
from openerp.http import request, Response

_logger = logging.getLogger(__name__)

class NewsWebsiteSale(website_sale):

    @http.route(['/write_newsletter_member'],  type="json",  auth="public")
    def write_newsletter_member(self, **post):
        member = request.env['newsletter.member']
        if post and post.get('name', False):
            member.sudo().create(post)
            return True
        return False

    @http.route('/goodbye', type='http', auth='public', website=True)
    def goodbye_user(self, *args, **kw):
        result = request.render('dp_newsletter.goodbye_user')
        Response(result, mimetype='text/html')
        result.set_cookie('access', 'false', max_age=90 * 24 * 60 * 60)
        return result

class NewsWebsite(Website):
    @http.route('/', type='http', auth="none", website=True)
    def index(self, **kw):
        res = super(NewsWebsite, self).index(**kw)
        if request.httprequest and request.httprequest.cookies and 'access' in request.httprequest.cookies:
            return request.render('dp_newsletter.goodbye_user')
        return res