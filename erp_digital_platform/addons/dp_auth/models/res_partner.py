import random
import re
import string
import logging, sys
from openerp.http import request

from datetime import datetime as dt
from multiprocessing import cpu_count
import threading
CPU = min(cpu_count(), 16)

from openerp import models, fields, api, _, sql_db
from openerp.exceptions import Warning, except_orm
_logger = logging.getLogger(__name__)

def valid_email(email):
  return bool(re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email))


class DPResPartner(models.Model):
    _inherit = "res.partner"

    chandler_list_for_shipmaster = fields.One2many("dp.chandler.partner", "shipmaster_id", "Chandler List")

    vessel_name = fields.Char("Vessel Name")
    vessel_type = fields.Char("Vessel Type")
    imo_number = fields.Char("IMO Number")
    call_sign = fields.Char("Call Sign")

    # change child's pricelist when change parent company's
    @api.multi
    def write(self, vals):
        for r in self:
            if 'property_product_pricelist' in vals and r.child_ids:
                for child_id in r.child_ids:
                    child_id.property_product_pricelist = vals.get('property_product_pricelist')
        return super(DPResPartner, self).write(vals)


class DPChandlerList(models.Model):
    _name = "dp.chandler.partner"
    _order = "priority"
    _rec_name = "chandler_id"
    """The purpose of this model is store list of preferred chandler in shipmaster profile. maximum 3 as per current\
     flow."""

    priority = fields.Integer("Priority", default=1)
    shipmaster_id = fields.Many2one("res.partner", "Shipmaster", index=True, domain=[('customer','=',True)])
    chandler_id = fields.Many2one("res.partner", "Chandler List", index=True, domain=[('supplier','=',True)])
    chandler_temp_id = fields.Many2one("dp.chandler.temp", compute='_get_chandler_temp_id')

    @api.model
    def send_mail_to_chandler(self):
        try:
            template = self.env.ref('dp_auth.invitation_accepted_by_shipmaster_for_chandler_email')
            template.with_context({'email_bcc': True}).send_mail(self.id, force_send=True, raise_exception=True)
        except:
            _logger.exception('{} While sending accepted invitation exception generated'.format(self))
        return True

    @api.depends('chandler_id')
    def _get_chandler_temp_id(self):
        for record in self:
            if record.chandler_id:
                obj = record.env['dp.chandler.temp'].search([('partner_id', '=', record.chandler_id.id)])
                if obj.exists():
                    record.chandler_temp_id = obj.id

# class DPShipmasterInvitation(models.Model):
#     _name = "dp.shipmaster.invitation"
#     _rec_name = "user_id"
#     _order = "id desc"
#     """The purpose of this model is to invite shipmaster from chandler profile."""
#
#     name = fields.Char("Invitation Token")
#     shipmaster_name = fields.Char("Name", required=True)
#     shipmaster_email = fields.Char("Shipmaster Email", required=True)
#     state = fields.Selection([('draft', 'Draft'), ('sent','Sent'), ('accepted', 'Accepted')], default="draft")
#     user_id = fields.Many2one("res.users", "Chandler", index=True, default=lambda self: self.env.user)
#     active = fields.Boolean("Active", default=True)
#
#     @api.model
#     def get_token_link(self):
#         return self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value + "/web/signup?inv_id={}".format(self.name)
#
#     @api.model
#     def create(self, vals):
#         if not valid_email(vals.get("shipmaster_email", False)):
#             raise Warning('Invalid email address \n Please provide only one email address single invitation time.')
#         lettersAndDigits = string.ascii_letters + string.digits
#         uniqueInvitationLink = ''.join(random.choice(lettersAndDigits) for i in range(10))
#         uniqueInvitationLink += str(self._uid)
#         vals.update({'name': uniqueInvitationLink})
#         rtn = super(DPShipmasterInvitation, self).create(vals)
#         return rtn
#
#     @api.multi
#     def send_invitation(self):
#         template = self.env.ref('dp_auth.invitation_shipmaster_onboard_email')
#         template.send_mail(self.id, force_send=True, raise_exception=True)
#         self.write({'state':'sent'})
#         return True

class DPChandlerTempList(models.Model):
    _name = "dp.chandler.temp"

    name = fields.Char('Chandler Name')
    email = fields.Char('Chandler Email')
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('draft', 'Draft')], string='State', default='pending')
    hidden_state = fields.Selection([('new', 'new'), ('write', 'write')], string='Hidden State', default='new', compute='_get_hidden_state')
    user_id = fields.Many2one('res.users', 'User')
    chandler_priority = fields.Integer('Chandler Priority', default=1)
    approver_id = fields.Many2one('res.partner', 'Approver', default=lambda self: self.env['res.partner'].search([('name', '=', 'admin')]))
    partner_id = fields.Many2one('res.partner', 'Partner Name')
    remarks = fields.Text('Remarks')
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    zip = fields.Char(string='Zip', size=24, change_default=True)
    city = fields.Char(tring='City')
    state_id = fields.Many2one('res.country.state', string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country',string='Country', ondelete='restrict')

    @api.constrains('name', 'email')
    def constrain_name(self):
        if len(self.search([('name', 'in', (self.name.strip(), self.name))])) > 1:
            raise except_orm("Warning", 'This Chandler Name already existed in our system')
        if len(self.search([('email', 'in', (self.email.strip(), self.email))])) > 1:
            raise except_orm("Warning", 'This Chandler Email already existed in our system')

    @api.onchange('state_id')
    def onchange_address_state(self):
        if self.state_id:
            state = self.state_id
            self.country_id = state.country_id.id


    @api.model
    def send_email_multithreading(self, sale_ids, email_to=None):
        _logger.info('------------------------------------------------------ dp_auth.dp_chandler_temp.send_email_multithreading START THREAD')
        with api.Environment.manage():
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            uid = self.env.uid
            start_thread = dt.now()
            new_env = api.Environment(new_cr, uid, self.env.context.copy())
            self = self.with_env(new_env)
            for record in self.env['sale.order'].browse(sale_ids):
                newer_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
                uid = self.env.uid
                newer_env = api.Environment(newer_cr, uid, self.env.context.copy())
                self = self.with_env(newer_env)
                try:
                    pending = record.pending_user_id
                    if pending:
                        con = {'other_chandler': True, 'email_to': email_to or ''}
                    else:
                        con = {'existing_chandler': True, 'email_to': email_to or ''}
                except:
                    con = {'existing_chandler': True, 'email_to': email_to or ''}
                self.send_invitation_to_chandler(record.id, con)
                newer_cr.commit()
                newer_cr.close()

            finish_thread = dt.now() - start_thread
            _logger.info(('------------------------------------------------------ dp_auth.dp_chandler_temp.send_email_multithreading TIME FINISH 1 thread: %s') \
                            % (finish_thread.total_seconds()))
            new_cr.commit()
            new_cr.close()
        return True

    @api.model
    def send_invitation_to_chandler(self, sale_id, context={}):
        # context['existing_chandler'] = True if chandler has been approved in the system
        # context['other_chandler'] = True if shipmaster entered chandler as others
        sale_obj = self.env['sale.order'].sudo().with_context(context).browse(sale_id)
        if context.get('existing_chandler', False):
            _logger.info('send_invitation_to_chandler: send_email_to_preferred_chandler_on_checkout START')
            sale_obj.send_email_to_preferred_chandler_on_checkout()
            _logger.info('send_invitation_to_chandler: send_email_to_preferred_chandler_on_checkout COMPLETE ')
            _logger.info('send_invitation_to_chandler: send_email_to_shipmaster_on_checkout START ')
            sale_obj.send_email_to_shipmaster_on_checkout()
            _logger.info('send_invitation_to_chandler: send_email_to_shipmaster_on_checkout COMPLETE ')
        if context.get('other_chandler', False):
            _logger.info('send_invitation_to_chandler: send_email_to_other_chandler_on_checkout START ')
            sale_obj.send_email_to_other_chandler_on_checkout()
            _logger.info('send_invitation_to_chandler: send_email_to_other_chandler_on_checkout COMPLETE ')
            _logger.info('send_invitation_to_chandler: send_email_to_shipmaster_on_checkout START ')
            sale_obj.send_email_to_shipmaster_on_checkout()
            _logger.info('send_invitation_to_chandler: send_email_to_shipmaster_on_checkout COMPLETE ')
            # _logger.info('send_invitation_to_chandler: send_email_to_admin_to_accept_preferred_chandler START ')
            # self.send_email_to_admin_to_accept_preferred_chandler()
            # _logger.info('send_invitation_to_chandler: send_email_to_admin_to_accept_preferred_chandler COMPLETE ')

    @api.model
    def send_email_to_admin_to_accept_preferred_chandler(self):
        try:
            _logger.info('dp_auth.send_email_to_admin_to_accept_preferred_chandler START')
            shipmaster = self._context.get('sale_obj').partner_id.name
            admin_template = self.env.ref('dp_auth.notify_other_chandler_from_shipmaster_digitaplatform_email')
            admin_template.with_context({'shipmaster': shipmaster}).send_mail(self.id, force_send=True, raise_exception=True)
            _logger.info('dp_auth.send_email_to_admin_to_accept_preferred_chandler SUCCESS')
            _logger.info('dp_auth.notify_other_chandler_from_shipmaster_digitaplatform_email: {dp_chandler_temp} email template had been successfully sent'.format(dp_chandler_temp=str(self)))
        except Exception as e:
            _logger.error(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.exception('{} While sending accepted invitation exception generated'.format(self))

    @api.model
    def get_signup_link(self):
        name = self.name
        if ' ' in self.name:
            name = name.replace(' ', '%')
        return self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value + "/web/signup?inv_id={}".format(name)

    @api.multi
    def action_approve_pending_chandler(self):
        self.create_partner_user_send_email()

    @api.model
    def create_partner_user_send_email(self):
        user_obj = self.env['res.users']
        obj = self.env.ref('dp_common.default_template_chandler')
        ru_flag = True
        if isinstance(obj, object):
            user_obj = obj.sudo().copy(default={'name': self.name, 'login': self.email, 'alias_name': self.name,
                                               'active': True, })
            self.write({'user_id': user_obj.id,
                        'partner_id': user_obj.partner_id.id})
            user_obj.partner_id.write(self.partner_info())
            user_obj.partner_id.sudo().action_signup_prepare()
            ru_flag = False
            user_obj.partner_id.currency_line.create({'currency_id': self.env.user.company_id.currency_id.id, 'sale_rate':1, 'chandler_id':user_obj.partner_id.id})
            user_obj.partner_id.currency_line.create({'currency_id': self.env['res.currency'].search([('name','=','USD')]).id, 'sale_rate':0, 'chandler_id':user_obj.partner_id.id})
        else:
            _logger.exception('Unable to create get object, o: {o}, self: {s}'.format(o=obj, s=self))

        try:
            template = self.env.ref('dp_auth.notify_new_chandler')
            template.with_context({'email_bcc': True}).sudo().send_mail(user_obj.id, force_send=True, raise_exception=True)
            # user_obj.action_reset_password(context={'create_user': 1})
            email_flag = False
        except:
            email_flag = True
            _logger.exception('{} While sending accepted invitation exception generated'.format(self))
        if email_flag:
            raise except_orm(_('Unable to send invitation email!'), _('Please contact system admin regarding this issue!'))
        email_flag = False

        if not ru_flag and not email_flag:
            self.write({'state': 'approved', 'remarks': 'Approved by {}'.format(self.approver_id.name)})
            for sale in self.env['sale.order'].sudo().search([('pending_user_id', '=', self.id)]):
                sale.sudo().write({'user_id': self.user_id.id, 'pending_user_id': None})
        else:
            self.write({'state': 'pending'})
            user_obj.partner_id.unlink()
            user_obj.unlink()

    @api.model
    def partner_info(self):
        return{
            'supplier': True,
            'is_company': True,
            'email': self.email,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,
            'parent_id':self.company.id,
            'property_product_pricelist':self.company.property_product_pricelist,
        }

    @api.multi
    def action_reject_chandler(self):
        try:
            t = threading.Thread(target=self.send_email_reject_chandler_multithreading,
                                 args=([self.id]))
            t.start()
            self.write({'approval_date': dt.now()})
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('Multithreading Problems')

        self.write({'state': 'rejected', 'remarks': 'Rejected by {}'.format(self.approver_id.name)})

    @api.model
    def send_email_reject_chandler_multithreading(self, dp_chandler_temp_id):
        _logger.info('------------------------------------------------------ dp_auth.dp_chandler_temp.send_email_reject_chandler_multithreading START THREAD')
        with api.Environment.manage():
            new_cr = sql_db.db_connect(self.env.cr.dbname).cursor()
            uid = self.env.uid
            start_thread = dt.now()
            new_env = api.Environment(new_cr, uid, self.env.context.copy())
            for record in self.with_env(new_env).env['dp.chandler.temp'].browse(dp_chandler_temp_id):

                try:
                    _logger.info('------------------------------------- sending dp_auth.notify_rejected_chandlers START')
                    chandler_template = record.env.ref('dp_auth.notify_rejected_chandlers')
                    chandler_template.with_context({'email_bcc': True}).send_mail(record.id, force_send=True, raise_exception=True)
                    _logger.info('------------------------------------- sending dp_auth.notify_rejected_chandlers SUCCESS')
                except Exception as e:
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + 'Line Numnber: ' + str(exc_tb.tb_lineno))
                    _logger.exception('{} While sending accepted invitation exception generated'.format(record))

                try:
                    _logger.info('------------------------------- sending dp_auth.notify_shipmaster_rejected_chandlers START')
                    chandler_template = record.env.ref('dp_auth.notify_shipmaster_rejected_chandlers')
                    chandler_template.with_context({'email_bcc': True}).send_mail(record.id, force_send=True, raise_exception=True)
                    _logger.info('------------------------------- sending dp_auth.notify_shipmaster_rejected_chandlers SUCCESS')
                except Exception as e:
                    _logger.error(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename) + 'Line Numnber: ' + str(exc_tb.tb_lineno))
                    _logger.exception('{} While sending accepted invitation exception generated'.format(record))

                finish_thread = dt.now() - start_thread
                _logger.info(('------------------------------------------------------ dp_auth.dp_chandler_temp.send_email_reject_chandler_multithreading TIME FINISH 1 thread: %s') \
                             % (finish_thread.total_seconds()))
            dp_sale = self.with_env(new_env).env['ir.module.module'].sudo().search([('name', '=', 'dp_sale')])
            try:
                if dp_sale.state == 'installed':
                    for sale in self.with_env(new_env).env['sale.order'].sudo().search([('pending_user_id', '=', self.id)]):
                        sale.sudo().write({'state': 'cancel'})
            except:
                pass
            new_cr.commit()
            new_cr.close()
        return True


    @api.multi
    def action_mass_approval(self):
        pass

    @api.multi
    def action_mass_reject(self):
        pass

    @api.multi
    def unlink(self):
        partner_obj = self.env['res.partner'].browse(self._ids)
        user_obj = self.env['res.users'].search([('partner_id', 'in', partner_obj.ids)])
        res = super(DPChandlerTempList, self).unlink()
        for rec in partner_obj:
            if rec.exists():
                rec.active = False
        for rec in user_obj:
            if rec.exists():
                rec.active = False
        return res

    @api.model
    def create(self, values):
        chan_admin = self.get_one_chandler_admin()
        values.update({'approver_id': chan_admin.partner_id.id})
        res = super(DPChandlerTempList, self).create(values)
        return res

    @api.multi
    def copy(self, default={}, context=None):
        res = super(DPChandlerTempList, self).copy(default=default, context=context)
        chan_admin = self.get_one_chandler_admin()
        res.approver_id = chan_admin.partner_id.id
        res.user_id = None
        res.partner_id = None
        res.remarks = ''
        return res

    @api.multi
    def write(self, default={}):
        if self.partner_id:
            self.partner_id.write(default)
        return super(DPChandlerTempList, self).write(default)

    @api.model
    def get_one_chandler_admin(self):
        """

        return only 1 chandler admin
        :return:
        """
        chan_admin_grp = self.env['res.groups'].search([('name', '=', 'Chandler Admin')])
        chan_admin = self.env['res.users'].browse([user.id for user in chan_admin_grp.users if user.id != 1])
        try:
            assert len(chan_admin) == 1
        except AssertionError:
            chan_admin = chan_admin[0]

        return chan_admin

    @api.multi
    def _get_hidden_state(self):
        for r in self:
            if r.exists():
                r.hidden_state = 'write'