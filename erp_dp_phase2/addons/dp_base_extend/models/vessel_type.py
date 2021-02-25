from openerp import models, fields, api


class VesselTypeModelInherit(models.Model):
    _inherit = 'vessel.type'

    source_origin = fields.Selection([('btf', 'BuyTaxFree'), ('np', 'New Port')], string='Origin')
    is_to_np = fields.Boolean('Sync to New Port')
    is_from_np = fields.Boolean('Sync From New Port')
    sync_status = fields.Boolean('Sync Success')
    erp_id = fields.Integer('ERP Vessel Name ID')

    @api.model
    def create(self, vals):
        if vals.get('name', False):
            vals['name'] = vals['name'].upper()
        return super(VesselTypeModelInherit, self).create(vals)