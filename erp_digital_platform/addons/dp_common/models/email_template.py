from openerp import models, fields

class DPEmailTemplate(models.Model):
    _inherit = "email.template"

    active = fields.Boolean('Active', default=True)