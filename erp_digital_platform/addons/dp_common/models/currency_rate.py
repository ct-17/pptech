from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class ChandlerCurrencyRate(models.Model):
    _name = "chandler.currency.rate"
    _description = """This model helps to define currency rate by chandler."""

    currency_id = fields.Many2one("res.currency", "Currency")
    chandler_id = fields.Many2one("res.partner", "Currency Rate")
    sale_rate = fields.Float("Sale Rate", digits=dp.get_precision('Product Price'))
    purchase_rate = fields.Float("Purchase Rate")
    is_SGD = fields.Boolean(compute='_check_SGD')

    @api.multi
    def _check_SGD(self):
        for currency_line in self:
            if currency_line.currency_id.name == 'SGD':
                currency_line.is_SGD = True;

    @api.multi
    def unlink(self):
        if self.currency_id.exists():
            if self.currency_id.name == 'SGD':
                raise except_orm(_('Ooops!'), _('You are not allowed to remove SGD currency! Please discard changes and try again!'))
        return super(ChandlerCurrencyRate, self).unlink()

class ChandlerCurrencyPartner(models.Model):
    _inherit = "res.partner"

    currency_line = fields.One2many("chandler.currency.rate", "chandler_id", "Currency Rate")
