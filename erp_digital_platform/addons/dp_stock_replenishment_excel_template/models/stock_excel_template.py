from openerp import fields, models, api
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import datetime, date
from dateutil.relativedelta import relativedelta as rd
from openerp.tools.float_utils import float_round
from openerp import tools
import xlsxwriter
#
#
class stock_excel_template(models.Model):
    _name = 'stock.replenishment'


    @api.multi
    def _compute_lang(self):
        for r in self:
            r.lang = self.env.user.lang


    def get_stock_replenishment_data(self):
        sql = """
        select CONCAT (pp.default_code, ' - ', pt.name) AS product_name, pu.name AS uom_name, pt.id,
          pt.dp_maximum_qty, pt.dp_minimum_qty,allocated.qty as allocated_qty,
           pt.dp_allocated_qty - allocated.qty as balance_qty
         from product_template pt
            JOIN product_uom pu ON pt.uom_id=pu.id
            JOIN product_product pp on pp.product_tmpl_id = pt.id
            left join (select sum(product_qty) as qty, product_id from sale_line_stock_allocation where state not in ('draft', 'done','cancel') group by product_id) allocated on
                 allocated.product_id = pp.id
         WHERE website_published = TRUE 
                and pt.dp_allocated_qty - allocated.qty < pt.dp_minimum_qty
         """
        self.env.cr.execute(sql)
        data = self.env.cr.dictfetchall()
        return data


class report_stock_excel_template(ReportXlsx):
    _name = 'report.dp_stock_replenishment_excel_template.stock_excel_template'

    def _init_report_(self):
        self.font = 'Times New Roman'

        self.bold_center_header = self.wb.add_format({
            'bold': 1,
            'text_wrap': 1,
            'align': 'center',
            'valign': 'top',
            'font_name': self.font,
            'font_size': 22,
        })

        self.create_dd_mm_yyyy_date = self.wb.add_format({
            'text_wrap': 1,
            'align': 'center',
            'valign': 'top',
            'num_format': 'dd/mm/yyyy',
            'font_name': self.font,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
        })

        self.table_header_center = self.wb.add_format({
            'bold': 1,
            'text_wrap': 1,
            'align': 'center',
            'valign': 'top',
            'font_name': self.font,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'border': 1
        })

        self.data_bottomless_left = self.wb.add_format({
            'text_wrap': 1,
            'align': 'left',
            'valign': 'bottom',
            'font_name': self.font,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'border': 1
        })

        self.data_bottomless_right = self.wb.add_format({
            'text_wrap': 1,
            'align': 'right',
            'valign': 'bottom',
            'font_name': self.font,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'border': 1
        })

        self.data_bottomless_center = self.wb.add_format({
            'text_wrap': 1,
            'align': 'center',
            'valign': 'bottom',
            'font_name': self.font,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'border': 1
        })

        self.data_bottomless_center_red = self.wb.add_format({
            'text_wrap': 1,
            'align': 'center',
            'valign': 'bottom',
            'font_name': self.font,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'border': 1,
            'bg_color': '#FFC7CE'
        })


        self.a4_paper = 9  # set_paper index 9 is A4 size paper



    def _stock_replenishment_report(self, data, objs):
        self.ws_stock_report = self.wb.add_worksheet('Stock Excel Report')
        self.ws_stock_report.set_landscape()
        self.ws_stock_report.set_paper(self.a4_paper)
        self.ws_stock_report.fit_to_pages(1, 1)

        #SET REPORT TITLE
        self.ws_stock_report.merge_range('A1:G2', 'Stock Replenishment Report', self.bold_center_header)

        #SET TIME
        date_time = datetime.now()
        self.ws_stock_report.write('F3','Create Date: ', self.create_dd_mm_yyyy_date)
        self.ws_stock_report.write('G3', str(date_time.strftime("%Y-%m-%d %H:%M:%S")), self.create_dd_mm_yyyy_date)

        # SET COLUMNS'S WIDTH
        self.ws_stock_report.set_column(0, 0, 13)
        self.ws_stock_report.set_column(1, 1, 40)
        self.ws_stock_report.set_column(2, 2, 13)
        self.ws_stock_report.set_column(3, 3, 30)
        self.ws_stock_report.set_column(4, 4, 30)
        self.ws_stock_report.set_column(5, 5, 35)
        self.ws_stock_report.set_column(6, 6, 25)

        # REPORT COLUMN NAME
        row = 4
        self.ws_stock_report.write(row, 0, 'No.', self.table_header_center)
        self.ws_stock_report.write(row, 1, 'Product', self.table_header_center)
        self.ws_stock_report.write(row, 2, 'UOM', self.table_header_center)
        self.ws_stock_report.write(row, 3, 'Maximum Quantity', self.table_header_center)
        self.ws_stock_report.write(row, 4, 'Minimum Quantity', self.table_header_center)
        self.ws_stock_report.write(row, 5, 'Allocated Qty (from DP Requests)', self.table_header_center)
        self.ws_stock_report.write(row, 6, 'Balanced Qty', self.table_header_center)
        self.ws_stock_report.freeze_panes(row + 1, 0)

        stock_replenishment_data = objs.get_stock_replenishment_data()

        self.ws_stock_report.repeat_rows(0, row)
        row += 1
        counter = 1
        # slsa = self.env['sale.line.stock.allocation']
        for items in stock_replenishment_data:
        #     allocated_qty = sum(
        #         slsa.search([('product_id', '=', items['id']), ('state', 'not in', ('done', 'cancel'))]).mapped(
        #             lambda x: x.product_qty))
        #     if items['dp_maximum_qty']-allocated_qty < items['dp_minimum_qty']:
                self.ws_stock_report.write(row, 0, counter, self.data_bottomless_center)
                self.ws_stock_report.write(row, 1, items['product_name'], self.data_bottomless_center)
                self.ws_stock_report.write(row, 2, items['uom_name'], self.data_bottomless_center)
                self.ws_stock_report.write(row, 3, items['dp_maximum_qty'], self.data_bottomless_center)
                self.ws_stock_report.write(row, 4, items['dp_minimum_qty'], self.data_bottomless_center)
                self.ws_stock_report.write(row, 5, items['allocated_qty'], self.data_bottomless_center)
                if items['balance_qty']<0:
                    self.ws_stock_report.write(row, 6, items['balance_qty'], self.data_bottomless_center_red)
                else:
                    self.ws_stock_report.write(row, 6, items['balance_qty'], self.data_bottomless_center)
                row += 1
                counter+=1




    def generate_xlsx_report(self, wb, data, objs):
        report_obj = self.env['ir.actions.report.xml']
        report = report_obj.search([('report_name', '=', self.name[7:])])
        date_time = datetime.now()
        report.name = 'DIGITAL-PLATFORM_STOCK-REPLENISHMENT-REQUEST-REPORT_' + str(date_time.strftime("%d%m%Y"))+ '_' + str(date_time.strftime("%H%M"))
        self.wb = wb
        self._init_report_()
        self._stock_replenishment_report(data, objs)
        return


        # self.report.name = str(date_time)


report_stock_excel_template('report.dp_stock_replenishment_excel_template.stock_excel_template', 'stock.replenishment')
