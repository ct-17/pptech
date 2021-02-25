from openerp.report import report_sxw
from openerp.osv import osv

class picking_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(picking_parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_company_info': self.get_company_info,
            'get_customer_info':self.get_customer_info,
            'get_lines_picking':self.get_lines_picking,
            'get_picking_info':self.get_picking_info,
        })

    def get_company_info(self,docs):
        for o in docs:
            res=o.company_id
        return res
    
    def get_customer_info(self,docs):
        for o in docs:
            res=o.partner_id
        return res

    def get_lines_picking(self,docs):
        for o in docs:
            res=o.move_lines
        return res

    def get_picking_info(self,docs):
        for o in docs:
            res=o
        return res

class wrapped_picking(osv.AbstractModel):
    _name = 'report.awesome_invoice_report_template.custom_report_delivery_document'
    _inherit = 'report.abstract_report'
    _template = 'awesome_invoice_report_template.custom_report_delivery_document'
    _wrapped_report_class = picking_parser
    