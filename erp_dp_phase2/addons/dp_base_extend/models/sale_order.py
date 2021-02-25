from openerp import  models, fields


class BaseSaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    order_mobile_number = fields.Char('Mobile Number')
    order_contact_person = fields.Char('Contact Person')
    order_remarks = fields.Char('Remarks')
    other_vessel_name = fields.Char('Other Vessel Name')
    other_shipping_agent = fields.Char('Other Shipping Agent')
