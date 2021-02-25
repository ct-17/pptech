# -*- coding: utf-8 -*-
import logging, json
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
import sys
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


class DPWebsiteHTTPController(http.Controller):

    @http.route('/dropdown_list/get_public_category', type="json",  auth="public")
    def _get_public_category(self, **kwargs):
        if request.session.get('uid', False):
            json_rtn = json.dumps({'dropdown_select': [obj.name for obj in request.env['product.public.category'].sudo().search([], order='name')]})
        else:
            json_rtn = json.dumps({'dropdown_select': [obj.name for obj in request.env['product.public.category'].sudo().search([('hidden_to_public', '=', False)], order='name')]})
        return json_rtn

    @http.route('/customize_has_groups', type="json", auth="public")
    def customize_has_groups(self):
        user = request.env['res.users'].browse(request.env.uid)
        public_user = http.request.env['res.users'].sudo().search([('id', '=', 3), ('active', '=', False)])  # Public user default ID
        if user.has_group('dp_common.group_chandler') or user.id == public_user.id:
            return True
        else:
            return False

    @http.route(['/aboutus'], type='http', auth='public', website=True)
    def _aboutus(self):
        return request.website.render('dp_website.aboutus')

    @http.route(['/gettingstarted'], type='http', auth='public', website=True)
    def _gettingstarted(self):
        return request.website.render('dp_website.gettingstart')

    @http.route(['/termsandconditions'], type='http', auth='public', website=True)
    def _termsandconditions(self):
        return request.website.render('dp_website.temrsandconditions')

    @http.route(['/privacypolicy'], type='http', auth='public', website=True)
    def _privacypolicy(self):
        return request.website.render('dp_website.privacypolicy')

    @http.route(['/contactus'], type='http', auth='public', website=True)
    def _contactus(self):
        return request.website.render('dp_website.contactus')