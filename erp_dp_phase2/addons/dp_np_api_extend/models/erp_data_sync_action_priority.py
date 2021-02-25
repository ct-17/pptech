from openerp import models, fields, api


class DPDataSyncActionPriority(models.Model):
    _name = 'erp.data.sync.action.priority'
    _order = 'create_date desc, priority'

    name = fields.Char('Name')
    priority = fields.Integer('Priority')