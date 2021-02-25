from openerp import models, fields, api

class VesselNameModel(models.Model):
    _name = 'vessel.name'

    # UI display column name
    image = fields.Binary(String='Image')
    name = fields.Char(string='Name')
    imo_number = fields.Char(string='IMO Number')
    via = fields.Char(string="Via")
    via_desc = fields.Char(string="Via Destination")
    via_group = fields.Char(string="Via Group")
    type = fields.Many2one('vessel.type', string="Type")
    nrt = fields.Char(string="NRT")
    flag = fields.Char(string="Flag")
    crew = fields.Char(string="Crew No")
    shipping_agent = fields.Many2one('shipping.agent', string="Shipping Agent")
