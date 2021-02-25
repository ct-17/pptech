from openerp import models, fields, api

class purchaseOrder(models.Model):
    _inherit = "procurement.order"

    # comment because already super at dp_np_api
    # @api.multi
    # def run(self, autocommit=False):
    #     res = super(purchaseOrder, self).run(autocommit)
    #     self.mapped(lambda x: x.purchase_id).write({'so_id': self.mapped(lambda x: x.sale_line_id).mapped(lambda x: x.order_id).id or False})
    #     return res


class DPPurchaseOrder(models.Model):
    _inherit = "purchase.order"
    purchaser = fields.Many2one('res.users', string="Purchaser", default=lambda self: self.env.user)
    so_id = fields.Many2one('sale.order', string="SO Number")

    @api.model
    def get_np_sales_email(self):
        config_param_obj = self.env['ir.config_parameter'].search([('key', '=', 'np_sales_email_parameter')])
        if config_param_obj.exists():
            return config_param_obj.value

    @api.model
    def get_btf_support_email(self):
        config_param_obj = self.env['ir.config_parameter'].search([('key', '=', 'btf_support_email_parameter')])
        if config_param_obj.exists():
            return config_param_obj.value

    @api.multi
    def tmp_send_mail(self):
        """ This method is temp used for testing purpose only (email Without attachment)
            Change accordingly your needs.
        """
        template = self.env.ref('dp_purchase.confirm_chandler_quote_to_chandler_email')
        template.send_mail(self.id, force_send=True, raise_exception=True)
        return True

    @api.multi
    def tmp_attached_send_mail(self):
        """ This method is temp used for testing purpose only (email With attachment)
            Change accordingly your needs.
        """
        pdf = self.env['report'].sudo().get_pdf(self, 'purchase.report_purchaseorder')
        attachment = self.env['ir.attachment'].create({'type': 'binary', 'name': 'Report.pdf',
                                                       'datas_fname': 'Report.pdf', 'datas': pdf.encode('base64')})
        template = self.env.ref('dp_purchase.confirm_chandler_quote_to_newport_email')
        template.attachment_ids = [(6, 0, [attachment.id])]
        template.send_mail(self.id, force_send=True, raise_exception=True)
        return True

