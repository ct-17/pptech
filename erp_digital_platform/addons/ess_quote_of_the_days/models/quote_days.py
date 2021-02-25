# __author__ = 'BinhTT'
from openerp import models, fields, api


class QuoteDays(models.Model):
    _name = 'quote.days'
    name = fields.Char('Quotes')
    autho = fields.Char('Author')
    date = fields.Date('Date')
    img = fields.Binary('Image')