from openerp import models,fields,api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    incoterms_id = fields.Many2one('stock.incoterms',"Incoterms")
    assembly = fields.Char('Assembly')