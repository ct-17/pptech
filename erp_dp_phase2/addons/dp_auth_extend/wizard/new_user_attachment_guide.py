from openerp import models, fields, api
import base64, cStringIO, os
SELECTION_TYPE = [('shipmaster', 'Shipmaster'), ('chandler', 'Chandler')]


class NewUserAttachmentGuideWizard(models.TransientModel):
    _name = "new.user.attachment.guide.wizard"

    new_attach_line = fields.One2many('new.user.attachment.guide.wizard.line', 'new_attach_id')

    @api.multi
    def import_user_guide_into_email(self):
        """
        chandler invitation email - dp_auth.notify_new_chandler
        shipmaster invitation email - dp_common.invitation_shipmaster_onboard_email
        :return:
        """
        chandler_template = self.env.ref('dp_auth.notify_new_chandler')
        shipmaster_template = self.env.ref('dp_common.invitation_shipmaster_onboard_email')
        ir_attach_env = self.env['ir.attachment']
        for rec in self:
            for line in rec.new_attach_line:
                src_model = ''
                tmpl = None
                if line.type == 'shipmaster':
                   src_model = 'dp.shipmaster.invitation'
                   tmpl = shipmaster_template
                elif line.type == 'chandler':
                    src_model = 'dp.chandler.temp'
                    tmpl = chandler_template

                if src_model != '' and tmpl is not None:
                    existing_attach_obj = self.env['ir.attachment'].search([('name', '=', tmpl.name),('res_model', '=', 'email.template')], order='create_date desc')
                    attach_obj = ir_attach_env.create({
                        'name': tmpl.name,
                        'datas': line.file_import,
                        'datas_fname': line.file_name,
                        'res_model': 'email.template',
                        'res_id': tmpl.id,
                    })
                    if existing_attach_obj.exists():
                        i = 0
                        while i < len(tmpl.attachment_ids):
                            if tmpl.attachment_ids[i].res_model == 'email.template':
                                tmpl.attachment_ids[i].sudo().unlink()
                            i += 1

                    if attach_obj.exists():
                        sql = """INSERT INTO email_template_attachment_rel (email_template_id, attachment_id) VALUES ({email_template_id},{attachment_id})""".format(email_template_id=tmpl.id, attachment_id=attach_obj.id)
                        self._cr.execute(sql)

class NewUserAttachmentGuideWizardLine(models.TransientModel):
    _name = "new.user.attachment.guide.wizard.line"

    new_attach_id = fields.Many2one('new.user.attachment.guide.wizard')
    type = fields.Selection(SELECTION_TYPE, string='To Email Template', required=True)
    file_import = fields.Binary('Import File', required=True)
    file_name = fields.Char('File Name')
