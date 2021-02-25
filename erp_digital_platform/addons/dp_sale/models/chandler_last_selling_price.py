from openerp import models, fields, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time


class ChandlerLastSellingPrice(models.Model):
    _name = "chandler.last.selling.price"

    chan_partner_id = fields.Many2one('res.partner', string='Chandler Partner')
    sm_partner_id = fields.Many2one('res.partner', string='Ship Master Partner')
    product_id = fields.Many2one('product.product')
    last_selling_price = fields.Float(digits=dp.get_precision('Product Price'))
    currency_and_rate = fields.Char('Currency / Rate')