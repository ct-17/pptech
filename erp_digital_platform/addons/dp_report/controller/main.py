from openerp.addons.web.http import Controller, route, request
from openerp.addons.web.controllers.main import _serialize_exception
from openerp.osv import osv
from openerp.tools import html_escape

import simplejson
from werkzeug import exceptions, url_decode
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from werkzeug.datastructures import Headers
from openerp.addons.report.controllers.main import ReportController


class DP_ReportController(ReportController):

    @route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        requestcontent = simplejson.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        if type == 'qweb-pdf':
            reportname = url.split('/report/pdf/')[1].split('?')[0]
            report_obj = request.registry['report']
            docids = None
            if '/' in reportname:
                reportname, docids = reportname.split('/')

            if docids:
                # Generic report:
                response = self.report_routes(reportname, docids=docids, converter='pdf')
            else:
                # Particular report:
                data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
                response = self.report_routes(reportname, converter='pdf', **dict(data))
            file_name = reportname
            report_obj = request.registry['report']
            cr, uid, context = request.cr, request.uid, request.context
            report = report_obj._get_report_from_name(cr, uid, reportname)
            try:
                active_ids = request.env.context.get('active_ids') or int(docids) if docids else None
            except Exception as e:

                # active_ids = [int(x) for x in docids.split(',')]
                active_ids = []
            active_model = request.env.context.get('active_model') or report.model
            if active_model and active_ids:
                # render report file name follow attribute _file_name of report model
                obj = request.env[active_model].browse(active_ids)
                try:
                    file_name = obj.get_report_file_name()
                # If _file_name is not set in report model, do nothing
                except:
                    try:
                        if report.attachment:
                            file_name = eval(report.attachment, {'object': obj}).replace(" ", "_").split('.pdf')[0]
                    except:
                        file_name = reportname

            response.headers.add('Content-Disposition', 'attachment; filename=%s.pdf;' % file_name)
            response.set_cookie('fileToken', token)

            return response
        return super(DP_ReportController, self).report_download(data, token)

        """This function is used by 'qwebactionmanager.js' in order to trigger the download of
        a pdf/controller report.

        :param data: a javascript array JSON.stringified containg report internal url ([0]) and
        type [1]
        :returns: Response with a filetoken cookie and an attachment header
        """