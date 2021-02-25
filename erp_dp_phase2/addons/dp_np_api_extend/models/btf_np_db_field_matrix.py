from openerp import models, fields, api, tools, _
import os, logging, sys, json

_logger = logging.getLogger('BuyTaxFree-Newport Database Field Matrix')


class DPNPDatabaseFieldMatrix(models.Model):
    _name = "dp.np.db.field.matrix"
    _order = "matrix_id, name"

    name = fields.Char('Name')
    matrix_id = fields.Many2one("dp.np.db.matrix", 'DB Matrix')
    dp_field = fields.Char('BuyTaxFree Field')
    np_field = fields.Char('New Port Field')
    is_many2one = fields.Boolean("Is Many2one")

    @api.model
    def create(self, vals):
        name = "[{}]*[{}]".format(str(vals.get('dp_field', False)), str(vals.get('np_field', False)))
        vals.update({'name': name})
        res = super(DPNPDatabaseFieldMatrix, self).create(vals)
        return res

    @api.model
    def cron_create_dp_np_field_matrix(self):
        """
         ____                  _          _                                     _
        |  _ \ _   _ _ __ ___ | |__      / \   _ __  _ __  _ __ ___   __ _  ___| |__
        | | | | | | | '_ ` _ \| '_ \    / _ \ | '_ \| '_ \| '__/ _ \ / _` |/ __| '_ \
        | |_| | |_| | | | | | | |_) |  / ___ \| |_) | |_) | | | (_) | (_| | (__| | | |
        |____/ \__,_|_| |_| |_|_.__/  /_/   \_\ .__/| .__/|_|  \___/ \__,_|\___|_| |_|
                                              |_|   |_|
         _   _          ____ _           _
        | \ | | ___    / ___| |__   ___ (_) ___ ___
        |  \| |/ _ \  | |   | '_ \ / _ \| |/ __/ _ \
        | |\  | (_) | | |___| | | | (_) | | (_|  __/
        |_| \_|\___/   \____|_| |_|\___/|_|\___\___|

        matrix = {
            <dp_model>: {<dp_field1>: <np_field1>, <dp_field2>: <np_field2>, ...},
            <dp_model>: {<dp_field1>: <np_field1>, <dp_field2>: <np_field2>, ...}, ...
        }
        """
        db_matrix_obj = self.env['dp.np.db.matrix']
        field_matrix_obj = self.env['dp.np.db.field.matrix']
        matrix = {
            'vessel.name': {
                'name': 'name',
                'imo_number': 'imo_number',
                'type': 'type',
                'nrt': 'nrt',
                'flag': 'flag',
                'crew': 'crew',
                'shipping_agent': 'shipping_agent',
            },
            'shipping.agent': {
                'name': 'name',
                'contact': 'contact',
                'crNum': 'cr_number',
                'active': 'active'
            }
        }
        for dp_model, field_matrix in matrix.iteritems():
            db_matrix = db_matrix_obj.search([('dp_model', '=', dp_model)])
            if db_matrix.exists():
                for dp_field, np_field in field_matrix.iteritems():
                    field_matrix = field_matrix_obj.search([('dp_field', '=', dp_field), ('np_field', '=', np_field)])
                    if not field_matrix.exists():
                        field_matrix_obj.create({'matrix_id': db_matrix.id,
                                                 'dp_field': dp_field, 'np_field': np_field})
