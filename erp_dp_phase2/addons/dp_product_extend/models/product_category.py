from openerp import models, fields, api


class DPProductCategoryExtend(models.Model):
    _inherit = 'product.category'

    source_origin = fields.Selection([('btf', 'BuyTaxFree'), ('np', 'New Port')], string='Origin')
    is_to_np = fields.Boolean('Sync to New Port')
    is_from_np = fields.Boolean('Sync From New Port')
    sync_status = fields.Boolean('Sync Success')
    erp_id = fields.Integer('ERP Vessel Name ID')
