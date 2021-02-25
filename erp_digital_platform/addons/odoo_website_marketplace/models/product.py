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

from datetime import datetime, timedelta
import time
from openerp import models, api, _
from openerp.osv import osv, fields, expression

class product_template(osv.osv):
    _inherit = 'product.template'


    _columns = {
        'seller_id' : fields.many2one('res.partner', "Seller", default=lambda self: self.env.user.partner_id),
        'state' : fields.selection([
            ('draft', 'Draft'),
            ('waiting', 'Waiting'),
            ('approve', 'Approve'),
            ('cancel', 'Cancelled'),
            ], 'Status', readonly=True, copy=False, default="draft",  select=True),
        'product_categ_ids' : fields.many2many('product.public.category','Product Categories')
    }


    @api.model
    def create(self,val):
        val.update({'sale_ok' : True,})
        result = super(product_template, self).create(val)
        return result

    # seller_id = fields.Many2one('res.partner', "Seller",store=True,default=lambda self: self.env.user.partner_id)

    # state = fields.Selection([
    #         ('draft', 'Draft'),
    #         ('waiting', 'Waiting'),
    #         ('approve', 'Approve'),
    #         ('cancel', 'Cancelled'),
    #         ], 'Status', readonly=True, copy=False, default="draft",  select=True)
    # product_categ_ids = fields.Many2many('product.public.category','Product Categories')

    @api.multi
    def set_to_draft(self):
        for record in self:
            record.state = 'draft'
        return True

    @api.multi
    def request_approve(self):
        for record in self:
            template_id = self.pool['ir.model.data'].get_object_reference(self.env.cr, self.env.uid,'odoo_website_marketplace','email_template_marketplace_approve_product')[1]
            email_template_obj = self.pool['email.template']
            email_template_obj.send_mail(self.env.cr, self.env.uid, template_id, record.id, context=None) 
            record.state = 'waiting'
        return True

    @api.multi
    def approve_product(self):
        for record in self:
            template_id = self.pool['ir.model.data'].get_object_reference(self.env.cr, self.env.uid,'odoo_website_marketplace','email_template_marketplace_approved_product')[1]
            email_template_obj = self.pool['email.template']
            email_template_obj.send_mail(self.env.cr, self.env.uid, template_id, record.id, context=None) 
            record.state = 'approve'
            record.website_published = True
            record.active = True
        return True

    @api.multi
    def reject_product(self):
        for record in self:
            template_id = self.pool['ir.model.data'].get_object_reference(self.env.cr, self.env.uid,'odoo_website_marketplace','email_template_marketplace_reject_product')[1]
            email_template_obj = self.pool['email.template']
            email_template_obj.send_mail(self.env.cr, self.env.uid, template_id, record.id, context=None) 
            record.state = 'cancel'
        return True

    # @api.model
    # def default_get(self,field):
    #     res = super(product_template,self).default_get(field)
    #     res['active'] = False
    #     # res['seller_id'] = self.sudo().env.user.company_id.partner_id.id 
    #     return res

class website(models.Model):
    _inherit = 'website'

    def get_seller_products(self, seller):
        user_ids=self.env['res.users'].search([('partner_id','=',seller.id)])
        prod_ids=self.env['product.template'].search([('seller_id','=',user_ids.partner_id.id)])
        return prod_ids
