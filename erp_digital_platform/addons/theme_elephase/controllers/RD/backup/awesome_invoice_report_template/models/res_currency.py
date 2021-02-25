from openerp import models, fields

class res_currency(models.Model):
    _inherit = "res.currency"

    currency_name = fields.Char('Currency Name', help="Currecny Full name as known in the world")
