# -*- coding: utf-8 -*-
from sapsec.sapgui.saplogon import SAPLogon, GUI_CHILD_USERAREA1, GUI_CHILD_WINDOW1, GUI_MAIN_WINDOW
from sapsec.sapgui.transactions import TCode

SE16_TCODE = 'SE16'
TABLENAME_FIELD = "wnd[0]/usr/ctxtDATABROWSE-TABLENAME"
MENU_FIELDS_FOR_SELECTION = ["Поля для выбора", "Fields for Selection", "Felder für Selektion"]
MENU_USER_PARAMETERS = ["ПользовПараметры...", "User Parameters...", "Benutzerparameter..."]
OK_BUTTON = 'wnd[1]/tbar[0]/btn[0]'
FIELD_NAME_SELECTION = "wnd[1]/usr/tabsG_TABSTRIP/tabp0400/ssubTOOLAREA:SAPLWB_CUSTOMIZING:0400/radSEUCUSTOM-FIELDNAME"
ALV_GRID_SELECTION = "wnd[1]/usr/tabsG_TABSTRIP/tabp0400/ssubTOOLAREA:SAPLWB_CUSTOMIZING:0400/radRSEUMOD-TBALV_GRID"
EXCLUDE_VALUES = "wnd[1]/usr/tabsTAB_STRIP/tabpNOSV"
INCLUDE_VALUES = "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA"
INCLUDE_VALUES_TEMPLATE = "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE" \
                          "/{type}RSCSEL_255-SLOW_I[1,{row}]"
INCLUDE_VALUES_BUTTON = "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE" \
                        "/btnRSCSEL_255-SOP_I[0,{0}]"
EXCLUDE_VALUES_TEMPLATE = "wnd[1]/usr/tabsTAB_STRIP/tabpNOSV/ssubSCREEN_HEADER:SAPLALDB:3030/tblSAPLALDBSINGLE_E" \
                         "/{type}RSCSEL_255-SLOW_E[1,{row}]"
EXCLUDE_VALUES_BUTTON = "wnd[1]/usr/tabsTAB_STRIP/tabpNOSV/ssubSCREEN_HEADER:SAPLALDB:3030/tblSAPLALDBSINGLE_E" \
                        "/btnRSCSEL_255-SOP_E[0,{0}]"
OK_BUTTON_FILTER = "wnd[2]/tbar[0]/btn[0]"
ROW_NUMBER_BUTTON = 'wnd[0]/tbar[1]/btn[31]'
NUMBER_ENTRIES_FIELD = 'wnd[1]/usr/txtG_DBCOUNT'


class FieldFilters:
    def __init__(self, do_log=False):
        self.filters = list()
        self.do_log = do_log

    def __bool__(self):
        return True if len(self.filters) else False

    def __str__(self):
        out_list = list()
        out_list.append("Filter")

        for item in self.filters:
            out_list.append(str(item))

        return "\n".join(out_list)

    def add_filter(self, field_filter):
        self.filters.append(field_filter)

    def init_filter_by_dict(self, filterlist):
        for item in filterlist:
            if "field_name" not in item:
                continue
            field_name = item['field_name']
            new_filter = FieldFilter(field_name)
            if "exclude_values" in item:
                new_filter.set_exclude_values(item['exclude_values'])
            if "equal_values" in item:
                new_filter.set_equal_values(item['equal_values'])
            self.add_filter(new_filter)

    def enable_columns_to_filter(self, session):
        column_list = [filter1.field_name for filter1 in self.filters]
        if not len(column_list):
            return

        SAPLogon.call_menu(session, MENU_FIELDS_FOR_SELECTION)
        max_scroll = int(SAPLogon.get_max_scroll_position(session, GUI_CHILD_USERAREA1))
        pos_scroll = 0
        startpos = 5
        do_cycle = True
        while do_cycle:
            SAPLogon.set_scroll_position(session, pos_scroll, GUI_CHILD_USERAREA1)
            max_i = 0
            for i, element in SAPLogon.iter_elements_by_template(session,
                                                                 GUI_CHILD_USERAREA1,
                                                                 "wnd[1]/usr/lbl[4,{0}]",
                                                                 startpos):
                max_i = i
                if element.text in column_list:
                    SAPLogon.set_checkbox(session, "wnd[1]/usr/chk[2,{0}]".format(i))
            if pos_scroll < max_scroll:
                new_pos_scroll = min(pos_scroll + max_i, max_scroll)
                startpos = max_i - (new_pos_scroll - pos_scroll) + 1
                pos_scroll = new_pos_scroll
            else:
                do_cycle = False

        SAPLogon.press_keyboard_keys(session, "Enter", GUI_CHILD_WINDOW1)

    def get_filter_by_field_name(self, field_name):
        for field_filter in self.filters:
            if field_filter.field_name == field_name:
                return field_filter

    def set_filter_value(self, session):
        if not len(self.filters):
            return

        columnlist = [filter1.field_name for filter1 in self.filters]

        startpos = 1
        for i, element in SAPLogon.iter_elements_by_template(session,
                                                             GUI_MAIN_WINDOW,
                                                             "wnd[0]/usr/txt%_I{0}_%_APP_%-TEXT",
                                                             startpos):
            element_text = element.text
            if element_text in columnlist:
                element_id = element.id
                button_id = element_id.replace("txt", "btn").replace("-TEXT", "-VALU_PUSH")
                SAPLogon.press_button(session, button_id)
                field_filter = self.get_filter_by_field_name(element_text)
                field_filter.set_filter(session)


class FieldFilter:
    def __init__(self, field_name):
        self.field_name = field_name

    def __str__(self):
        out_list = list()
        out_list.append("Field: %s" % (self.field_name,))
        if hasattr(self, "exclude_single_values") and self.exclude_single_values:
            out_list.append("Exclude: %s" % (", ".join(self.exclude_single_values)))
        if hasattr(self, "equal_single_values") and self.equal_single_values:
            out_list.append("Equal: %s" % (", ".join(self.equal_single_values)))

        return ", ".join(out_list)

    def set_equal_values(self, values):
        self.equal_single_values = list()
        if type(values) is list:
            if len(values) == 1 and values[0] is None:
                self.equal_single_values.append("")
            else:
                self.equal_single_values.extend(values)
        else:
            self.equal_single_values.append(values)

    def set_exclude_values(self, values):
        self.exclude_single_values = list()
        if type(values) is list:
            if len(values) == 1 and values[0] is None:
                self.exclude_single_values.append("")
            else:
                self.exclude_single_values.extend(values)
        else:
            self.exclude_single_values.append(values)

    def set_range_values(self, values):
        self.equal_range_values = list()
        if type(values) is list:
            self.equal_range_values.extend(values)
        else:
            self.equal_range_values.append(values)

    def set_exclude_range_values(self, values):
        self.exclude_range_values = list()
        if type(values) is list:
            self.exclude_range_values.extend(values)
        else:
            self.exclude_range_values.append(values)

    def set_filter(self, session):
        SAPLogon.press_keyboard_keys(session, "Shift+F4")
        if hasattr(self, "exclude_single_values"):
            if len(self.exclude_single_values):
                SAPLogon.select_element(session, EXCLUDE_VALUES)
                for i, item in enumerate(self.exclude_single_values):
                    if item == "":
                        SAPLogon.press_button(session, EXCLUDE_VALUES_BUTTON.format(i))
                        SAPLogon.press_button(session, OK_BUTTON_FILTER)
                    else:
                        SAPLogon.try_to_set_text(session, EXCLUDE_VALUES_TEMPLATE.format(type="{type}", row=i), item)

        if hasattr(self, "equal_single_values"):
            if len(self.equal_single_values):
                SAPLogon.select_element(session, INCLUDE_VALUES)
                for i, item in enumerate(self.equal_single_values):
                    if item == "":
                        SAPLogon.press_button(session, INCLUDE_VALUES_BUTTON.format(i))
                        SAPLogon.press_button(session, OK_BUTTON_FILTER)
                    else:
                        SAPLogon.try_to_set_text(session, INCLUDE_VALUES_TEMPLATE.format(type="{type}", row=i), item)

        SAPLogon.press_keyboard_keys(session, "F8")


class TCodeSE16(TCode):
    first_call = True

    def __init__(self, table_name, sap_session=None, do_log=False):
        super().__init__(SE16_TCODE, sap_session, do_log)
        self.table_name = table_name
        self.problem = None

    def __get_entries_number(self, session):
        SAPLogon.press_keyboard_keys(session, "Ctrl+F7")
        entries_num = SAPLogon.get_text(session, NUMBER_ENTRIES_FIELD)
        SAPLogon.press_keyboard_keys(session, "Enter", GUI_CHILD_WINDOW1)
        return self.__parse_val(entries_num)

    @staticmethod
    def __parse_val(value):
        return value.replace('.', '').replace(',', '').replace(' ', '')

    def get_row_number_by_filter(self, sap_session, table_filter=None):
        if not sap_session:
            sap_session = self.sap_session
        self.call_transaction(sap_session)
        self.__set_table_name(sap_session)

        if TCodeSE16.first_call:
            TCodeSE16.__set_se16_parameters(sap_session)

        if table_filter:
            table_filter.enable_columns_to_filter(sap_session)
            table_filter.set_filter_value(sap_session)
        return self.__get_entries_number(sap_session)

    def __set_table_name(self, session):
        SAPLogon.set_text(session, TABLENAME_FIELD, self.table_name)
        SAPLogon.press_keyboard_keys(session, "Enter")
        gui_msg = SAPLogon.get_status_message(session)

        if gui_msg:
            if gui_msg[1] == "402":
                msg = "Table '{0}' not found. GUI Message: {1}".format(self.table_name, gui_msg)
                raise ValueError(msg)
            elif gui_msg[1] == "419":
                msg = "Not authorized to view the '{0}' table. GUI Message: {1}".format(self.table_name, gui_msg[2])
                raise PermissionError(msg)

    @staticmethod
    def __set_se16_parameters(session):
        SAPLogon.call_menu(session, MENU_USER_PARAMETERS)
        SAPLogon.select_element(session, FIELD_NAME_SELECTION)
        SAPLogon.select_element(session, ALV_GRID_SELECTION)
        SAPLogon.press_keyboard_keys(session, "Enter", GUI_CHILD_WINDOW1)
        TCodeSE16.first_call = False
