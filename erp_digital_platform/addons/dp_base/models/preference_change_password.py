from openerp.addons.web.controllers.main import Session
from openerp import http
import operator
from openerp.tools.translate import _
from openerp.http import request


class MySession(Session):
    @http.route('/web/session/change_password', type='json', auth="user")
    def change_password(self, fields):
        fields[1]['value'] = fields[1]['value'].strip()
        fields[2]['value'] = fields[2]['value'].strip()
        old_password, new_password, confirm_password = operator.itemgetter('old_pwd', 'new_password', 'confirm_pwd')(
            dict(map(operator.itemgetter('name', 'value'), fields)))
        if len(new_password) < 6:
            return {'error': _('New Passwords must be at least 6 characters in length.'),'title': _('Change Password')}
        elif old_password.strip() == new_password.strip():
            return {'error': _('New Passwords cannot be the same as the old password.'),'title': _('Change Password')}
        else:
            res = super(MySession, self).change_password(fields)
            if 'new_password' in res:
                user_obj = request.env['res.users'].browse(request.uid)
                if user_obj:
                    user_obj.sudo().myaccount_reset_password_send_alert_email()
            return res