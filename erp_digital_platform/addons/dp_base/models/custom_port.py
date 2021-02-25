from openerp import models, fields, api


class CustomPort(models.Model):
    _name = 'custom.port'

    # TODO: need to pump data into db
    code = fields.Char('Port Code')
    name = fields.Char('Name')
    port_reference_num = fields.Char('Port Reference ID')
    country_code = fields.Char('Country Code')
    country_id = fields.Many2one('res.country', 'Country Name')
    country_reference_num = fields.Char('Country Reference ID')

    @api.multi
    def name_get(self):
        result=[]
        for record in self:
            port = record
            string = port.code + ': ' + port.name
            result.append((port.id, "%s" % (string)))
        return result

    @api.multi
    def action_import_custom_port(self):
        pass