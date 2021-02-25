from openerp import models, fields, api
import json


class ERPAPIVesselNameModelInherit(models.Model):
    _inherit = 'vessel.name'

    @api.model
    def create(self, vals):
        res = super(ERPAPIVesselNameModelInherit, self).create(vals)
        if self._context.get('from_erp') in (False, None):
            res.with_context({'stop_recursive_write': True}).write({'is_to_np': True, 'source_origin': 'btf'})
            self.env['erp.data.sync'].sudo().create({
                'name': res._name + "_" + str(res.id),
                'sync_model': res._name,
                'sync_model_id': res.id,
                'sync_action': 'create',
                'data': json.dumps(vals),
                'state': 'pending',
                'init_user_id': self.env.user.id
            })
        return res

    @api.multi
    def write(self, vals):
        if not self._context.get('stop_recursive_write', False):
            for rec in self:
                if self._context.get('from_erp') in (False, None):
                    rec.env['erp.data.sync'].sudo().create({
                        'name': rec._name + "_" + str(rec.id),
                        'sync_model': rec._name,
                        'sync_model_id': rec.id,
                        'sync_action': 'write',
                        'data': json.dumps(vals),
                        'keyword': [('name', '=' , rec.name)],
                        'state': 'pending',
                        'init_user_id': self.env.user.id
                    })
        res = super(ERPAPIVesselNameModelInherit, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            if self._context.get('from_erp') in (False, None):
                rec.env['erp.data.sync'].sudo().create({
                    'name': rec._name + "_" + str(rec.id),
                    'sync_model': rec._name,
                    'sync_model_id': rec.id,
                    'keyword': [('name', '=' , rec.name)],
                    'sync_action': 'unlink',
                    'state': 'pending',
                    'init_user_id': self.env.user.id
                })
        res = super(ERPAPIVesselNameModelInherit, self).unlink()
        return res