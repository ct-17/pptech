# __author__ = 'BinhTT'
from openerp import tools, http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.controllers.main import Website
from openerp.exceptions import except_orm
import logging, json, random
_logger = logging.getLogger(__name__)

from datetime import date

class quote_days_Website(Website):

    @http.route('/get_quote_days_list', type="json", auth="public")
    def _get_approved_chandler_list(self, **kwargs):
        try:
            today = date.today()
            quote = request.env['quote.days'].sudo().search([('date', '=', today)])
            if not quote:
                quote = random.choice(request.env['quote.days'].sudo().search([]))
                quote.sudo().write({'date': today})
            return json.dumps({'quote': quote.name,
                               'autho': quote.autho or None,
                               'img': quote.img or None})
        except:
            _logger.info(
                'NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING ')
            return json.dumps({'quote': []})