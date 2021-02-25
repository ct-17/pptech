import logging
from openerp.tools.translate import _
from openerp import models, fields, api, tools
from openerp.exceptions import except_orm, Warning
from openerp.http import request
from datetime import datetime as dt
_logger = logging.getLogger(__name__)


class ShipmasterInvitationExtend(models.Model):
    _inherit = "shipmaster.invitation"

    @api.multi
    def send_invitation(self):
        #   ___                               _ _         ____  _                      _
        #  / _ \__   _____ _ ____      ___ __(_) |_ ___  |  _ \| |__   __ _ ___  ___  / |
        # | | | \ \ / / _ \ '__\ \ /\ / / '__| | __/ _ \ | |_) | '_ \ / _` / __|/ _ \ | |
        # | |_| |\ V /  __/ |   \ V  V /| |  | | ||  __/ |  __/| | | | (_| \__ \  __/ | |
        #  \___/  \_/ \___|_|    \_/\_/ |_|  |_|\__\___| |_|   |_| |_|\__,_|___/\___| |_|
        #
        sm_emails = [line.shipmaster_email for line in self.invitation_lines]
        results = self.env['res.users'].sudo().search([('login', 'in', sm_emails)])
        if results.exists():
            # res.users(1, ) will throw error
            msg = ",".join([user.login for user in results])
            msg = "The following shipmaster(s) have already registered with BuyTaxFree\n" + msg
            raise except_orm(_("Shipmaster is a registered user in BuyTaxFree"), _(msg))
        else:
            # res.users() then send invitation
            for line in self.invitation_lines:
                line.send_invitation()
                line.invitation_date = dt.now()


class DPShipmasterInvitationLine_extend(models.Model):
    _inherit = "dp.shipmaster.invitation"

    invitation_date = fields.Datetime('Invitation Date')
    joined_date = fields.Datetime('Joined Date')
    last_session = fields.Datetime('Last Session', compute='_get_last_session')

    @api.multi
    def _get_last_session(self):
        res_user = request.env['res.users']
        res_users_log_obj = request.env['res.users.log']
        for r in self:
            res_users_id = res_user.search([('login', '=', r.shipmaster_email)], limit=1)
            r.last_session = res_users_log_obj.search([('user_id', '=', res_users_id.id)], order='sign_in desc',
                                                      limit=1).sign_in
