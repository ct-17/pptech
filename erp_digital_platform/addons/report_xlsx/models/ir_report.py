# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api, _
from openerp.exceptions import except_orm
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_type = fields.Selection(selection_add=[("xlsx", "xlsx")])

# class ess_report(models.Model):
#     _inherit = 'report'
#
#     @api.model
#     def render_xlsx(self, docids, reportname, data):
#         report_model_name = "report.%s" % reportname
#         # report_model = self.env[report_model_name]
#         # if report_model is None:
#         #     raise except_orm(_("%s model was not found" % report_model_name))
#         create_xlsx = ReportXlsx.create_xlsx_report()
#         return ReportXlsx.create_xlsx_report(  # noqa
#             docids, data
#         )
