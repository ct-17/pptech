from openerp import models, fields, api, tools, _
import os, logging, sys, json
_logger = logging.getLogger('BuyTaxFree-Newport Database Matrix')


class DPNPDatabaseMatrix(models.Model):
    _name = "dp.np.db.matrix"

    """
    only store model name if they have different name serving the same purpose.
    do not store if it is the same, i.e. sale.order on erp and btf is serves the same purpose and has the same model name
    
    or should i store it as well?
    """

    name = fields.Char('Name')
    field_line_ids = fields.One2many('dp.np.db.field.matrix', 'matrix_id')
    dp_model = fields.Char('BuyTaxFree Model')
    np_model = fields.Char('New Port Model')
    has_additional_fields = fields.Boolean('Has Additional Fields in BuyTaxFree Model', default=False)
    auto_capitalize_in_dp = fields.Boolean('Tick if Buytaxfree Model name field is Autocapitalized', default=False)
    display_name = fields.Char('Display Name')

    @api.model
    def create(self, vals):
        name = "[{}]*[{}]".format(str(vals.get('dp_model', False)), str(vals.get('np_model', False)))
        vals.update({'name': name})
        res = super(DPNPDatabaseMatrix, self).create(vals)
        return res