from openerp import models, fields, api

class ShippingAgent(models.Model):
    _name = 'shipping.agent'

    # UI display column name
    name = fields.Char(string='Name')
    contact = fields.Char(string='Contact')
    crNum = fields.Char(string='C R - Number')
    active = fields.Boolean(string='Active')

