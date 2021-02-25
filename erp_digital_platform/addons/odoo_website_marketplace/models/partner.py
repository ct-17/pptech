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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    seller = fields.Boolean('Seller')
    profile_detail = fields.Text(string='Profile Details')
    state = fields.Selection([
            ('pending', 'Pending'),
            ('approve', 'Approve'),
            ('denied', 'Denied'),
            ], 'Status', readonly=True, copy=False, default="pending",  select=True)
    seller_shop_id = fields.Many2one('seller.shop','Seller')
    return_polocy = fields.Html('Return Policy')
    shipping_policy = fields.Html('Shipping Policy')

    @api.multi
    def approve(self):
        for record in self:
            record.state = 'approve'
        return True

    @api.multi
    def deny(self):
        for record in self:
            record.state = 'denied'
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
