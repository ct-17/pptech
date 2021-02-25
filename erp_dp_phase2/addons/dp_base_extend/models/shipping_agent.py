from openerp import models, fields, api


class ShippingAgentInherit(models.Model):
    _inherit = 'shipping.agent'

    source_origin = fields.Selection([('btf', 'BuyTaxFree'), ('np', 'New Port')], string='Origin')
    is_to_np = fields.Boolean('Sync to New Port')
    is_from_np = fields.Boolean('Sync From New Port')
    sync_status = fields.Boolean('Sync Success')
    erp_id = fields.Integer('ERP Vessel Name ID')

    @api.model
    def create(self, vals):
        if vals.get('name', False):
            vals['name'] = vals['name'].upper()
        return super(ShippingAgentInherit, self).create(vals)