# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today BrowseInfo (<http://www.browseinfo.in>)
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

{
    "name" : "Odoo Multi Seller Marketplace",
    "version" : "8.0.0.4",
    "category" : "eCommerce",
    "depends" : ['base','sale','mail','email_template','product','stock','website','website_sale','website_partner'],
    "author": "BrowseInfo",
    'summary': 'This apps enable Online multi-seller marketplace on odoo to sell thier product, manage product, manage orders and their profile ',
    "description": """
    
    Purpose :- 
This Module Helps Odoo Website Marketplace.
    This apps enable Online multi-seller marketplace on odoo to sell thier product, manage product, manage orders and their profile
    Odoo website marketplace.
    Odoo Multi Seller Marketplace, Odoo Multi seller Marketplace. Odoo marketplace, Marketplace for seller, marketplace odoo seller, 
    """,
    "website" : "www.browseinfo.in",
    "price": 169,
    "currency": 'EUR',
    "data": [
        'security/marketplace_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'edi/email_template_signup.xml',
        'views/assets.xml',
        'views/templates/signup_page.xml',
        'views/templates/thanks_for_register_page.xml',
        'views/templates/website_seller_view.xml',
        'views/templates/mail_message_view.xml',
        'views/templates/sellers_res_partner_views.xml',
        'views/templates/product_view.xml',
        'views/templates/inventory_view.xml',
        'views/templates/seller_config_view.xml',
        'views/templates/seller_sales_view.xml',
        'views/templates/seller_shop.xml',
        'views/templates/seller_signup_template_view.xml',
        'views/templates/odoo_website_marketplace.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
