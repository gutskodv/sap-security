import os
import xlsxwriter
from sapsecurity.checks.security_check import SecurityCheckStatus


class SecurityReport:
    def __init__(self, main_process, folder_report):
        self.main_process = main_process
        self.dir = folder_report
        self.filename = "sapinfo.xlsx"

    def open_report(self):
        pass

    def get_scan_descr(self):
        scan_descr = list()
        if hasattr(self.main_process, 'datescan'):
            scan_descr.append("Date: {datescan}".format(datescan=self.main_process.datescan))
        if hasattr(self.main_process, 'sessioninfo'):
            if hasattr(self.main_process.sessioninfo, 'user'):
                scan_descr.append("User: {user}".format(user=self.main_process.sessioninfo.user))
        return ", ".join(scan_descr)

    def get_system_descr(self):
        sys_descr = list()
        if hasattr(self.main_process, 'sessioninfo'):
            if hasattr(self.main_process.sessioninfo, 'sid'):
                sys_descr.append("SAP system: {sid}".format(sid=self.main_process.sessioninfo.sid))
            if hasattr(self.main_process.sessioninfo, 'client'):
                sys_descr.append("Client: {client}".format(client=self.main_process.sessioninfo.client))
            if hasattr(self.main_process.sessioninfo, 'app_server'):
                sys_descr.append("Application server: {app_server}".format(
                    app_server=self.main_process.sessioninfo.app_server))
        return "\n".join(sys_descr)

    def generate_report(self):
        rep1 = XlsxReport(os.path.join(self.dir, self.filename))
        current_row = 0
        current_row = rep1.insert_main_header(current_row,
                                              self.main_process.title,
                                              self.get_scan_descr(),
                                              self.get_system_descr()
                                              )
        column_list = ['Security Check Title', 'Description', '', 'Critical Level', 'Status', 'Comment']
        current_row = rep1.insert_columns(current_row,column_list)
        for check in self.main_process.composite_checks:
            current_row = rep1.insert_composite_header(current_row, check.title, check.descr, check.status)
            for elementary_check in check.checks:
                current_row = rep1.insert_elementary_header(current_row,
                                                            elementary_check.title.format(**elementary_check.__dict__),
                                                            elementary_check.descr.format(**elementary_check.__dict__),
                                                            elementary_check.critical,
                                                            elementary_check.status,
                                                            elementary_check.comment)


class XlsxReport:
    def __init__(self, filename):
        self.filname = filename
        self.workbook = xlsxwriter.Workbook(filename)
        self.start_column = 1
        self.main_worksheet = self.workbook.add_worksheet("Security Report")
        for i in range(0, self.start_column):
            self.main_worksheet.set_column(i, i, 1)

        main_title_style = {'bold': True, 'font_name': 'Times New Roman', 'font_size': 20}
        self.main_title_style = self.workbook.add_format(main_title_style)

        self.main_descr_style = self.workbook.add_format({'bold': False,
                                                          'font_name': 'Calibri',
                                                          'font_size': 10,
                                                          'text_wrap': True})

        column_base_style = {'bold': True, 'font_name': 'Times New Roman', 'bg_color': '#C0C0C0', 'font_size': 14,
                             'bottom': 1, 'top': 1}
        column_base_style['left'] = 1
        column_base_style['align'] = 'left'
        self.column_title_style = self.workbook.add_format(column_base_style)

        column_base_style['left'] = 0
        column_base_style['align'] = 'left'
        self.column_descr_style = self.workbook.add_format(column_base_style)

        column_base_style['align'] = 'center'
        self.column_critical_style = self.workbook.add_format(column_base_style)

        column_base_style['align'] = 'center'
        self.column_status_style = self.workbook.add_format(column_base_style)

        column_base_style['right'] = 1
        column_base_style['align'] = 'left'
        self.column_comment_style = self.workbook.add_format(column_base_style)

        self.composite_title_style = self.workbook.add_format({'bold': True,
                                                                'font_name': 'Times New Roman',
                                                               'left': 5,
                                                               'top': 5,
                                                                'font_size': 14})
        self.composite_status_style = self.workbook.add_format({'bold': True,
                                                                'font_name': 'Times New Roman',
                                                               'top': 5,
                                                                'align': 'center',
                                                                'font_size': 12})
        self.composite_comment_style = self.workbook.add_format({'bold': True,
                                                                'font_name': 'Times New Roman',
                                                                 'top': 5,
                                                                 'right': 5,
                                                                'font_size': 14})
        self.composite_descr_style = self.workbook.add_format({'bold': False,
                                                      'font_name': 'Calibri',
                                                      'font_size': 10,
                                                               'bottom': 5,
                                                               'left': 5,
                                                               'right': 5,
                                                                 'text_wrap': True
                                                                 })

        elementary_title_style = {'font_name': 'Times New Roman', 'font_size': 11,
                                  'bottom': 6, 'left': 6, 'top': 6,
                                  'bg_color': '#C6EFCE', 'font_color': '#006100', 'bold': True,
                                  'text_wrap': True}
        self.elementary_title_style_green = self.workbook.add_format(elementary_title_style)

        elementary_title_style['bg_color'] = '#FFC7CE'
        elementary_title_style['font_color'] = '#9C0006'
        self.elementary_title_style_red = self.workbook.add_format(elementary_title_style)

        elementary_title_style['bg_color'] = '#FFEB9C'
        elementary_title_style['font_color'] = '#9C6500'
        self.elementary_title_style_yellow = self.workbook.add_format(elementary_title_style)

        elementary_descr_style = {'font_name': 'Calibri', 'font_size': 10,
                                  'bottom': 6, 'top': 6,
                                  'bg_color': '#C6EFCE', 'font_color': '#006100',
                                  'text_wrap': True}

        self.elementary_descr_style_green = self.workbook.add_format(elementary_descr_style)

        elementary_descr_style['bg_color'] = '#FFC7CE'
        elementary_descr_style['font_color'] = '#9C0006'
        self.elementary_descr_style_red = self.workbook.add_format(elementary_descr_style)

        elementary_descr_style['bg_color'] = '#FFEB9C'
        elementary_descr_style['font_color'] = '#9C6500'
        self.elementary_descr_style_yellow = self.workbook.add_format(elementary_descr_style)

        elementary_critical_icon_style = {'font_name': 'Calibri', 'font_size': 11,
                                   'bottom': 6, 'top': 6,
                                   'bg_color': '#C6EFCE', 'font_color': '#006100',
                                   'text_wrap': True, 'align': 'right'}
        self.elementary_critical_icon_green = self.workbook.add_format(elementary_critical_icon_style)

        elementary_critical_icon_style['bg_color'] = '#FFC7CE'
        elementary_critical_icon_style['font_color'] = '#9C0006'
        self.elementary_critical_icon_red = self.workbook.add_format(elementary_critical_icon_style)

        elementary_critical_icon_style['bg_color'] = '#FFEB9C'
        elementary_critical_icon_style['font_color'] = '#9C6500'
        self.elementary_critical_icon_yellow = self.workbook.add_format(elementary_critical_icon_style)

        elementary_critical_style = {'font_name': 'Calibri', 'font_size': 11,
                                   'bottom': 6, 'top': 6,
                                   'bg_color': '#C6EFCE', 'font_color': '#006100',
                                   'text_wrap': True, 'align': 'left'}
        self.elementary_critical_green = self.workbook.add_format(elementary_critical_style)

        elementary_critical_style['bg_color'] = '#FFC7CE'
        elementary_critical_style['font_color'] = '#9C0006'
        self.elementary_critical_red = self.workbook.add_format(elementary_critical_style)

        elementary_critical_style['bg_color'] = '#FFEB9C'
        elementary_critical_style['font_color'] = '#9C6500'
        self.elementary_critical_yellow = self.workbook.add_format(elementary_critical_style)

        elementary_status_style = {'font_name': 'Calibri', 'font_size': 11,
                                   'bottom': 6, 'top': 6,
                                   'bg_color': '#C6EFCE', 'font_color': '#006100',
                                   'text_wrap': True, 'align': 'center'}

        self.elementary_status_style_green = self.workbook.add_format(elementary_status_style)

        elementary_status_style['bg_color'] = '#FFC7CE'
        elementary_status_style['font_color'] = '#9C0006'
        self.elementary_status_style_red = self.workbook.add_format(elementary_status_style)

        elementary_status_style['bg_color'] = '#FFEB9C'
        elementary_status_style['font_color'] = '#9C6500'
        self.elementary_status_style_yellow = self.workbook.add_format(elementary_status_style)

        elementary_comment_style = {'font_name': 'Calibri', 'font_size': 11,
                                    'bottom': 6, 'right': 6, 'top': 6,
                                    'bg_color': '#C6EFCE', 'font_color': '#006100',
                                    'text_wrap': True}

        self.elementary_comment_style_green = self.workbook.add_format(elementary_comment_style)

        elementary_comment_style['bg_color'] = '#FFC7CE'
        elementary_comment_style['font_color'] = '#9C0006'
        self.elementary_comment_style_red = self.workbook.add_format(elementary_comment_style)

        elementary_comment_style['bg_color'] = '#FFEB9C'
        elementary_comment_style['font_color'] = '#9C6500'
        self.elementary_comment_style_yellow = self.workbook.add_format(elementary_comment_style)


        self.border = self.workbook.add_format({'border':3})
        self.bold = self.workbook.add_format({'bold': True})
        self.text_wrap = self.workbook.add_format({'text_wrap': True})

    def __del__(self):
        if self.workbook:
            self.workbook.close()

    def insert_main_header(self, startrow, main_title, scan_descr, sys_descr):
        self.main_worksheet.write(startrow, self.start_column, main_title, self.main_title_style)
        startrow += 1
        self.main_worksheet.write(startrow, self.start_column, scan_descr, self.main_descr_style)
        startrow += 1
        self.main_worksheet.write(startrow, self.start_column, sys_descr, self.main_descr_style)
        startrow += 2
        return startrow

    def insert_columns(self, startrow, columns):
        column_size = [65, 40, 5, 20, 20, 30]

        self.main_worksheet.write(startrow, self.start_column, columns[0], self.column_title_style)
        self.main_worksheet.write(startrow, self.start_column + 1, columns[1], self.column_descr_style)
        self.main_worksheet.merge_range(startrow, self.start_column + 2,
                                        startrow, self.start_column + 3,
                                        columns[3],
                                        self.column_critical_style)
        self.main_worksheet.write(startrow, self.start_column + 4, columns[4], self.column_status_style)
        self.main_worksheet.write(startrow, self.start_column + 5, columns[5], self.column_comment_style)


        for i, column in enumerate(columns):
            self.main_worksheet.set_column(self.start_column + i, self.start_column + i, column_size[i])
        startrow += 1
        return startrow

    def insert_composite_header(self, startrow, title, descr, status):
        self.main_worksheet.set_row(startrow, 3)
        startrow += 1
        self.main_worksheet.merge_range(startrow,
                                        self.start_column,
                                        startrow,
                                        self.start_column + 3,
                                        title,
                                        self.composite_title_style)
        self.main_worksheet.write(startrow, self.start_column + 4, status, self.composite_status_style)
        self.main_worksheet.write(startrow, self.start_column + 5, '', self.composite_comment_style)
        startrow += 1
        self.main_worksheet.merge_range(startrow,
                                        self.start_column,
                                        startrow,
                                        self.start_column + 5,
                                        descr,
                                        self.composite_descr_style)
        startrow += 1
        self.main_worksheet.set_row(startrow, 3)
        startrow += 1
        return startrow

    def get_ctitical_int(self, critical):
        if critical == 'High level':
            return 1
        elif critical == 'Medium level':
            return 2
        else:
            return 3


    def insert_elementary_header(self, startrow, title, descr, critical, status, comment):
        if status == SecurityCheckStatus.COMPLIED:
            title_style = self.elementary_title_style_green
            descr_style = self.elementary_descr_style_green
            critical_icon_style = self.elementary_critical_icon_green
            critical_style = self.elementary_critical_green
            status_style = self.elementary_status_style_green
            comment_style = self.elementary_comment_style_green
            val = 3

        elif status == SecurityCheckStatus.NOT_COMPLIED:
            title_style = self.elementary_title_style_red
            descr_style = self.elementary_descr_style_red
            critical_icon_style = self.elementary_critical_icon_red
            critical_style = self.elementary_critical_red
            status_style = self.elementary_status_style_red
            comment_style = self.elementary_comment_style_red
            val = 1
        else:
            title_style = self.elementary_title_style_yellow
            descr_style = self.elementary_descr_style_yellow
            critical_icon_style = self.elementary_critical_icon_yellow
            critical_style = self.elementary_critical_yellow
            status_style = self.elementary_status_style_yellow
            comment_style = self.elementary_comment_style_yellow

        self.main_worksheet.write(startrow, self.start_column, title, title_style)
        self.main_worksheet.write(startrow, self.start_column + 1, descr, descr_style)
        self.main_worksheet.write(startrow, self.start_column + 2, self.get_ctitical_int(critical), critical_icon_style)
        self.main_worksheet.write(startrow, self.start_column + 3, critical, critical_style)
        self.main_worksheet.write(startrow, self.start_column + 4, status, status_style)
        self.main_worksheet.write(startrow, self.start_column + 5, comment, comment_style)

        self.main_worksheet.conditional_format(
            startrow, self.start_column + 2, startrow, self.start_column + 2,
            {'type': 'icon_set',
             'icon_style': '3_traffic_lights',
             'icons_only': True,
             'icons': [{'criteria': '>=', 'type': 'number', 'value': 3},
                       {'criteria': '<', 'type': 'number', 'value': 2},
                       {'criteria': '>=', 'type': 'number', 'value': 2}]}
        )
        startrow += 1
        return startrow

    def create_composite_check_page(self, page_name, title, descr, status, data):
        self.worksheet = self.workbook.add_worksheet(page_name)
        if title:
            self.worksheet.write(0, 0, title, self.bold)

        if descr:
            self.worksheet.write(1, 0, title, self.bold)

        self.worksheet.write(2, 0, 'Security check title', self.text_wrap)
        self.worksheet.write(2, 1, 'Description', self.bold)
        self.worksheet.write(2, 2, 'Status', self.bold)
        self.worksheet.write(2, 3, 'Comment', self.bold)

        row = 3
        for elem_title, elem_descr, elem_status, elem_comment in data:
            self.worksheet.write(row, 0, elem_title, self.text_wrap)
            self.worksheet.write(row, 1, elem_descr, self.bold)
            self.worksheet.write(row, 2, elem_status, self.bold)
            self.worksheet.write(row, 3, elem_comment, self.bold)
            row += 1
        self.worksheet.set_column(0, 0, 50)
        self.worksheet.set_column(1, 1, 50)
        self.worksheet.set_column(2, 2, 20)
        self.worksheet.set_column(3, 3, 50)


    def create_total_page(self, title, descr, data):
        self.worksheet = self.workbook.add_worksheet("Total")

        if title:
            self.worksheet.write(0, 0, title, self.bold)

        if descr:
            self.worksheet.write(1, 0, title, self.bold)

        if data:
            row = 2
            for check_title, check_descr, check_status, check_data in data:
                self.worksheet.write(row, 0, check_title, self.bold)
                self.worksheet.write(row, 1, check_descr, self.bold)
                self.worksheet.write(row, 2, check_status, self.bold)
                row += 1

class CsvReport:
    pass
