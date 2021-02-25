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

class payment_seller(models.Model):
    _name = 'payment.seller'

    name = fields.Char('Name',default='New')
    seller_id= fields.Many2one('res.users', "seller" ,required=True)
    payment = fields.Selection([
            ('paid', 'Paid'),
            ('refund', 'Refund'),
            ('seller_payment', 'Seller Payment'),
            ('cancel', 'Cancelled'),
            ], 'Payment',required=True)
    payment_description = fields.Char('Payment Description') 
    payable_amount = fields.Float('Payable Amount',required=True)
    date = fields.Date('Date')
    payment_method = fields.Many2one('seller.payment.method','Payment Method',required=True)
    payment_type = fields.Selection([('debit','Debit'),('credit','Credit')],'Payment Type',required=True)
    invoice_id = fields.Many2one('account.invoice','Invoice',domain=[('type','=','in_invoice')])
    state = fields.Selection([('draft','Draft'),('requested','Requested'),('confirm','Confirm'),('cancel','Cancelled')],'State')
    
    def view_invoice(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=None):
            mod_obj = self.pool.get('ir.model.data')
            act_obj = self.pool.get('ir.actions.act_window')

            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
            res_id = res and res[1] or False
            print rec.invoice_id,'--------------------------------------------in'
            record = []
            record.append(rec.invoice_id.id)
            return {
                'name': _('Supplier Invoices'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'account.invoice',
                'context': "{'type':'in_invoice', 'journal_type': 'purchase'}",
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': rec.invoice_id.id or False,
            }


class seller_payment_method(models.Model):
    _name = 'seller.payment.method'

    name = fields.Char('Payment Method',required=True)    
    
