from openerp import models, fields, api


class DPResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def get_company_url(self):
        """ This method is used to generate erp link.
            Change accordingly your needs.
        """
        return self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value

    @api.multi
    def tmp_send_mail(self):
        """ This method is temp used for testing purpose only (email)
            Change accordingly your needs.
        """
        template = self.env.ref('dp_base.invitation_chandler_onboard_email')
        template.with_context({'email_bcc': True}).send_mail(self.id, force_send=True, raise_exception=True)
        return True
