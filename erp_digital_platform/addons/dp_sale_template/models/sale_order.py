# __author__ = 'BinhTT'
from openerp import models, fields, api


class PDFSale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def print_quotation(self):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(self.ids) == 1, 'This option should only be used for a single id at a time'
        self.signal_workflow('quotation_sent')
        return self.env['report'].get_action(self, 'dp_sale_template.np_sale_order_body_template')
