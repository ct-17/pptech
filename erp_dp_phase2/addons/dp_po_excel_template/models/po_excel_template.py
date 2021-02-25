from openerp import fields, models, api
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta as rd
from openerp.tools.float_utils import float_round
from openerp import tools
import xlsxwriter

class po_excel_report(models.Model):

    def print_xls_report(self, cr, uid, ids, context=None):
        data=self.read(cr,uid,ids)[0]
        return {'type': 'ir.actions.report.xml',
                'report_name':'dp_po_excel_template.po_excel_template.xlsx',
                'datas':data
        }

class so_excel_template(ReportXlsx):
    _name = 'report.dp_po_excel_template.po_excel_report'

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

        self.heading_bold_center = self.wb.add_format({
            'bold': 1,
            'text_wrap': 1,
            'align': 'left',
            'valign': 'vcenter',
            'font_name': self.font,
            # 'font_size': 22,
        })

        self.table_header_center = self.wb.add_format({
            'bold': 1,
            'text_wrap': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_name': self.font,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'border': 1
        })

        self.table_content = self.wb.add_format({
            'bold': 0,
            'text_wrap': 1,
            'align': 'left',
            'font_name': self.font,
            'top': 0,
            'left': 0,
            'right': 0,
            'bottom': 0,
            'border': 0
        })

        self.table_content_center = self.wb.add_format({
            'bold': 0,
            'text_wrap': 1,
            'align': 'left',
            'valign': 'vcenter',
            'font_name': self.font,
            'top': 0,
            'left': 0,
            'right': 0,
            'bottom': 0,
            'border': 0
        })

        self.table_content_center_bold = self.wb.add_format({
            'bold': 0,
            'text_wrap': 1,
            'align': 'left',
            'valign': 'vcenter',
            'font_name': self.font,
            'top': 0,
            'left': 0,
            'right': 0,
            'bottom': 0,
            'border': 0,
            'bold': 1
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

        self.footer_label = self.wb.add_format({
            'text_wrap': 1,
            'align': 'right',
            'valign': 'bottom',
            'font_name': self.font,
            'bold': 1,
            # 'top': 1,
            # 'left': 1,
            # 'right': 1,
            # 'bottom': 1,
            # 'border': 1
        })
        self.footer_label_top_border = self.wb.add_format({
            'bold': 1,
            'text_wrap': 1,
            'align': 'right',
            'valign': 'bottom',
            'font_name': self.font,
            'top': 1,
            # 'left': 1,
            # 'right': 1,
            # 'bottom': 1,
            # 'border': 1
        })

        self.footer_data = self.wb.add_format({
            'text_wrap': 1,
            'align': 'right',
            'valign': 'bottom',
            'font_name': self.font,
        })

        self.footer_data_top_border = self.wb.add_format({
            'bold': 1,
            'text_wrap': 1,
            'align': 'right',
            'valign': 'bottom',
            'font_name': self.font,
            'top': 1,
            # 'left': 1,
            # 'right': 1,
            # 'bottom': 1,
            # 'border': 1
        })


        self.a4_paper = 9  # set_paper index 9 is A4 size paper

    def _purchase_order_report(self, data, objs):
        self.ws_stock_report = self.wb.add_worksheet('Purchase Order')
        self.ws_stock_report.set_landscape()
        self.ws_stock_report.set_paper(self.a4_paper)
        self.ws_stock_report.fit_to_pages(1, 1)

        # SET REPORT TITLE
        self.ws_stock_report.merge_range('A1:F2', 'Purchase Order', self.bold_center_header)

        # SET COLUMNS'S WIDTH
        self.ws_stock_report.set_column(0, 0, 50)
        self.ws_stock_report.set_column(1, 1, 30)
        self.ws_stock_report.set_column(2, 2, 15)
        self.ws_stock_report.set_column(3, 3, 15)
        self.ws_stock_report.set_column(4, 4, 30)
        self.ws_stock_report.set_column(5, 5, 25)
        self.ws_stock_report.set_row(3, 30)
        self.ws_stock_report.set_row(4, 30)
        self.ws_stock_report.set_row(5, 30)
        self.ws_stock_report.set_row(10, 30)
        self.ws_stock_report.set_row(11, 30)
        self.ws_stock_report.set_row(12, 30)

        # Header Fields
        if objs.parent_partner_id.exists():
            customer_name = objs['parent_partner_id']['name'] or ''
            customer_code = objs['parent_partner_id']['company_code'] or ''
            customer_street = objs['parent_partner_id']['street'] or ''
            customer_street2 = objs['parent_partner_id']['street2'] or ''
            customer_city = objs['parent_partner_id']['city'] or ''
            customer_state_id_name = objs['parent_partner_id']['state_id']['name'] or ''
            customer_zip = objs['parent_partner_id']['zip'] or ''
            customer_country_id_name = objs['parent_partner_id']['country_id']['name'] or ''
        else:
            customer_name = objs['dest_address_id']['name'] or ''
            customer_code = objs['dest_address_id']['company_code'] or ''
            customer_street = objs['dest_address_id']['street'] or ''
            customer_street2 = objs['dest_address_id']['street2'] or ''
            customer_city = objs['dest_address_id']['city'] or ''
            customer_state_id_name = objs['dest_address_id']['state_id']['name'] or ''
            customer_zip = objs['dest_address_id']['zip'] or ''
            customer_country_id_name = objs['dest_address_id']['country_id']['name'] or ''
        order_contact_person = objs['order_contact_person'] or ''
        order_mobile_number = objs['order_mobile_number'] or ''
        order_remarks = objs['order_remarks'] or ''
        vessel_name = objs['vessel_name']['name'] or ''
        other_vessel_name = objs['other_vessel_name'] or ''
        shipping_agent = objs['shipping_agent_id']['name'] or ''
        other_shipping_agent = objs['other_shipping_agent'] or ''

        company_name = objs['company_id']['name'] or ''
        company_street = objs['company_id']['street'] or ''
        company_street2 = objs['company_id']['street2'] or ''
        company_city = objs['company_id']['city'] or ''
        company_state_id_name = objs['company_id']['state_id']['name'] or ''
        company_zip = objs['company_id']['zip'] or ''
        company_country_id_name = objs['company_id']['country_id']['name'] or ''
        order_name = objs['name'] or ''
        date_strp = datetime.strptime(objs['date_order'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=8)
        date = date_strp.strftime('%d/%m/%Y %H:%M:%S')
        source_document = objs['origin'] or ''
        chandler_po_num = objs['po_num'] or ''
        chandler_marking_num = objs['marking_num'] or ''
        eta_strp = datetime.strptime(objs['estimated_arrival'], '%Y-%m-%d')
        eta = eta_strp.strftime('%d/%m/%Y')
        etd_strp = datetime.strptime(objs['estimated_departure'], '%Y-%m-%d')
        etd = etd_strp.strftime('%d/%m/%Y')
        if objs['next_port_id']:
            next_port = objs['next_port_id']['code'] +': ' + objs['next_port_id']['name'] or ''
        else:
            next_port = ''

        # left column
        self.ws_stock_report.write('A3', 'FROM:', self.heading_bold_center)
        self.ws_stock_report.write('A4', customer_code + ' - ' + customer_name, self.table_content_center_bold)
        self.ws_stock_report.write('A5', ', '.join([s for s in [customer_street, customer_street2] if s]),
                                   self.table_content_center)
        self.ws_stock_report.write('A6', ', '.join([s for s in [customer_city, customer_state_id_name, customer_zip, customer_country_id_name] if s]),
                                   self.table_content_center)
        self.ws_stock_report.write('A8', 'Contact Person', self.heading_bold_center)
        self.ws_stock_report.write('B8', order_contact_person, self.table_content_center)
        self.ws_stock_report.write('A9', 'Contact No', self.heading_bold_center)
        self.ws_stock_report.write('B9', order_mobile_number, self.table_content_center)

        self.ws_stock_report.write('A11', 'Vessel Name', self.heading_bold_center)
        self.ws_stock_report.write('B11', vessel_name, self.table_content_center)
        if other_vessel_name:
            self.ws_stock_report.write('A12', 'Other Vessel Name', self.heading_bold_center)
            self.ws_stock_report.write('B12', other_vessel_name , self.table_content_center)
            self.ws_stock_report.write('A13', 'Shipping Agent', self.heading_bold_center)
            self.ws_stock_report.write('B13', shipping_agent, self.table_content_center)
            if other_shipping_agent:
                self.ws_stock_report.write('A14', 'Other Shipping Agent', self.heading_bold_center)
                self.ws_stock_report.write('B14', other_shipping_agent, self.table_content_center)

                self.ws_stock_report.merge_range('A16:A17', 'Remarks', self.heading_bold_center)
                self.ws_stock_report.merge_range('B16:B17', order_remarks, self.table_content_center)
            else:
                self.ws_stock_report.merge_range('A15:A16', 'Remarks', self.heading_bold_center)
                self.ws_stock_report.merge_range('B15:B16', order_remarks, self.table_content_center)
        else:
            self.ws_stock_report.write('A12', 'Shipping Agent', self.heading_bold_center)
            self.ws_stock_report.write('B12', shipping_agent, self.table_content_center)
            if other_shipping_agent:
                self.ws_stock_report.write('A13', 'Other Shipping Agent', self.heading_bold_center)
                self.ws_stock_report.write('B13', other_shipping_agent, self.table_content_center)

                self.ws_stock_report.merge_range('A15:A16', 'Remarks', self.heading_bold_center)
                self.ws_stock_report.merge_range('B15:B16', order_remarks, self.table_content_center)
            else:
                self.ws_stock_report.merge_range('A14:A15', 'Remarks', self.heading_bold_center)
                self.ws_stock_report.merge_range('B14:B15', order_remarks, self.table_content_center)

        # right column
        self.ws_stock_report.write('E3', 'TO:', self.heading_bold_center)
        self.ws_stock_report.write('E4', company_name, self.table_content_center_bold)
        self.ws_stock_report.write('E5', ', '.join([s for s in [company_street, company_street2] if s]),
                                   self.table_content_center)
        self.ws_stock_report.write('E6', ', '.join(
            [s for s in [company_city, company_state_id_name, company_zip, company_country_id_name] if s]),
                                   self.table_content_center)

        self.ws_stock_report.write('E8', 'BTF PO', self.heading_bold_center)
        self.ws_stock_report.write('F8',  order_name, self.table_content_center)
        self.ws_stock_report.write('E9', 'Date', self.heading_bold_center)
        self.ws_stock_report.write('F9', date, self.table_content_center)
        self.ws_stock_report.write('E10', 'Order No', self.heading_bold_center)
        self.ws_stock_report.write('F10', source_document, self.table_content_center)

        self.ws_stock_report.write('E12', 'Chandler PO No', self.heading_bold_center)
        self.ws_stock_report.write('F12', chandler_po_num, self.table_content_center)
        self.ws_stock_report.write('E13', 'Chandler Marking No', self.heading_bold_center)
        self.ws_stock_report.write('F13', chandler_marking_num or None, self.table_content_center)
        self.ws_stock_report.write('E14', 'ETA', self.heading_bold_center)
        self.ws_stock_report.write('F14', eta, self.table_content_center)
        self.ws_stock_report.write('E15', 'ETD', self.heading_bold_center)
        self.ws_stock_report.write('F15', etd, self.table_content_center)
        self.ws_stock_report.merge_range('E16:E17', 'Next Port of Call', self.heading_bold_center)
        self.ws_stock_report.merge_range('F16:F17', next_port, self.table_content_center)


        # REPORT TABLE COLUMN NAME
        row = 18
        self.ws_stock_report.write(row, 0, 'Product', self.table_header_center)
        self.ws_stock_report.write(row, 1, 'Quantity', self.table_header_center)
        self.ws_stock_report.write(row, 2, 'UOM', self.table_header_center)
        self.ws_stock_report.write(row, 3, 'Unit Price', self.table_header_center)
        self.ws_stock_report.write(row, 4, 'Taxes', self.table_header_center)
        self.ws_stock_report.write(row, 5, 'Subtotal', self.table_header_center)
        self.ws_stock_report.repeat_rows(0, row)
        row += 1
        counter = 1
        for items in objs['order_line']:
            self.ws_stock_report.write(row, 0,items['product_id']['name'], self.data_bottomless_center)
            self.ws_stock_report.write(row, 1,items['product_qty'], self.data_bottomless_right)
            self.ws_stock_report.write(row, 2, items['product_uom']['name'], self.data_bottomless_center)
            self.ws_stock_report.write(row, 3, '{0:.2f}'.format(items['price_unit']), self.data_bottomless_right)
            self.ws_stock_report.write(row, 4, items['taxes_id']['display_name'], self.data_bottomless_right)
            self.ws_stock_report.write(row, 5, '{0:.2f}'.format(items['price_subtotal']), self.data_bottomless_right)
            row += 1
            counter += 1

        row += 2
        # REPORT TABLE FOOTER
        self.ws_stock_report.write(row+2, 4, 'Total Amount', self.footer_label)
        self.ws_stock_report.write(row+2, 5, '{0:.2f}'.format(objs['total_before_discount']), self.footer_data)

        # def formatNumber(num):
        #     if num % 1 == 0:
        #         return int(num)
        #     else:
        #         return num

        actual_inc = 3
        if objs['amount_discount']:
            if objs['ws_discount_percent']:
                self.ws_stock_report.write(row + actual_inc, 4,
                                           '{0:.2f}'.format(objs['ws_discount_percent']) + '% Discount',
                                           self.footer_label)
                self.ws_stock_report.write(row + actual_inc, 5, '{0:.2f}'.format(objs['amount_discount']),
                                           self.footer_data)
            else:
                self.ws_stock_report.write(row + actual_inc, 4, 'Discount', self.footer_label)
                self.ws_stock_report.write(row + actual_inc, 5, '{0:.2f}'.format(objs['amount_discount']),
                                           self.footer_data)
            actual_inc += 1
        if objs['amount_tax']:
            self.ws_stock_report.write(row + actual_inc, 4, 'Taxes', self.footer_label)
            self.ws_stock_report.write(row + actual_inc, 5, '{0:.2f}'.format(objs['amount_tax']), self.footer_data)
            actual_inc += 1
        self.ws_stock_report.write(row + actual_inc, 4, 'Grand Total', self.footer_label_top_border)
        self.ws_stock_report.write(row + actual_inc, 5, '{0:.2f}'.format(objs['amount_total']),
                                   self.footer_data_top_border)


    def generate_xlsx_report(self, wb, data, objs):
        report_obj = self.env['ir.actions.report.xml']
        report = report_obj.search([('report_name', '=', self.name[7:])])
        date_time = datetime.now()
        self.wb = wb
        self._init_report_()
        self._purchase_order_report(data, objs)
        return

so_excel_template('report.purchase.order.xlsx', 'purchase.order')

