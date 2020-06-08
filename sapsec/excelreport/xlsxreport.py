import xlsxwriter
from sapsec.checks.security_check import SecurityCheckStatus


class XlsxReport:
    def __init__(self, filename, worksheet_name):
        self.filname = filename
        self.workbook = xlsxwriter.Workbook(filename)
        self.worksheet = self.workbook.add_worksheet(worksheet_name)
        self.styles = dict()
        self.__init_styles()
        self.start_column = self.__init_null_columns(1)
        self.current_row = 0

    def __init_null_columns(self, num=1):
        for i in range(0, num):
            self.worksheet.set_column(i, i, 1)
        return num

    def __add_style(self, style_name, style_dict):
        self.styles[style_name] = self.workbook.add_format(style_dict)

    @staticmethod
    def __set_color_to_style(style_dict, color):
        if color == "red":
            style_dict['bg_color'] = '#FFC7CE'
            style_dict['font_color'] = '#9C0006'
        elif color == "yellow":
            style_dict['bg_color'] = '#FFEB9C'
            style_dict['font_color'] = '#9C6500'
        elif color == "green":
            style_dict['bg_color'] = '#C6EFCE'
            style_dict['font_color'] = '#006100'

    def __add_styles_with_three_colors(self, style_name, style_dict, vcenter=False):
        colors = ["green", "red", "yellow"]

        for color in colors:
            XlsxReport.__set_color_to_style(style_dict, color)
            self.__add_style(style_name + "_" + color, style_dict)
            if vcenter:
                self.__get_style(style_name + "_" + color).set_align('vcenter')

    def __init_styles(self):
        self.__add_style("default", {'font_name': 'Calibri', 'font_size': 10})

        main_title_style = {'bold': True, 'font_name': 'Times New Roman', 'font_size': 20}
        self.__add_style("main_title", main_title_style)

        main_descr_style = {'bold': False, 'font_name': 'Times New Roman', 'font_size': 10}
        self.__add_style("main_descr", main_descr_style)

        column_base_style = {'bold': True, 'font_name': 'Times New Roman', 'bg_color': '#C0C0C0', 'font_size': 14,
                             'bottom': 1, 'top': 1, 'left': 1, 'align': 'left'}
        self.__add_style("column_first", column_base_style)

        column_base_style['left'] = 0
        column_base_style['align'] = 'left'
        self.__add_style("column_middle_left", column_base_style)

        column_base_style['align'] = 'center'
        self.__add_style("column_middle_center", column_base_style)

        column_base_style['right'] = 1
        column_base_style['align'] = 'left'
        self.__add_style("column_last", column_base_style)

        composite_title_style = {'bold': True, 'font_name': 'Times New Roman', 'left': 5, 'top': 5, 'font_size': 14}
        self.__add_style("composite_title", composite_title_style)

        composite_status_style = {'bold': True, 'font_name': 'Times New Roman', 'top': 5, 'align': 'center',
                                  'font_size': 12}
        self.__add_style("composite_status", composite_status_style)

        composite_title_style['left'] = 0
        composite_title_style['right'] = 5
        self.__add_style("composite_comment", composite_title_style)

        composite_descr_style = {'font_name': 'Calibri', 'font_size': 10, 'bottom': 5, 'left': 5,
                                 'right': 5, 'align': 'vdistributed'}
        self.__add_style("composite_descr", composite_descr_style)

        elementary_title_style = {'font_name': 'Times New Roman', 'font_size': 12,
                                  'bottom': 6, 'left': 6, 'top': 6,
                                  'bold': True,
                                  'align': 'vcenter',
                                  'text_wrap': True}
        self.__add_styles_with_three_colors("elementary_title", elementary_title_style)

        elementary_descr_style = {'font_name': 'Calibri', 'font_size': 10,
                                  'bottom': 6, 'top': 6,
                                  'text_wrap': True}
        self.__add_styles_with_three_colors("elementary_descr", elementary_descr_style)

        elementary_critical_style = {'font_name': 'Calibri', 'font_size': 11,
                                     'bottom': 6, 'top': 6,
                                     'text_wrap': True, 'align': 'left'}
        self.__add_styles_with_three_colors("elementary_critical", elementary_critical_style, True)

        elementary_critical_style['align'] = 'right'
        self.__add_styles_with_three_colors("elementary_critical_icon", elementary_critical_style, True)

        elementary_status_style = {'font_name': 'Calibri', 'font_size': 11,
                                   'bottom': 6, 'top': 6, 'align': 'center',
                                   'text_wrap': True}
        self.__add_styles_with_three_colors("elementary_status", elementary_status_style, True)

        elementary_comment_style = {'font_name': 'Calibri', 'font_size': 10,
                                    'bottom': 6, 'right': 6, 'top': 6,
                                    'text_wrap': True}
        self.__add_styles_with_three_colors("elementary_comment", elementary_comment_style)

    def __del__(self):
        self.close()

    def inc_current_row(self, value=1):
        self.current_row += value

    def __get_style(self, style_name):
        if style_name in self.styles.keys():
            return self.styles[style_name]
        print('Style ' + style_name + ' not found')
        return self.styles['default']

    def insert_main_header(self, main_title, scan_descr, sys_descr):
        self.worksheet.write(self.current_row, self.start_column, main_title, self.__get_style("main_title"))
        self.worksheet.merge_range(self.current_row, self.start_column + 2, self.current_row, self.start_column + 5,
                                   scan_descr, self.__get_style("main_descr"))
        self.inc_current_row()
        self.worksheet.write(self.current_row, self.start_column, sys_descr, self.__get_style("main_descr"))
        self.inc_current_row(2)

    def close(self):
        if self.workbook:
            self.workbook.close()

    def __set_columns_width(self, columns_width):
        for i, column in enumerate(columns_width):
            self.worksheet.set_column(self.start_column + i, self.start_column + i, columns_width[i])

    def insert_columns(self, columns, columns_width):
        self.__set_columns_width(columns_width)

        self.worksheet.write(self.current_row, self.start_column, columns[0], self.__get_style("column_first"))
        self.worksheet.write(self.current_row, self.start_column + 1, columns[1],
                             self.__get_style("column_middle_left"))
        self.worksheet.merge_range(self.current_row, self.start_column + 2, self.current_row, self.start_column + 3,
                                   columns[3], self.__get_style("column_middle_center"))
        self.worksheet.write(self.current_row, self.start_column + 4, columns[4],
                             self.__get_style("column_middle_center"))
        self.worksheet.write(self.current_row, self.start_column + 5, columns[5], self.__get_style("column_last"))

        self.inc_current_row()

    def insert_composite_header(self, title, descr, status):
        self.worksheet.set_row(self.current_row, 3)
        self.worksheet.merge_range(self.current_row, self.start_column, self.current_row, self.start_column + 5,
                                   "", self.__get_style("default"))
        self.inc_current_row()

        self.worksheet.merge_range(self.current_row, self.start_column, self.current_row, self.start_column + 3,
                                   title, self.__get_style("composite_title"))
        self.worksheet.write(self.current_row, self.start_column + 4, status, self.__get_style("composite_status"))
        self.worksheet.write(self.current_row, self.start_column + 5, '', self.__get_style("composite_comment"))
        self.inc_current_row()
        self.worksheet.merge_range(self.current_row, self.start_column, self.current_row, self.start_column + 5,
                                   descr, self.__get_style("composite_descr"))
        self.worksheet.set_row(self.current_row, 13 * ((len(descr)//250) + 1))
        self.inc_current_row()
        self.worksheet.set_row(self.current_row, 3)
        self.worksheet.merge_range(self.current_row, self.start_column, self.current_row, self.start_column + 5,
                                   "", self.__get_style("default"))
        self.inc_current_row()

    @staticmethod
    def __get_critical_int(critical):
        if critical == 'High level':
            return 1
        elif critical == 'Medium level':
            return 2
        else:
            return 3

    def insert_elementary_header(self, title, descr, critical, status, comment):
        if status == SecurityCheckStatus.COMPLIED:
            color = "_green"
        elif status == SecurityCheckStatus.NOT_COMPLIED:
            color = "_red"
        else:
            status = "ERROR"
            color = "_yellow"

        self.worksheet.write(self.current_row, self.start_column, title, self.__get_style("elementary_title" + color))
        self.worksheet.write(self.current_row, self.start_column + 1, descr,
                             self.__get_style("elementary_descr" + color))
        self.worksheet.write(self.current_row, self.start_column + 2, self.__get_critical_int(critical),
                             self.__get_style("elementary_critical_icon" + color))
        self.worksheet.write(self.current_row, self.start_column + 3, critical,
                             self.__get_style("elementary_critical" + color))
        self.worksheet.write(self.current_row, self.start_column + 4, status,
                             self.__get_style("elementary_status" + color))
        self.worksheet.write(self.current_row, self.start_column + 5, comment,
                             self.__get_style("elementary_comment" + color))

        self.worksheet.conditional_format(
            self.current_row, self.start_column + 2, self.current_row, self.start_column + 2,
            {'type': 'icon_set',
             'icon_style': '3_traffic_lights',
             'icons_only': True,
             'icons': [{'criteria': '>=', 'type': 'number', 'value': 3},
                       {'criteria': '<', 'type': 'number', 'value': 2},
                       {'criteria': '>=', 'type': 'number', 'value': 2}]}
        )
        self.inc_current_row()

    def add_filters(self, startpos):
        column_min = 4
        column_max = 5

        self.worksheet.autofilter(startpos - 1, column_min, self.current_row - 1, column_max)
