from openerp import models

class StockIncoterms(models.Model):
    _inherit = ["stock.incoterms"]
    _rec_name = 'code'