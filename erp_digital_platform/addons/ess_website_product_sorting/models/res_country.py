from openerp import models, fields, api

class ResCountryExtend(models.Model):
    _inherit = 'res.country'

    display_name= fields.Char('Display Name')