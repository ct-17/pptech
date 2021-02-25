from openerp import  models, fields

class BasePurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vessel_name = fields.Many2one('vessel.name', string="Vessel Name")
    vessel_id = fields.Many2one('vessel.type', string='Vessel Type')
    shipping_agent_id = fields.Many2one('shipping.agent', string='Shipping Agent')
    next_port = fields.Char("Next Port of Call")
    next_port_id = fields.Many2one('custom.port', "Next Port of Call")
    last_port = fields.Char("Last Port of Call")
    last_port_id = fields.Many2one('custom.port', "Last Port of Call")
    imo_number = fields.Char("IMO Number")
    call_sign = fields.Char("Call Sign")
    stay_duration = fields.Integer("Stay Duration in Singapore (in days)")
    estimated_arrival = fields.Date("Estimated Date of Arrival")
