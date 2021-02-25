from openerp import api, fields, models, _, tools

from openerp.osv import fields, osv
import base64,logging, psycopg2, sys
_logger = logging.getLogger(__name__)


class email_template(osv.osv):
    "Templates for sending email"
    _inherit = "email.template"

    @api.cr_uid_id_context
    def send_mail(self, cr, uid, template_id, res_id, force_send=False, raise_exception=False, context=None):
        """Generates a new mail message for the given template and record,
           and schedules it for delivery through the ``mail`` module's scheduler.

           :param int template_id: id of the template to render
           :param int res_id: id of the record to render the template with
                              (model is taken from the template)
           :param bool force_send: if True, the generated mail.message is
                immediately sent after being created, as if the scheduler
                was executed for this message only.
           :returns: id of the mail.message that was created
        """
        if context is None:
            context = {}
        mail_mail = self.pool.get('mail.mail')
        ir_attachment = self.pool.get('ir.attachment')

        # create a mail_mail based on values, without attachments
        values = self.generate_email(cr, uid, template_id, res_id, context=context)
        if not values.get('email_from'):
            raise osv.except_osv(_('Warning!'), _("Sender email is missing or empty after template rendering. Specify one to deliver your message"))
        values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
        attachment_ids = values.pop('attachment_ids', [])
        attachments = values.pop('attachments', [])
        msg_id = mail_mail.create(cr, uid, values, context=context)
        mail = mail_mail.browse(cr, uid, msg_id, context=context)

        # manage attachments
        for attachment in attachments:
            attachment_data = {
                'name': attachment[0],
                'datas_fname': attachment[0],
                'datas': attachment[1],
                'res_model': 'mail.message',
                'res_id': mail.mail_message_id.id,
            }
            context = dict(context)
            context.pop('default_type', None)
            attachment_ids.append(ir_attachment.create(cr, uid, attachment_data, context=context))
        if attachment_ids:
            values['attachment_ids'] = [(6, 0, attachment_ids)]
            mail_mail.write(cr, uid, msg_id, {'attachment_ids': [(6, 0, attachment_ids)]}, context=context)
        if force_send:
            try:
                mail_mail.send(cr, uid, [msg_id], raise_exception=raise_exception, context=context)
            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                error_log = 'Exception Type: ' + str(exc_type) + '\n' + 'Exception Error Description: ' + str(exc_obj) + '\n' \
                + 'Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + '\n' + 'Line Numnber: ' + str(exc_tb.tb_lineno)
                mail.write({'error_log': error_log})
                mail.error_count += 1
        return msg_id