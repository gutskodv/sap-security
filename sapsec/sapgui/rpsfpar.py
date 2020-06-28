from .reports import Report
from pysapgui.sapguielements import SAPGuiElements
from pysapgui.alv_grid import SAPAlvGrid

RSPFPAR_REPORT = 'RSPFPAR'
PARAM_NAME_FIELD = 'wnd[0]/usr/txtPNAME-LOW'
REPORT_GRID = 'wnd[0]/usr/cntlGRID1/shellcont/shell'


class Rspfpar(Report):
    def __init__(self, param_name, config_file, sap_session=None, do_log=False):
        self.param_name = param_name
        super().__init__(RSPFPAR_REPORT, config_file, sap_session, do_log)

    def __set_param_name_and_execute(self, sap_session):
        SAPGuiElements.set_text(sap_session, PARAM_NAME_FIELD, self.param_name)
        SAPGuiElements.press_keyboard_keys(sap_session, "F8")

    def get_param_value(self, sap_session=None):
        if not sap_session:
            sap_session = self.sap_session

        self.start_report(sap_session)
        self.__set_param_name_and_execute(sap_session)
        result = self.__get_param_from_grid(sap_session)
        return result

    def __get_param_from_grid(self, sap_session):
        grid = SAPAlvGrid(sap_session, REPORT_GRID)
        grid_rows_number = grid.get_row_count()

        if grid_rows_number != 1:
            msg = "Bad parameter name '{0}'. Found {1} parameters".format(self.param_name, grid_rows_number)
            raise ValueError(msg)

        return self.__get_param_value_from_grid(sap_session)

    @staticmethod
    def __get_param_value_from_grid(sap_session):
        row_number = 0
        grid = SAPAlvGrid(sap_session, REPORT_GRID)

        for column_number in range(1, 4):
            value = grid.get_cell(row_number, column_number)
            if value:
                return value.strip()

        return ""
