import logging
from openerp import models, api
_logger = logging.getLogger(__name__)
from openerp.tools.translate import _
from openerp.osv.orm import except_orm


class Import(models.Model):
    _inherit = 'product.pricelist'
    @api.model
    def load(self, fields, data):
        for line in data:
            price = line[-1]
            if price == '0':
                raise except_orm(_('Price Filed Invalid'),
                                 _('Price cannot be 0,\n please amend the field and try importing again.'))
        res = super(Import, self).load(fields, data)
        return res
