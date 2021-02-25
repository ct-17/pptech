from openerp import models, fields, api
from openerp.exceptions import except_orm
import logging


class DPResPartnerCompanyCode(models.Model):
    _inherit = 'res.partner'

    company_code = fields.Char('Company Code')

    @api.constrains('company_code')
    def constrain_company_code(self):
        if self.company_code:
            if len(self.search([('company_code', 'in', (self.company_code.strip(), self.company_code))])) > 1:
                raise except_orm("Warning", 'This Company Code already existed in our system')

class DPChandlerTempListInherit(models.Model):
    _inherit = "dp.chandler.temp"

    code = fields.Char('Code')
    company = fields.Many2one("res.partner", "Company")


    _sql_constraints = [
        ('code_unique_chandler',
         'unique(code)',
         'Code must be Unique!')
    ]

    @api.model
    def partner_info(self):
        data = super(DPChandlerTempListInherit, self).partner_info()
        data.update(company_code=self.code)

        return data