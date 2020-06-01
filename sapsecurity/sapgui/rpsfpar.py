from .reports import Report
from .saplogon import SAPLogon

RSPFPAR_REPORT = 'RSPFPAR'
PARAM_NAME_FIELD = 'wnd[0]/usr/txtPNAME-LOW'
REPORT_GRID = 'wnd[0]/usr/cntlGRID1/shellcont/shell'


class Rspfpar(Report):
    def __init__(self, param_name, sap_sessoin=None, do_log=False):
        self.param_name = param_name
        super().__init__(RSPFPAR_REPORT, sap_sessoin, do_log)

    def __set_param_name_and_execute(self, sap_session):
        SAPLogon.set_text(sap_session, PARAM_NAME_FIELD, self.param_name)
        SAPLogon.press_keyboard_keys(sap_session, "F8")

    def get_param_value(self, sap_session=None):
        if not sap_session:
            sap_session = self.sap_session

        self.start_report(sap_session)
        self.__set_param_name_and_execute(sap_session)
        result = self.__get_param_from_grid(sap_session)
        if self.do_log:
            print("Parameter {0} is set to ".format(self.param_name, result))
        return result

    def __get_param_from_grid(self, sap_session):
        grid_rows_number = SAPLogon.get_grid_rows_number(sap_session, REPORT_GRID)

        if grid_rows_number != 1:
            msg = "An error occurred while executing the script. Details:\n"
            msg += "Bad parameter name '{0}'. Found {1} parameters".format(self.param_name, grid_rows_number)
            raise ValueError(msg)

        return self.__get_param_value_from_grid(sap_session)

    @staticmethod
    def __get_param_value_from_grid(sap_session):
        row_number = 0

        for column_number in range(1, 4):
            value = SAPLogon.get_value_from_grid(sap_session, REPORT_GRID, row_number, column_number)
            if value:
                return value.strip()

        return ""
