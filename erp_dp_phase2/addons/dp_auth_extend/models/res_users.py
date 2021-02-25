import logging, werkzeug
from openerp import models, fields, api, tools
_logger = logging.getLogger(__name__)

class DPAuthExtendResUsers(models.Model):
    _inherit = 'res.users'

    def check_credentials(self, cr, uid, password):
        password = password.strip()
        return super(DPAuthExtendResUsers,self).check_credentials(cr, uid, password)