import string
import logging
from openerp import models, fields, api, tools
from openerp.exceptions import Warning
_logger = logging.getLogger(__name__)
import re
import base64, cStringIO, os
import random
from xlrd import open_workbook
from datetime import datetime as dt
from openerp.osv.orm import except_orm
from openerp.tools.translate import _

class ShipmasterInvitation(models.Model):
    _name = "shipmaster.invitation"
    _order = "id desc"



    invitation_lines = fields.One2many('dp.shipmaster.invitation', 'invitation_id', )
    file_import = fields.Binary('Import File')
    file_name = fields.Char()
    template_file = fields.Many2one('ir.attachment')
    template_data = fields.Char( related='template_file.url')


    @api.model
    def default_get(self, fields_list):
        data = super(ShipmasterInvitation, self).default_get(fields_list)
        data.update(template_file = self.env.ref('dp_common.shipmaster_inv_temp').id)
        return data

    @api.multi
    def send_invitation(self):
        for line in self.invitation_lines:
            line.send_invitation()

    @api.multi
    def import_excel(self):
        """
        function import excel and csv file to do invitation
        :return: same form with update line
        """
        self.ensure_one()
        if self.file_import:
            filecontent = base64.b64decode(self.file_import)
            try:
                # Todo: import excel
                input = cStringIO.StringIO()
                input.write(filecontent)
                wb = open_workbook(file_contents=input.getvalue())
                problem_emails = {"inserted_names": [],
                                  "inserted_emails": [],
                                  "invalid_emails": [],
                                  "duplicate_names": [],
                                  "duplicate_emails": []}
                for sheet in wb.sheets():
                    try:
                        self.insert_db(sheet, wb, problem_emails)
                    except Exception as e:
                        raise (str(e))

            except:
                # todo: import csv
                wb = filecontent.split('\r\n')
                for line in range(1, len(wb) - 1):
                    line_data = wb[line].split(',')
                    self.crete_line(line_data[0], line_data[1])

        if problem_emails['invalid_emails']:
            raise except_orm(_('Invalid Email Format Found!'),
                             _( '\n'.join(map(str, list(item for item in problem_emails['invalid_emails']))) + '\n\n Please check and try again.'))
        if problem_emails['duplicate_names']:
            raise except_orm(_('Duplicate Name Found!'),
                             _( '\n'.join(map(str, list(item for item in problem_emails['duplicate_names']))) + '\n\n Please check and try again.'))
        if problem_emails['duplicate_emails']:
            raise except_orm(_('Duplicate Email Found!'),
                             _( '\n'.join(map(str, list(item for item in problem_emails['duplicate_emails']))) + '\n\n Please check and try again.'))

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'shipmaster.invitation',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.model
    def insert_db(self, sheet, wb, problem_emails):
        nrows = sheet.nrows
        for row in range(1, nrows):
            if sheet.cell(row, 1).value != 0 and sheet.cell(row, 0).value != 0:
              self.crete_line(sheet.cell(row, 0).value, sheet.cell(row, 1).value, problem_emails)


    @api.model
    def crete_line(self, name, email, problem_emails):
        """
        create line
        :param name: string
        :param email: string
        :return:
        """
        vals = {
            'shipmaster_name': name,
            'shipmaster_email': email,
            'invitation_id': self.id,
            'problem_emails': problem_emails,
            'import_excel': True
        }
        self.env['dp.shipmaster.invitation'].create(vals)


class DPShipmasterInvitationLine(models.Model):
    _name = "dp.shipmaster.invitation"
    _rec_name = "user_id"
    _order = "id asc"
    """The purpose of this model is to invite shipmaster from chandler profile."""

    name = fields.Char("Invitation Token")
    shipmaster_name = fields.Char("Name", required=True)
    shipmaster_email = fields.Char("Shipmaster Email", required=True)
    state = fields.Selection([('draft', 'Draft'), ('sent','Sent'), ('accepted', 'Accepted')], default="draft")
    user_id = fields.Many2one("res.users", "Chandler", index=True, default=lambda self: self.env.user)
    active = fields.Boolean("Active", default=True)
    invitation_id = fields.Many2one('shipmaster.invitation')

    @api.model
    def get_token_link(self):
        """
        function get token when sign up
        :return:
        """
        return self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value + "/web/signup?inv_id={}".format(self.name)

    @api.model
    def valid_email(self, email):
        return bool(re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)$', email)) or \
                bool(re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,20})$', email))

    @api.model
    def create(self, vals):
        """
        inherit to update url token
        :param vals:
        :return:
        """
        # Check and store invalid emails
        if vals.get("import_excel", False):
            if not self.valid_email(vals.get("shipmaster_email", False)):
                vals['problem_emails']["invalid_emails"].append(vals.get("shipmaster_email"))
                # Check and store duplicate names
            elif next((item for item in vals['problem_emails']['inserted_names'] if item == vals['shipmaster_name']), False):
                vals['problem_emails']["duplicate_names"].append(vals.get("shipmaster_name"))
            # Check and store duplicate emails
            elif next((item for item in vals['problem_emails']['inserted_emails'] if item == vals['shipmaster_email']),False):
                vals['problem_emails']["duplicate_emails"].append(vals.get("shipmaster_email"))
                # raise Warning('Invalid email address \n Please use a valid email format \n example: JohnSmith@yourcompany.com, JaneDoe@yourcompany.com.sg')
            else:
                lettersAndDigits = string.ascii_letters + string.digits
                uniqueInvitationLink = ''.join(random.choice(lettersAndDigits) for i in range(10))
                uniqueInvitationLink += str(self._uid)
                vals.update({'name': uniqueInvitationLink})
                vals['problem_emails']["inserted_names"].append(vals.get("shipmaster_name"))
                vals['problem_emails']["inserted_emails"].append(vals.get("shipmaster_email"))
                rtn = super(DPShipmasterInvitationLine, self).create(vals)
                return rtn
        else:
            lettersAndDigits = string.ascii_letters + string.digits
            uniqueInvitationLink = ''.join(random.choice(lettersAndDigits) for i in range(10))
            uniqueInvitationLink += str(self._uid)
            vals.update({'name': uniqueInvitationLink})
            rtn = super(DPShipmasterInvitationLine, self).create(vals)
            return rtn

    @api.multi
    def send_invitation(self):
        template = self.env.ref('dp_common.invitation_shipmaster_onboard_email')
        template.with_context({'email_bcc': True}).send_mail(self.id, force_send=True, raise_exception=True)
        self.write({'state':'sent', 'invitation_date': dt.now()})
        return True

