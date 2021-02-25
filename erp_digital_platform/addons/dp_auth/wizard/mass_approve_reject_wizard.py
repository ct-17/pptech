from openerp import models, fields, api


class DPChandlerMassApproveReject(models.TransientModel):
    _name = "dp.chandler.temp.mass.approve.reject.wizard"

    @api.multi
    def action_mass_approval(self):
        model = self._context.get('active_model', False)
        approve_ids = self._context.get('active_ids', [])
        if model is not False:
            approve_list = self.env[model].browse(approve_ids)
            for chan in approve_list:
                if chan.state == 'pending':
                    chan.action_approve_pending_chandler()

    @api.multi
    def action_mass_reject(self):
        model = self._context.get('active_model', False)
        approve_ids = self._context.get('active_ids', [])
        if model is not False:
            approve_list = self.env[model].browse(approve_ids)
            for chan in approve_list:
                if chan.state == 'pending':
                    chan.action_reject_chandler()