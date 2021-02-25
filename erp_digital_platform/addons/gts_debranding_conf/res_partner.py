# __author__ = 'truongdung'
from openerp import models, api, fields


class GTSResPartner(models.Model):
    _inherit = 'res.partner'

    bank_name = fields.Char(string="Bank Name")
    bank_address = fields.Char(string="Bank Address")
    swift_code = fields.Char(string="Swift Code")
    account_no = fields.Char(string="Account No.")

GTSResPartner()

