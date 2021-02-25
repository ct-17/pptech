from openerp import models, fields, api


class VesselNameModelInherit(models.Model):
    _inherit = 'vessel.name'

    source_origin = fields.Selection([('btf', 'BuyTaxFree'), ('np', 'New Port')], string='Origin')
    is_to_np = fields.Boolean('Sync to New Port')
    is_from_np = fields.Boolean('Sync From New Port')
    sync_status = fields.Boolean('Sync Success')
    erp_id = fields.Integer('ERP Vessel Name ID')

    imo_number = fields.Char(string='IMO Number', required=True)
    type = fields.Many2one('vessel.type', string="Type", required=True)
    flag = fields.Char(string="Flag", required=True)

    @api.model
    def create(self, vals):
        if vals.get('name', False):
            vals['name'] = vals['name'].upper()
        return super(VesselNameModelInherit, self).create(vals)