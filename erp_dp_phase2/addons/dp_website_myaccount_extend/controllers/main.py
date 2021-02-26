import logging, json
from openerp import http
from openerp.http import request


class website_myaccount_extend(http.Controller):

    @http.route('/myaccount/get_vessel_type', type="json", method=['POST', 'GET'], auth="public")
    def get_corresponding_vessel_type(self, **kwargs):
        vess_obj = request.env['vessel.name']
        vtype = ''
        if kwargs.get('value', {}).get('vessel', False):
            vess_obj = request.env['vessel.name'].sudo().search([('name', '=', kwargs.get('value', {}).get('vessel', False))])
            try:
                vtype = vess_obj.type.name
            except AttributeError:
                vtype = ''
        rtn_dict = {"vessel_type": vtype}
        return json.dumps(rtn_dict)

    @http.route(['/mywishlist'], type='http', auth='user', website=True)
    def get_wish_list(self, **kwargs):
        product_obj = request.env['wish.list']

        values = {
            'product_name': product_obj.name or '',
            'contact': product_obj.contact or '',
            'crNum': product_obj.crNum or '',
            'active': product_obj.active or ''
        }

        return request.website.render("dp_website_myaccount_extend.wish_list", values)