from openerp.report import report_sxw
from openerp.osv import osv

class invoice_parser_copy(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(invoice_parser_copy, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_company_info': self.get_company_info,
            'get_customer_info':self.get_customer_info,
            'get_lines_invoice':self.get_lines_invoice,
            'get_invoice_info':self.get_invoice_info,
        })

    def get_company_info(self,docs):
        for o in docs:
            res=o.company_id
        return res
    
    def get_customer_info(self,docs):
        for o in docs:
            res=o.partner_id
        return res

    def get_lines_invoice(self,docs):
        for o in docs:
            res=o.invoice_line
        return res

    def get_invoice_info(self,docs):
        for o in docs:
            res=o
        return res

class wrapped_invoice(osv.AbstractModel):
    _name = 'report.awesome_invoice_report_template.custom_report_invoice_copy'
    _inherit = 'report.abstract_report'
    _template = 'awesome_invoice_report_template.custom_report_invoice_copy'
    _wrapped_report_class = invoice_parser_copy
    