from openerp import models, fields


class res_currency(models.Model):
    _inherit = "res.company"

    rtn_no = fields.Char('R.T.N.')
    phone2 = fields.Char('Phone2')
    mobile = fields.Char('Mobile')
