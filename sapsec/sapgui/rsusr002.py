from sapsec.sapgui.reports import Report
from pysapgui.sapguielements import SAPGuiElements
from pysapgui.alv_grid import SAPAlvGrid

RSUSR002_REPORT = "RSUSR002"
MAX_AUTH_OBJECTS = 4
MAX_AUTH_VALUES = 4
ACTIVE_USERS_ONLY = "wnd[0]/usr/tabsTABSTRIP_TAB/tabpTAB1/ssub%_SUBSCREEN_TAB:RSUSR002:1001/radUNLOCK"
USER_TYPE_FILTER_BUTTON = "wnd[0]/usr/tabsTABSTRIP_TAB/tabpTAB1/ssub%_SUBSCREEN_TAB:RSUSR002:1001/btn%_UTYPE_%_APP_" \
                          "%-VALU_PUSH"
INCLUDE_VALUES_TEMPLATE = "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE/{" \
                          "type}RSCSEL_255-SLOW_I[1,{row}]"
OK_BUTTON = "wnd[1]/tbar[0]/btn[8]"
AUTH_OBJECT_TEMPLATE = "wnd[0]/usr/tabsTABSTRIP_TAB/tabpTAB4/ssub%_SUBSCREEN_TAB:RSUSR002:1004/{type}OBJ{num}"
AUTH_VALUES_TEMPLATE = "wnd[0]/usr/tabsTABSTRIP_TAB/tabpTAB4/ssub%_SUBSCREEN_TAB:RSUSR002:1004/{type}VAL{num}{num1}{" \
                       "num2}"
PRIVILEGE_TAB = "wnd[0]/usr/tabsTABSTRIP_TAB/tabpTAB4"
LOGON_TAB = "wnd[0]/usr/tabsTABSTRIP_TAB/tabpTAB1"
FIELD_NAME_TEMPLATE = "wnd[0]/usr/tabsTABSTRIP_TAB/tabpTAB4/ssub%_SUBSCREEN_TAB:RSUSR002:1004/txtFTX{num}{num1}"
REPORT_GRID = "wnd[0]/usr/cntlGRID1/shellcont/shell/shellcont[1]/shell"


class Rsusr002Filter:
    def __init__(self):
        self.active_users = False
        self.filter_user_type = list()
        self.role_filter = list()
        self.auth_objects = list()

    def __add_auth_object(self, ao):
        self.auth_objects.append(ao)

    def init_filter_by_dict(self, indict):
        if "active_users_filter" in indict:
            self.active_users = indict["active_users_filter"]

        if "user_type_filter" in indict:
            self.filter_user_type.extend(indict["user_type_filter"])

        if "role_filter" in indict:
            self.role_filter.extend(indict["role_filter"])

        if "privilege_filter" in indict:
            for privilege in indict["privilege_filter"]:
                if "auth_object" in privilege and "auth_values" in privilege:
                    new_ao = AuthObject(privilege["auth_object"])
                    new_ao.get_privileges_from_dict(privilege["auth_values"])
                    self.__add_auth_object(new_ao)


class AuthObject:
    def __init__(self, name):
        self.name = name
        self.privileges = list()

    def get_privileges_from_dict(self, privileges):
        for item in privileges:
            if "auth_field" in item and "values" in item:
                self.privileges.append((item["auth_field"], item["values"]))

    def get_values_for_field(self, field_name):
        for field, values in self.privileges:
            if field_name.startswith(field):
                return values


class Rsusr002(Report):
    def __init__(self, config_file, sap_session=None, do_log=False):
        super().__init__(RSUSR002_REPORT, config_file, sap_session=sap_session, do_log=do_log)

    @staticmethod
    def __set_active_users_only(session):
        SAPGuiElements.select_element(session, ACTIVE_USERS_ONLY)

    @staticmethod
    def __set_filter_by_user_type(session, user_types):
        SAPGuiElements.press_button(session, USER_TYPE_FILTER_BUTTON)
        for i, user_type in enumerate(user_types):
            SAPGuiElements.try_to_set_text(session,
                                     INCLUDE_VALUES_TEMPLATE.format(type="{type}", row=i),
                                     user_type)
        SAPGuiElements.press_button(session, OK_BUTTON)

    @staticmethod
    def __set_auth_filter(session, rsusr002_filter):
        SAPGuiElements.select_element(session, PRIVILEGE_TAB)

        for i, auth in enumerate(rsusr002_filter.auth_objects):
            if i >= MAX_AUTH_OBJECTS:
                break

            SAPGuiElements.try_to_set_text(session, AUTH_OBJECT_TEMPLATE.format(type="{type}", num=i + 1), auth.name)
            SAPGuiElements.press_keyboard_keys(session, "Enter")

            for k in range(0, 10):
                try:
                    text = SAPGuiElements.get_text(session, FIELD_NAME_TEMPLATE.format(num=i + 1, num1=k))
                except AttributeError:
                    break
                else:
                    values = auth.get_values_for_field(text)

                    if not values or len(values) == 0:
                        continue

                    for j, value in enumerate(values):
                        if j >= MAX_AUTH_VALUES:
                            break
                        SAPGuiElements.try_to_set_text(session,
                                                 AUTH_VALUES_TEMPLATE.format(type="{type}",
                                                                             num=i + 1, num1=k, num2=j + 1),
                                                 value)

    def __execute_and_return_entries_number(self, session):
        SAPGuiElements.press_keyboard_keys(session, "F8")
        gui_msg = SAPGuiElements.get_status_message(session)

        if gui_msg and gui_msg[1] == "485":
            msg = "Not authorized to analyze privileges. GUI Message: {0}".format(gui_msg[2])
            raise PermissionError(msg)
        elif gui_msg and gui_msg[1] == "265":
            return 0
        elif hasattr(self, "save_to_file") and self.save_to_file:
            filename = self.save(session)
            self.comment = '=HYPERLINK("{0}", "more details")'.format(filename)

        grid = SAPAlvGrid(session, REPORT_GRID)
        grid_num = grid.get_row_count()
        return grid_num

    def get_row_number_by_filter(self, sap_session, rsusr002_filter):
        if not sap_session:
            sap_session = self.sap_session
        self.start_report(sap_session)

        SAPGuiElements.select_element(sap_session, LOGON_TAB)
        if rsusr002_filter.active_users:
            self.__set_active_users_only(sap_session)

        if len(rsusr002_filter.filter_user_type):
            self.__set_filter_by_user_type(sap_session, rsusr002_filter.filter_user_type)

        if len(rsusr002_filter.auth_objects):
            self.__set_auth_filter(sap_session, rsusr002_filter)

        return self.__execute_and_return_entries_number(sap_session)
