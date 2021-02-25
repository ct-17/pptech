# __author__ = 'truongdung'
from openerp import fields, models, api
import os


class GTSDebrandingConf(models.Model):
    _name = 'gts.debranding.conf'

    x_active = fields.Boolean(string="Active")
    x_power_by = fields.Char(string="Power By")
    x_logo = fields.Binary(string="Logo")
    x_icon = fields.Binary(string="Icon")
    x_title = fields.Char(string="Title")
    x_hide_usermenu_help = fields.Boolean(string="Hide Help")
    x_hide_usermenu_odoosuport = fields.Boolean(string="Hide Odoo Support")

    @api.model
    def read_write_conf(self):
        value = self.search([('x_active', '=', True)], limit=1)
        my_conf = {}
        if len(value) > 0:
            for k in value._all_columns.keys():
                if k.find('x_') >= 0:
                    if k == 'x_logo' and value[k]:
                        fh = open('%s/%s' % (os.path.dirname(__file__), 'static/src/img/company_logo.gif'), 'wb')
                        fh.write(value[k].decode('base64'))
                        fh.close()
                    elif k == 'x_icon' and value[k]:
                        fh = open('%s/%s' % (os.path.dirname(__file__), 'static/src/img/favicon.ico'), 'wb')
                        fh.write(value[k].decode('base64'))
                        fh.close()
                    my_conf[k.replace("x_", "")] = value[k]
        f = open('%s/%s' % (os.path.dirname(__file__), 'controllers/abc.dung'), 'r+')
        all_conf = eval(f.read() or "{}")
        f.seek(0)
        f.truncate()
        all_conf[self.env.cr.dbname] = my_conf
        f.write(str(all_conf))
        f.close()

    @api.multi
    def write(self, vals):
        res = super(GTSDebrandingConf, self).write(vals)
        self.read_write_conf()
        return res

    @api.model
    def create(self, vals):
        res = super(GTSDebrandingConf, self).create(vals)
        self.read_write_conf()
        return res

GTSDebrandingConf()
