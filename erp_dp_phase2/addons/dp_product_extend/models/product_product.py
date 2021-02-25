from openerp import models, fields, api


class DPProductProductExtend(models.Model):
    _inherit = 'product.template'

    country_id = fields.Many2one('res.country', 'Country of Origin')
    country_name = fields.Char()
    hot_selling = fields.Boolean('Hot-Selling', default=False)

    source_origin = fields.Selection([('btf', 'BuyTaxFree'), ('np', 'New Port')], string='Origin')
    is_to_np = fields.Boolean('Sync to New Port')
    is_from_np = fields.Boolean('Sync From New Port')
    sync_status = fields.Boolean('Sync Success')
    erp_id = fields.Integer('ERP Vessel Name ID')

    @api.model
    def create(self, vals):
        res = super(DPProductProductExtend, self).create(vals)
        self.set_country_name()
        return res

    @api.multi
    def write(self, vals):
        res = super(DPProductProductExtend, self).write(vals)
        if not self._context.get('stop_recursive_write', False):
            for rec in self:
                rec.set_country_name()
        return res

    @api.model
    def set_country_name(self):
        if self.country_id.exists():
            if self.country_id.name != self.country_name or self.country_name in (False, None):
                self.with_context({'stop_recursive_write': True}).write({'country_name': self.country_id.name})