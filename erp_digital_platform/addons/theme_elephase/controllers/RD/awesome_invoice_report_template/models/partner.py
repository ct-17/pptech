# -*- coding: utf-8 -*-
from openerp import models, fields, api

class ResPartner(models.Model):
    _inherit=["res.partner"]

    commercial_partner_id_number = fields.Char(compute="get_commercial_partner_id_int",string="Commercial Partner ID")
    
    @api.multi
    def get_commercial_partner_id_int(self):
        for partner in self:
            partner.commercial_partner_id_number =  partner.commercial_partner_id and str(partner.commercial_partner_id.id) or False