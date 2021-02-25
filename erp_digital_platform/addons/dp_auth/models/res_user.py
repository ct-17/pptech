# -*- coding: utf-8 -*-
from openerp import api, models
from openerp.tools.translate import _
import logging, sys
from openerp import SUPERUSER_ID, models
import openerp

_logger = logging.getLogger(__name__)

class UserExtended(models.Model):
    _inherit = "res.users"

    @api.model
    def check_dp_reset_password(self, login):
        """ retrieve the user corresponding to email,
            and display ele******@gmail.com email format in reset password screen. [As per URD screen shot page no 24]
        """
        user_ids = self.search([('login', '=', login)])
        if not user_ids:
            user_ids = self.search([('email', '=', login)])
        if len(user_ids) != 1:
            raise Exception(_('Reset password: invalid username or email'))

        user_email = user_ids.email
        user_first_email = user_email.split("@")[0]
        inx = 0
        new_user_first_email = ""
        for ufe in user_first_email:
            if inx > 2:
                new_user_first_email += "*"
            else:
                new_user_first_email += ufe
            inx+=1
        new_user_first_email += "@"
        for ufe in user_email.split("@")[1:]:
            new_user_first_email += ufe
        return new_user_first_email

    @api.model
    def get_approver_email(self):
        rtn = self.env['res.users'].search([('login', '=', 'admin')])
        rtn.ensure_one()
        if rtn.exists():
            return rtn.partner_id.email
        else:
            return ''

    @api.model
    def create(self, vals):
        rtn = super(UserExtended, self).create(vals)
        return rtn

    @api.model
    def set_shipmaster_permission(self):
        pass

    def _login(self, db, login, password):
        if not password:
            return False
        user_id = False
        cr = self.pool.cursor()
        try:
            # autocommit: our single update request will be performed atomically.
            # (In this way, there is no opportunity to have two transactions
            # interleaving their cr.execute()..cr.commit() calls and have one
            # of them rolled back due to a concurrent access.)
            cr.autocommit(True)
            # check if user exists
            res = self.search(cr, SUPERUSER_ID, [('login','=ilike',login)])
            if res:
                user_id = res[0]
                # check credentials
                self.check_credentials(cr, user_id, password)
                # We effectively unconditionally write the res_users line.
                # Even w/ autocommit there's a chance the user row will be locked,
                # in which case we can't delay the login just for the purpose of
                # update the last login date - hence we use FOR UPDATE NOWAIT to
                # try to get the lock - fail-fast
                # Failing to acquire the lock on the res_users row probably means
                # another request is holding it. No big deal, we don't want to
                # prevent/delay login in that case. It will also have been logged
                # as a SQL error, if anyone cares.
                try:
                    # NO KEY introduced in PostgreSQL 9.3 http://www.postgresql.org/docs/9.3/static/release-9-3.html#AEN115299
                    update_clause = 'NO KEY UPDATE' if cr._cnx.server_version >= 90300 else 'UPDATE'
                    cr.execute("SELECT id FROM res_users WHERE id=%%s FOR %s NOWAIT" % update_clause, (user_id,), log_exceptions=False)
                    cr.execute("UPDATE res_users SET login_date = now() AT TIME ZONE 'UTC' WHERE id=%s", (user_id,))
                    self.invalidate_cache(cr, user_id, ['login_date'], [user_id])
                except Exception:
                    _logger.debug("Failed to update last_login for db:%s login:%s", db, login, exc_info=True)
        except openerp.exceptions.AccessDenied:
            _logger.info("Login failed for db:%s login:%s", db, login)
            user_id = False
        finally:
            cr.close()

        return user_id

    @api.model
    def web_reset_password_send_alert_email(self,qcontext):
        try:
            qcontext.update({'login': self.partner_id.email, 'name': self.name})
            _logger.info('------------------------------------------------------ dp_auth.web_reset_password_send_alert_email START')
            template = self.env.ref('dp_auth.notify_user_password_has_been_reset')
            template.sudo().with_context(qcontext).send_mail(self.id, force_send=True, raise_exception=True)
            _logger.info('------------------------------------------------------ dp_auth.web_reset_password_send_alert_email SUCCESS')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception: ' + str(e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('unable to send web_reset_password_send_alert_email!')
        return True

    @api.model
    def myaccount_reset_password_send_alert_email(self):
        try:
            _logger.info('------------------------------------------------------ dp_auth.notify_user_password_has_been_reset_myaccount START')
            template = self.env.ref('dp_auth.notify_user_password_has_been_reset_myaccount')
            template.send_mail(self.id, force_send=True, raise_exception=True)
            _logger.info('------------------------------------------------------ dp_auth.notify_user_password_has_been_reset_myaccount SUCCESS')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception: ' + str(e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('unable to send web_reset_password_send_alert_email!')
        return True