from sapsec.sapgui.reports import Report
from sapsec.sapgui.saplogon import SAPLogon

RSUSR070_REPORT = "RSUSR070"
MAX_AUTH_OBJECTS = 4
MAX_AUTH_VALUES = 4
REPORT_GRID = "wnd[0]/usr/cntlGRID1/shellcont/shell/shellcont[1]/shell"

AUTH_OBJECT_TEMPLATE = "wnd[0]/usr/{type}OBJ{num}"
FIELD_NAME_TEMPLATE = "wnd[0]/usr/txtFTX{num}{num1}"
AUTH_VALUES_TEMPLATE = "wnd[0]/usr/{type}VAL{num}{num1}{num2}"

ROLES_FILTER_BUTTON = "wnd[0]/usr/btn%_ACTGRPS_%_APP_%-VALU_PUSH"
EQUAL_FILTER_TEMPLATE = "wnd[1]/usr/tabsTAB_STRIP/tabpSIVA/ssubSCREEN_HEADER:SAPLALDB:3010/tblSAPLALDBSINGLE" \
                        "/{type}RSCSEL_255-SLOW_I[1,{num}]"
OK_BUTTON = "wnd[1]/tbar[0]/btn[8]"


class Rsusr070(Report):
    def __init__(self, config_file, sap_session=None, do_log=False):
        super().__init__(RSUSR070_REPORT, config_file, sap_session=sap_session, do_log=do_log)

    @staticmethod
    def __set_auth_filter(session, rsusr002_filter):
        for i, auth in enumerate(rsusr002_filter.auth_objects):
            if i >= MAX_AUTH_OBJECTS:
                break
            SAPLogon.try_to_set_text(session, AUTH_OBJECT_TEMPLATE.format(type="{type}", num=i + 1), auth.name)
            SAPLogon.press_keyboard_keys(session, "Enter")

            for k in range(0, 10):
                try:
                    text = SAPLogon.get_text(session, FIELD_NAME_TEMPLATE.format(num=i + 1, num1=k))
                except AttributeError:
                    break
                else:
                    values = auth.get_values_for_field(text)
                    if not values or len(values) == 0:
                        continue

                    for j, value in enumerate(values):
                        if j >= MAX_AUTH_VALUES:
                            break
                        SAPLogon.try_to_set_text(
                            session, AUTH_VALUES_TEMPLATE.format(type="{type}", num=i + 1, num1=k, num2=j + 1), value)

    def __execute_and_return_enties_number(self, session):
        SAPLogon.press_keyboard_keys(session, "F8")
        msg = SAPLogon.get_status_message(session)
        if msg and msg[1] == "265":
            return 0
        elif hasattr(self, "save_to_file") and self.save_to_file:
            self.save(session)

        grid_num = SAPLogon.get_grid_rows_number(session, REPORT_GRID)
        return grid_num

    @staticmethod
    def __set_roles_filter(session, roles_filter):
        SAPLogon.press_button(session, ROLES_FILTER_BUTTON)
        for i, item in enumerate(roles_filter):
            SAPLogon.try_to_set_text(session,
                                     EQUAL_FILTER_TEMPLATE.format(type="{type}", num=i),
                                     item)
        SAPLogon.press_button(session, OK_BUTTON)

    def get_row_number_by_filter(self, sap_session, rsusr070_filter):
        if not sap_session:
            sap_session = self.sap_session
        self.start_report(sap_session)
        if self.problem:
            return

        if len(rsusr070_filter.role_filter) > 0:
            self.__set_roles_filter(sap_session, rsusr070_filter.role_filter)

        if len(rsusr070_filter.auth_objects):
            self.__set_auth_filter(sap_session, rsusr070_filter)

        return self.__execute_and_return_enties_number(sap_session)
