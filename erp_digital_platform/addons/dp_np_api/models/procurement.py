from openerp import models, fields, api
from datetime import datetime as dt
import logging
from openerp.exceptions import except_orm


class DPNPProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def run(self,  autocommit=False):
        res = super(DPNPProcurementOrder, self).run(autocommit)
        pur_obj = self.mapped('purchase_id')
        sale_obj = self.mapped(lambda x:x.sale_line_id.mapped(lambda y:y.order_id))
        sale_obj.ensure_one()
        newport_supplier = self.env['res.partner'].sudo().search([('company_code', '=', 'New Port')])
        if not newport_supplier:
            raise except_orm('Warning', 'Please create 1 Company with Company Code is *New Port*')
        newport_supplier.ensure_one()
        pur_obj.write({'purchaser': sale_obj.user_id.id, 'date_order': dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                       'partner_id': newport_supplier.id, 'vessel_name': sale_obj.vessel_name.id, 'vessel_id':sale_obj.vessel_id.id,
                       'other_vessel_name': sale_obj.other_vessel_name, 'other_shipping_agent': sale_obj.other_shipping_agent, 'order_mobile_number':sale_obj.order_mobile_number,
                       'order_contact_person': sale_obj.order_contact_person, 'shipping_agent_id': sale_obj.shipping_agent_id.id, 'crNum':sale_obj.shipping_agent_id.crNum,
                       'next_port_id': sale_obj.next_port_id.id,
                       'last_port_id': sale_obj.last_port_id.id,
                       'so_id': sale_obj.id,
                       'invoice_method': 'manual'})
        pur_obj.sudo().signal_workflow('purchase_confirm')
        return res