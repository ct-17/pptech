from openerp import  models, fields, api, _
from openerp.osv import osv
from datetime import datetime
import inspect


class Np_currency(models.Model):
    _inherit = 'res.currency'

    def _compute(self, cr, uid, from_currency, to_currency, from_amount, round=True, context=None):
        if (to_currency.id == from_currency.id):
            if round:
                return self.round(cr, uid, to_currency, from_amount)
            else:
                return from_amount
        else:
            rate = self._get_conversion_rate(cr, uid, from_currency, to_currency, context=context)
            if round:
                return self.round(cr, uid, to_currency, from_amount / rate)
            else:
                return from_amount / rate

    @api.v7
    def compute(self, cr, uid, from_currency_id, to_currency_id, from_amount,
                round=True, context=None):
        context = context or {}

        if not from_currency_id:
            from_currency_id = to_currency_id
        if not to_currency_id:
            to_currency_id = from_currency_id
        xc = self.browse(cr, uid, [from_currency_id, to_currency_id], context=context)
        from_currency = (xc[0].id == from_currency_id and xc[0]) or xc[1]
        to_currency = (xc[0].id == to_currency_id and xc[0]) or xc[1]
        return self._compute(cr, uid, from_currency, to_currency, from_amount, round, context)

    @api.v8
    def compute(self, from_amount, to_currency, round=True):
        """ Convert `from_amount` from currency `self` to `to_currency`. """
        assert self, "compute from unknown currency"
        assert to_currency, "compute to unknown currency"
        # apply conversion rate
        if self == to_currency:
            to_amount = from_amount
        else:
            to_amount = from_amount / self._get_conversion_rate(self, to_currency)
        # apply rounding
        return to_currency.round(to_amount) if round else to_amount