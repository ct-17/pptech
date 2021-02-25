﻿from openerp.report import report_sxw
from openerp.osv import osv

class picking_list_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(picking_list_parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_company_info': self.get_company_info,
            'get_customer_info':self.get_customer_info,
#            'get_lines_purchase':self.get_lines_purchase,
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

    def get_lines_purchase(self,docs):
        for o in docs:
            res=o.order_line
        return res

    def get_picking_info(self,docs):
        for o in docs:
            res=o
        return res

class wrapped_picking_list(osv.AbstractModel):
    _name = 'report.awesome_invoice_report_template.custom_report_picking_list_document'
    _inherit = 'report.abstract_report'
    _template = 'awesome_invoice_report_template.custom_report_picking_list_document'
    _wrapped_report_class = picking_list_parser
    