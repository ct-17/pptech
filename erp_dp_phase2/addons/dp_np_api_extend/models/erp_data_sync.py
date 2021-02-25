from openerp import models, fields, api
_action = [('create', 'Create'), ('write', 'Write'), ('unlink', 'Unlink')]
_state = [('pending', 'Pending'), ('done', 'Done'), ('cancel', 'Cancel')]


class DPDataSync(models.Model):
    _name = 'erp.data.sync'
    _order = 'create_date desc, priority, state'

    name = fields.Char('Name')
    init_user_id = fields.Many2one('res.users', 'Sync Initiated By User')
    sync_model = fields.Char('Model')
    sync_model_id = fields.Integer('Model ID')
    sync_action = fields.Selection(_action, 'Action')
    priority = fields.Integer('Priority')
    data = fields.Text('Data')
    keyword = fields.Char('Search Keyword')
    state = fields.Selection(_state, 'State')

    @api.model
    def create(self, vals):
        """
        ----------------------------------------------------------------------------------------------------------------
        action_priority - action Priority to upgrade in buytaxfree
        create = 1, write = 2, unlink = 3
        ----------------------------------------------------------------------------------------------------------------
        upgrade_priority - model Priority to upgrade in buytaxfree (higher number means that it has m2o/o2m
        shipping.agent = 20
        vessel.name = 90
        ----------------------------------------------------------------------------------------------------------------
        priority - search from buytaxfree based on this priority for data synchronisation
        priority = upgrade_priority + action_priority
        ----------------------------------------------------------------------------------------------------------------
        """
        action_priority = self.env['erp.data.sync.action.priority'].search([('name','=',vals.get('sync_action'))])
        upgrade_priority = self.env['erp.data.sync.upgrade.priority'].search([('name','=',vals.get('sync_model'))])
        if action_priority.exists() and upgrade_priority.exists():
            priority = action_priority.priority + upgrade_priority.priority
            vals.update({"priority": priority})
        return super(DPDataSync, self).create(vals)