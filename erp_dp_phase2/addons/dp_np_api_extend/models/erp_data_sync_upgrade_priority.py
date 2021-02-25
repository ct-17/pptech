from openerp import models, fields, api


class DPDataSyncUpgradePriority(models.Model):
    _name = 'erp.data.sync.upgrade.priority'
    _order = 'create_date desc, priority'

    name = fields.Char('Model Name')
    description = fields.Char('Description')
    priority = fields.Integer('Priority')