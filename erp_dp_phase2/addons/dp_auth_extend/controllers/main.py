# -*- coding: utf-8 -*-
import logging
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
import openerp.addons.auth_signup.controllers.main as main
from openerp.addons.auth_signup.res_users import SignupError
from datetime import datetime as dt

_logger = logging.getLogger(__name__)


class SignupExtendExtend(main.AuthSignupHome):


    @http.route('/web/chandler_signup', type='http', auth='public', website=True)
    def chandler_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    chand = request.env['dp.chandler.temp'].sudo().search([('email', '=', qcontext.get('login'))])
                    chand.joined_date = dt.now()
                    return super(SignupExtendExtend, self).web_login(*args, **kw)
                else:
                    if qcontext.get("reset_request"):
                        login = qcontext.get('login')
                        assert login, "No login provided."
                        res_users = request.env['res.users']
                        res_users.sudo().reset_password(login)
                        qcontext['message'] = _("An email has been sent to reset your password.")
                    else:
                        login = qcontext.get('login')
                        assert login, "No login provided."
                        res_users = request.env['res.users']
                        get_email = res_users.sudo().check_dp_reset_password(login)
                        if get_email:
                            qcontext['reset_message'] = _(get_email)
                        else:
                            qcontext['error'] = _("Reset password: invalid username or email")
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception, e:
                qcontext['error'] = e.message or e.name
        if qcontext.get('login') is None or qcontext.get('error')=="Invalid signup token":
            qcontext.update(error_account="Looks like you already have an account with us. Would you like to log in or recover your password?")
            qcontext.update(error={})
        if not qcontext.get('error', False):
            qcontext.update(error={})
        return request.render('dp_auth_extend.chandler_signup_template', qcontext)

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, *args, **kw):
        if not request.uid:
            request.uid = 3
        res = super(SignupExtendExtend,self).web_login(*args, **kw)
        return res