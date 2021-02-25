# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


from openerp import api, tools
from openerp import models, fields, _
import base64,logging, psycopg2
from openerp import SUPERUSER_ID
_logger = logging.getLogger(__name__)
from openerp.addons.base.ir.ir_mail_server import MailDeliveryException



class mail_mail(models.Model):
    """ Model holding RFC2822 email messages to send. This model also provides
        facilities to queue and send new email messages.  """
    _inherit = 'mail.mail'

    attempt_send = fields.Integer(default=0,string='Sending Attempts', readonly=True)
    error_count = fields.Integer('Error Counter', default=0)
    error_log = fields.Text('Error', default='')

    @api.constrains('state')
    def _onchange_state(self):
        if self.state == 'exception':
            self.state = 'outgoing'