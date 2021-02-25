# -*- coding: utf-8 -*-
import werkzeug
import openerp
from openerp import addons
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website.models.website import slug, unslug
from openerp.tools.translate import _
import openerp.http as http
from openerp.http import Controller, route, request, Response
from openerp.addons.auth_signup.res_users import SignupError
from openerp.addons.auth_signup.res_users import res_users      # Registration type return

from openerp.addons.website_sale.controllers.main import website_sale
import werkzeug.urls
import werkzeug.wrappers
import openerp.addons.auth_signup.controllers.main as main  # add library for Registration page



class OdooWebsiteMarketplace(http.Controller):

    # Seller Page
    @http.route(['/sellers/<seller_id>'], type='http', auth="public", website=True)
    def partners_detail(self, seller_id, **post):
        _, seller_id = unslug(seller_id)
        if seller_id:
            partner = request.registry['res.partner'].browse(request.cr, SUPERUSER_ID, seller_id, context=request.context)
            is_website_publisher = request.registry['res.users'].has_group(request.cr, request.uid, 'base.group_website_publisher')
            if partner.exists() and (partner.website_published or is_website_publisher):
                values = {
                    'main_object': partner,
                    'partner': partner,
                    'edit_page': False
                }
                return request.website.render("odoo_website_marketplace.seller_page", values)
        return request.not_found()



    # Seller Page
    @http.route(['/marketplace'], type='http', auth='user', website=True)
    def marketplace(self, redirect=None, **post):

        user_brw = request.registry['res.users'].browse(request.cr, SUPERUSER_ID, request.uid, context=request.context).groups_id
        group_id = [a.id for a in user_brw]
        seller_pending_user = user_brw.env.ref('odoo_website_marketplace.group_market_place_pending_seller')
        seller_account_user = user_brw.env.ref('odoo_website_marketplace.group_market_place_seller')
        seller_manager_user = user_brw.env.ref('odoo_website_marketplace.group_market_place_manager')
        menu_brw = False
        if seller_pending_user.id in group_id:
            menu_id = request.registry['ir.ui.menu'].search(request.cr, SUPERUSER_ID, [('name', '=','Seller Dashboard')], context=request.context)
            menu_brw = request.registry['ir.ui.menu'].browse(request.cr, SUPERUSER_ID, menu_id, context=request.context)

        if seller_account_user.id in group_id:
            menu_id = request.registry['ir.ui.menu'].search(request.cr, SUPERUSER_ID, [('name', '=','Seller Dashboard')], context=request.context)
            menu_brw = request.registry['ir.ui.menu'].browse(request.cr, SUPERUSER_ID, menu_id, context=request.context)

        if seller_manager_user.id in group_id:
            menu_id = request.registry['ir.ui.menu'].search(request.cr, SUPERUSER_ID, [('name', '=','Seller Dashboard')], context=request.context)
            menu_brw = request.registry['ir.ui.menu'].browse(request.cr, SUPERUSER_ID, menu_id, context=request.context)

        market = '/web#menu_id=' + str(menu_brw.id)

        return werkzeug.utils.redirect(market, 303)


    @http.route(['/seller/signup'], type='http', auth="public", website=True)
    def seller_signup(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        return request.website.render("odoo_website_marketplace.seller_signup")


    @http.route(['/seller/signup/thanks'], type='http', auth="public", website=True)
    def seller_thank_you(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        if post:
            name = post['name']
            shop_name = post['shopname']
            # url = post['url']
            password = post['password2']
            confirm_password = post['password3']
            email = post['email']
            tag_line = post['tagline']

            partner_obj = request.env['res.partner']
            user_obj = request.env['res.users']
            part_vals = {
                'name' : str(name),
                'shop_name' : str(shop_name),
                'email' : str(email),
                'seller' : True,
                # 'url_handler' : str(url),
                'tag_line' : str(tag_line),
                'password' : str(confirm_password),
            }
            
            partner = partner_obj.sudo().create(part_vals)
            
            pending_seller_id = request.env['ir.model.data'].sudo().get_object_reference('odoo_website_marketplace','group_market_place_pending_seller')[1]

            group_list = []
            group_list.append(pending_seller_id)
            # group_list.append(helpdesk_manager_id)
            user_vals = {
                'email': str(email),
                'login': str(email),
                'password' : str(confirm_password),
                'partner_id': partner.id,
                'groups_id': [(6, 0, group_list)],
            }

            users = user_obj.sudo().create(user_vals)
            
            partner1 = request.registry['res.partner'].browse(cr, SUPERUSER_ID, partner.id, context=request.context)
            
            partner1.write({'user_id':users.id, 'website_true' : True})


            # template_obj = self.pool.get('email.template')

            # template_id = request.registry['ir.model.data'].get_object_reference(request.cr, request.session.uid, 'odoo_website_marketplace','email_template_marketplace')[1]

            # mananger_seller_id = request.env['ir.model.data'].sudo().get_object_reference('odoo_website_marketplace','group_market_place_manager')[1]

            # group_manager = request.env['res.groups'].sudo().browse(mananger_seller_id)

            # manager = None
            # if group_manager.users:
            #     manager = group_manager.users[0]


            # email_template_obj = request.registry['email.template']
            # email_from = manager.sudo().partner_id.email
            # email_to = str(email)
            # html = """
            #         <p>Dear %s</p>
            #         <p> We Receive your request as a Seller</p>
            #         <p> Thank You for being part of us.</p>
            #         <br/>
            #         <p>Here is your login details </p>
            #         <table style="border 1px solid black">
            #             <tr>
            #                 <td>Login</td>
            #                 <td>%s</td>
            #             </tr>
            #             <tr>
            #                 <td>Password</td>
            #                 <td>%s</td>
            #             </tr>
            #         </table>
            #     """ % (str(name),str(email),str(confirm_password))
            # ctx = {}
            # ctx.update({
            #     'email_from' : email_from,
            #     'email_to' : email_to,
            #     'html' : html,
            #     })
            
            # email_template_obj.send_mail(request.cr, request.session.uid, template_id, manager.id, context=None) 

            return request.website.render("odoo_website_marketplace.seller_thank_you")
        else:
            request.website.render("odoo_website_marketplace.seller_signup")

        return request.website.render("odoo_website_marketplace.seller_thank_you")


    # Seller Menu 
    @http.route(['/seller'], type='http', auth="public", website=True)
    def seller(self, page=0, category=None, search='', **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        return request.website.render("odoo_website_marketplace.sellers")


    # Reviews & Rating
    """ This method is overloaded for to add messaege_rate and short_description
    in product.template"""
    @http.route(['/sellers/comment/<int:seller_id>'], type='http', auth="public", methods=['POST'], website=True)
    def seller_rating( self, seller_id, **post ):
        cr, uid, context = request.cr, request.uid, request.context
        if post.get( 'comment' ):
            message_id1 = request.registry['res.partner'].message_post(
                cr, SUPERUSER_ID, seller_id,
                body=post.get( 'comment' ),
                type='comment',
                subtype='mt_comment',
            context=dict( context ) )  # mail_create_nosubcribe=True
            
            review = post.get( 'review', 0 )
            short_description = post.get( 'short_description' )
            cr, uid = request.cr, request.uid
            mail_message1 = request.registry['mail.message']
            mail_message1.write( cr, SUPERUSER_ID, message_id1, {'message_rate':review, 'short_description':short_description, 'website_message':True, } )
            
            # seller review 
            vals = {}
            seller_review = request.registry['seller.review']
            res_partner_obj = request.registry['res.partner'].browse(cr,uid,seller_id,context=context)
            res_user_obj = request.registry['res.users'].search(request.cr, uid, [('id', '=',res_partner_obj.sudo().user_id.id)], context=request.context)
            if res_user_obj != None:
                vals = {
                    'name' : post['comment'],
                    'seller_id' : res_user_obj[0],
                    'rating_msg' : short_description,
                    'rating_num' : review,
                }
            seller_review_create = seller_review.create(cr, SUPERUSER_ID, vals, context=context)
            return werkzeug.utils.redirect( request.httprequest.referrer + "#comments" )


# Login page based on type of registration.
# class AuthSignupHomeCustom(main.AuthSignupHome):

#     @http.route('/web/signup', type='http', auth='public', website=True)
#     def web_auth_signup(self, *args, **kw):
#         qcontext = self.get_auth_signup_qcontext()

#         if not qcontext.get('token') and not qcontext.get('signup_enabled'):
#             raise werkzeug.exceptions.NotFound()


#         if qcontext.get('type') == 'seller':
#             if 'error' not in qcontext and request.httprequest.method == 'POST':
#                 try:
#                     self.do_signup(qcontext)
#                     return request.render('odoo_website_marketplace.thank_you', qcontext)
#                 except (SignupError, AssertionError), e:
#                     qcontext['error'] = _(e.message)

#         else:
#             if 'error' not in qcontext and request.httprequest.method == 'POST':
#                 try:
#                     self.do_signup(qcontext)
#                     return super(AuthSignupHomeCustom, self).web_login(*args, **kw)
#                 except (SignupError, AssertionError), e:
#                     qcontext['error'] = _(e.message)

#         return request.render('auth_signup.signup', qcontext)


#     def do_signup(self, qcontext):
#         """ Shared helper that creates a res.partner out of a token """
#         values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password','type'))
#         assert any([k for k in values.values()]), "The form was not properly filled in."
#         assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
#         supported_langs = [lang['code'] for lang in request.registry['res.lang'].search_read(request.cr, openerp.SUPERUSER_ID, [], ['code'])]
#         if request.lang in supported_langs:
#             values['lang'] = request.lang
#         self._signup_with_values(qcontext.get('token'), values)
#         request.cr.commit()


#     def _signup_with_values(self, token, values):
#         db, login, password ,type = request.registry['res.users'].signup(request.cr, openerp.SUPERUSER_ID, values, token)
#         if type == 'consumer':
#             request.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
#             uid = request.session.authenticate(db, login, password)
#             if not uid:
#                 raise SignupError(_('Authentication Failed.'))



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
