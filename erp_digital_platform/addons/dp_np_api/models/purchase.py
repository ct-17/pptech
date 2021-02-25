from openerp import models, fields, api
import logging
from openerp.http import request


class DPNPPurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    def wkf_confirm_order(self):
        res = super(DPNPPurchaseOrder, self).wkf_confirm_order()
        dna = self.env['dp.np.api'].with_context(
            purchase_id=self.id,
        ).create({})
        dna.create_cron_job()
        # directly call cron job to create so in erp after creating po
        dp_np_api_rel_obj = request.env['dp.np.api.rel'].search([('dp_purchase_id', '=', self.id)])
        if dp_np_api_rel_obj:
            dp_np_api_rel_obj.dp_np_api_id.with_context({'direct_from_make_po': True}).run_cron()
        return res