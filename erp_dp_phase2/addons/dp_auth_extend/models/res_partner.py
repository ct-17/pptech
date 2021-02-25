import logging, werkzeug
from urlparse import urljoin
from openerp.tools.translate import _
from openerp import models, fields, api, tools
from openerp.exceptions import except_orm, Warning
from datetime import datetime as dt
from openerp.http import request
_logger = logging.getLogger(__name__)


class DPAuthExtendResPartner(models.Model):
    _inherit = 'res.partner'

    chandler_signup_url = fields.Char(compute='get_chandler_signup_url')

    @api.multi
    def get_chandler_signup_url(self):
        context = {}
        if self._context is None:
            context = self._context
        base_url = self.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value

        for partner in self:
            if partner.signup_type == 'signup':
                partner.chandler_signup_url = urljoin(base_url, "/web/signup?token=%s" % (partner.signup_token))


class DPChandlerTempList_extend(models.Model):
    _inherit = "dp.chandler.temp"

    approval_date = fields.Datetime('Approval Date')
    joined_date = fields.Datetime('Joined Date')
    last_session = fields.Datetime('Last Session', compute='_get_last_session')

    @api.multi
    def action_approve_pending_chandler(self):
        super(DPChandlerTempList_extend, self).action_approve_pending_chandler()
        self.approval_date = dt.now()

    @api.multi
    def _get_last_session(self):
        res_users_log_obj = request.env['res.users.log']
        for r in self:
            r.last_session = res_users_log_obj.search([('user_id', '=', r.user_id.id)], order='sign_in desc', limit=1).sign_in