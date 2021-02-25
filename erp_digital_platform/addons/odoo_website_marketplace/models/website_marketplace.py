# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import osv, orm, fields
from openerp import api, models, tools, _
from openerp import SUPERUSER_ID, tools
from openerp.addons.website_sale.models.sale_order import website,sale_order

class res_users(osv.Model):
    _inherit='res.users'
    _columns={
              'type':fields.selection([('consumer', 'Consumer'), ('seller', 'Seller')], string='Types'),
              }

# For Registration page
class res_users(osv.Model):
    _inherit = 'res.users'

    def signup(self, cr, uid, values, token=None, context=None):
        """ signup a user, to either:
            - create a new user (no token), or
            - create a user for a partner (with token, but no user for partner), or
            - change the password of a user (with token, and existing user).
            :param values: a dictionary with field values that are written on user
            :param token: signup token (optional)
            :return: (dbname, login, password) for the signed up user
        """
        if token:
            # signup with a token: find the corresponding partner id
            res_partner = self.pool.get('res.partner')
            partner = res_partner._signup_retrieve_partner(
                            cr, uid, token, check_validity=True, raise_exception=True, context=None)
            # invalidate signup token
            partner.write({'signup_token': False, 'signup_type': False, 'signup_expiration': False})

            partner_user = partner.user_ids and partner.user_ids[0] or False

            # avoid overwriting existing (presumably correct) values with geolocation data
            if partner.country_id or partner.zip or partner.city:
                values.pop('city', None)
                values.pop('country_id', None)
            if partner.lang:
                values.pop('lang', None)

            if partner_user:
                # user exists, modify it according to values
                values.pop('login', None)
                values.pop('name', None)
                partner_user.write(values)
                return (cr.dbname, partner_user.login, values.get('password'), values.get('type'))
            else:
                # user does not exist: sign up invited user
                values.update({
                    'name': partner.name,
                    'partner_id': partner.id,
                    'email': values.get('email') or values.get('login'),
                })
                if partner.company_id:
                    values['company_id'] = partner.company_id.id
                    values['company_ids'] = [(6, 0, [partner.company_id.id])]
                self._signup_create_user(cr, uid, values, context=context)
        else:
            # no token, sign up an external user
            values['email'] = values.get('email') or values.get('login')
            self._signup_create_user(cr, uid, values, context=context)

        return (cr.dbname, values.get('login'), values.get('password'), values.get('type'))

    def create(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        # overridden to automatically invite user to sign up
        user_id = super(res_users, self).create(cr, uid, values, context=context)
        user = self.browse(cr, uid, user_id, context=context)

        # if type is seller, then seller boolean true in customer/partner...
        if values.get('type') == 'seller':
            user.partner_id.seller = True
            user.partner_id.user_id = user.id

            # When Seller is Register, Seller Access Rights Set True...
            seller_account_user = user.env.ref('odoo_website_marketplace.group_market_place_seller')
            seller_employee_user = user.env.ref('base.group_user')
            seller_access_user = user.env.ref('base.group_erp_manager')
            seller_portal_user = user.env.ref('base.group_portal')
            user.groups_id=[(6, 0, [seller_account_user.id, seller_employee_user.id, seller_access_user.id, seller_portal_user.id])]

        if user.email and not context.get('no_reset_password'):
            context = dict(context, create_user=True)
            try:
                self.action_reset_password(cr, uid, [user.id], context=context)
            except MailDeliveryException:
                self.pool.get('res.partner').signup_cancel(cr, uid, [user.partner_id.id], context=context)
        return user_id






# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
