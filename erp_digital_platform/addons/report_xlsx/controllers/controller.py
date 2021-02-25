from openerp.addons.report.controllers.main import ReportController
from openerp.addons.web.http import Controller, route, request
from openerp.report.report_sxw import report_sxw
import simplejson
from werkzeug import exceptions, url_decode
from openerp.tools import html_escape


class EssreportController(ReportController):
    @route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        requestcontent = simplejson.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        if type == 'xlsx':
            reportname = url.split('/report/xlsx/')[1].split('?')[0]

            docids = None
            if '/' in reportname:
                reportname, docids = reportname.split('/')

            if docids:
                # Generic report:
                response = self.report_routes(reportname, docids=docids, converter='xlsx')
            else:
                # Particular report:
                data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
                response = self.report_routes(reportname, converter='xlsx', **dict(data))
            report_obj = request.registry['report']
            cr, uid, context = request.cr, request.uid, request.context
            report = request.registry['ir.actions.report.xml'].search(cr, uid, [('report_name', '=', reportname)])[0]
            report = request.registry['ir.actions.report.xml'].browse(cr, uid, report)

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
                            file_name = eval(report.attachment, {'object': obj}).replace(" ", "_").split('.xlsx')[0]
                    except:
                        file_name = reportname

            response.headers.add('Content-Disposition', 'attachment; filename=%s.xlsx;' % file_name)
            response.set_cookie('fileToken', token)
            return response

        return super(EssreportController, self).report_download(data, token)

    @route([
        '/report/<path:converter>/<reportname>',
        '/report/<path:converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):

        if converter == 'xlsx':
            report_obj = request.registry['ir.actions.report.xml']
            cr, uid, context = request.cr, request.uid, request.context

            if docids:
                docids = [int(i) for i in docids.split(',')]
            options_data = None
            if data.get('options'):
                options_data = simplejson.loads(data['options'])
            if data.get('context'):
                # Ignore 'lang' here, because the context in data is the one from the webclient *but* if
                # the user explicitely wants to change the lang, this mechanism overwrites it.
                data_context = simplejson.loads(data['context'])
                if data_context.get('lang'):
                    del data_context['lang']
                context.update(data_context)
            html = report_obj.render_report(cr, uid, docids, reportname, data=options_data, context=context)
            return request.make_response(html)
        return super(EssreportController, self).report_routes(reportname, docids, converter, **data)

