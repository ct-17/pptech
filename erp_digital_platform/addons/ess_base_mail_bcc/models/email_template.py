from openerp import models, fields, api, SUPERUSER_ID, sql_db
import logging, sys, psycopg2, time
_logger = logging.getLogger(__name__)


class ESSEmailTemplate(models.Model):
    _inherit = "email.template"

    email_bcc = fields.Char('Bcc', help="Blind carbon copy recipients (placeholders may be used here)")
