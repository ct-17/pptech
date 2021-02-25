from openerp.report import report_sxw
from openerp.osv import osv

class payment_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(payment_parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_company_info': self.get_company_info,
            'get_customer_info':self.get_customer_info,
            'get_payment_lines':self.get_payment_lines,
            'get_payment_info':self.get_payment_info,
        })

    def get_company_info(self,docs):
        for o in docs:
            res=o.company_id
        return res
    
    def get_customer_info(self,docs):
        for o in docs:
            res=o.partner_id
        return res

    def get_payment_lines(self,docs):
        for o in docs:
            res=o.line_cr_ids
        return res

    def get_payment_info(self,docs):
        for o in docs:
            res=o
        return res

class wrapped_payment(osv.AbstractModel):
    _name = 'report.awesome_invoice_report_template.custom_report_payment_document'
    _inherit = 'report.abstract_report'
    _template = 'awesome_invoice_report_template.custom_report_payment_document'
    _wrapped_report_class = payment_parser
    