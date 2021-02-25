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

from openerp import models, fields, api, _
from openerp.osv import osv
from decimal import getcontext, Decimal

class seller_shop(models.Model):
    _name = 'seller.shop'
    _inherit = 'mail.thread'
    _description = 'Seller Shop'


    @api.one
    @api.depends('seller_id')
    def seller_products(self):
        product_ids = self.pool.get('product.template').search(self.env.cr,self.env.uid,[('seller_id','=',self.seller_id.sudo().partner_id.sudo().id)],context=None)
        self.seller_product_ids = [(6,0,product_ids)]
        return True

    @api.depends('seller_product_ids','seller_id')
    def count_product(self):
        self.total_product = len(self.seller_product_ids)
        return True

    name = fields.Char('Shop Name',required=True)

    seller_id= fields.Many2one('res.users', "seller" ,required="True")
    seller_product_ids = fields.Many2many('product.template',store=True, compute='seller_products')
    
    active = fields.Boolean(string='Active',default=True)
    
    city = fields.Char('city')
    color = fields.Integer('Color')
    country_id = fields.Many2one('res.country','Country')
    description = fields.Text('Description')
    state_id =fields.Many2one('res.country.state','State')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')

    email = fields.Char('Email')
    phone = fields.Char('Phone')
    
    # pro_count = fields.Boolean('Product Count')
    total_product = fields.Integer('Total Product',default=0,store=True,compute='count_product')
    
    shop_url = fields.Char('URL',readonly=True)
    header_url = fields.Char('Header URL')
    url_handler = fields.Char('URL Handler',required=True,copy=False)
    
    published_website = fields.Boolean('Website Published')
    # pro_sale_count = fields.Boolean('Product Sale Count')
    
    fax = fields.Char('Fax')
    terms_con_seller = fields.Html('Terms & Conditions')

    # terms_con_shop = fields.Html('Terms & Conditions')
    # ship_address = fields.Boolean('Seller Shipping Address')
    
    banner = fields.Binary('Banner')
    shop_logo = fields.Binary('Shop Logo')
    
    tag_line = fields.Char('Shop Tag Line',required=True)

    return_polocy = fields.Html('Return Policy')
    shipping_policy = fields.Html('Shipping Policy')

    _sql_constraints = [
        ('name_url_handler_shop_uniq', 'UNIQUE(url_handler)', 'URL Name Must Be unique! \n URL you\'re trying to use is already has been taken!!'),
        ('name_seller_shop_unique', 'UNIQUE(seller_id)', 'Seller Name Must Be unique! \n Seller you\'re trying to use is already has been taken!!'),
    ]


    @api.multi
    def toggle_active(self):
        for record in self:
            record.active = True
        return True


class seller_recommendation(models.Model):
    _name = 'seller.recommendation'   
    
    def pub_unpub_button(self):
        for i in self.browse(self.ids):
            i.write({'website_publish': not i.website_publish})
        return True

    seller_id= fields.Many2one('res.users', "seller" ,required="True")
    partner_id= fields.Many2one('res.partner', "Customer",required="True")
    state = fields.Selection([
            ('yes', 'Yes'),
            ('no', 'No'),
            ], 'Recommendation')
    publish_state = fields.Selection([
            ('published', 'Published'),
            ('un_published', 'Unpublished'),
            ], 'State',default="un_published")
    website_publish = fields.Boolean('Published')


class seller_review( models.Model):
    _name = 'seller.review'   
    
    name = fields.Char('Review Title',required=True)
    seller_id= fields.Many2one('res.users', "seller" ,required="True")
    state = fields.Selection([('published','Published'),
                              ('unpublished','Unpublished')],'state')
    email =fields.Char('Email Address')
    rating_num = fields.Integer('Rating',required=True)
    rating_msg = fields.Text('Rating Message',required=True)