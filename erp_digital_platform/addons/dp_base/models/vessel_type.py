from openerp import models, fields, api

class VesselModel(models.Model):
    _name = 'vessel.type'

    # UI display column name
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
