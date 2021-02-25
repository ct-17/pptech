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

from openerp import models, fields, api
from datetime import datetime

class marketplace_inventory(models.Model):
    _name = 'marketplace.inventory'

    name = fields.Char('Title')
    product_temp_id = fields.Many2one('product.template', 'Product')
    product_id = fields.Many2one('product.product', 'Product')
    new_quantity = fields.Integer('New Quantity on Hand')
    location_id = fields.Many2one('stock.location','Location')
    note = fields.Text('Note')
    seller_id= fields.Many2one('res.users', "seller")
    state = fields.Selection([
            ('draft', 'Draft'),
            ('requested', 'Requested'),
            ('approved', 'Approve'),
            ('cancel', 'Cancelled'),
            ], 'Status', readonly=True, copy=False, default="draft",  select=True)

    @api.model
    def default_get(self,fields):
        res = super(marketplace_inventory, self).default_get(fields)
        res['name'] = 'Stock added on ' + datetime.now().strftime("%d-%m-%y")
        return res

    @api.onchange('product_temp_id')
    def onchange_product_id(self):
        if self.product_temp_id:
            prod_id = self.env['product.product'].search([('product_tmpl_id','=',self.product_temp_id.id)])
            self.product_id = prod_id.id
            res_users = self.pool.get('res.users') 
            user_ids = res_users.search(self.env.cr, self.env.uid,[], context=None)
            user_id = False
            for partner in user_ids:
                partners = res_users.browse(self.env.cr, self.env.uid, partner, context=None)
                if partners.partner_id == self.product_id.seller_id:
                    user_id = partners.id

            self.seller_id = user_id or False
        return {}

    @api.multi
    def request(self):
        for record in self:
            record.state = 'requested'
        return True

    @api.multi
    def approve(self):
        for record in self:
            record.state = 'approved'
            res = self.env['stock.change.product.qty'].create({
                                                         'product_id':record.product_id.id,
                                                         'location_id':record.location_id.id,
                                                         'new_quantity':record.new_quantity
                                                         })
            res.change_product_qty()
            
        return True

    @api.multi
    def reject(self):
        for record in self:
            record.state = 'cancel'
        return True

    @api.multi
    def set_2_draft(self):
        for record in self:
            record.state = 'draft'
        return True

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    seller_id = fields.Many2one('res.users', "seller")
    
class stock_move(models.Model):
    _inherit = "stock.move"
    
    seller_id = fields.Many2one('res.users', "seller")
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
