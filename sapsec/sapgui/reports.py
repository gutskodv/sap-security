import yaml
import os
from .transactions import TCode
from .saplogon import SAPLogon
from .savetofile import SaveToFile

SA38_TCODE = 'SA38'
SE38_TCODE = 'SE38'
DEFAULT_TCODE = SA38_TCODE
PROGRAM_FIELD = 'wnd[0]/usr/ctxtRS38M-PROGRAMM'


class Report:
    tcode_to_start_report = None

    def __init__(self, report_name, config_file, sap_session=None, do_log=False):
        self.save_to_file = True
        self.report_name = report_name
        self.sap_session = sap_session
        self.do_log = do_log
        Report.load_tcode_to_start_report(config_file)
        self.problem = None
        self.problem_text = ""
        self.folder_to_save = ""
        self.save_to_file = False
        self.config_file = None

    def set_config_file(self, config_file):
        self.config_file = config_file

    @staticmethod
    def load_tcode_to_start_report(config_file):
        if Report.tcode_to_start_report:
            return
        if not config_file or not os.path.exists(config_file):
            return

        with open(config_file) as file:
            yaml_dict = yaml.full_load(file)

            if "tcode_to_execute_reports" in yaml_dict:
                if yaml_dict['tcode_to_execute_reports'].upper() == SA38_TCODE:
                    Report.tcode_to_start_report = SA38_TCODE
                elif yaml_dict['tcode_to_execute_reports'].upper() == SE38_TCODE:
                    Report.tcode_to_start_report = SE38_TCODE

        if not Report.tcode_to_start_report:
            Report.tcode_to_start_report = DEFAULT_TCODE

    def __set_report_and_execute(self, sap_session):
        SAPLogon.set_text(sap_session, PROGRAM_FIELD, self.report_name)
        SAPLogon.press_keyboard_keys(sap_session, "F8")
        gui_msg = SAPLogon.get_status_message(sap_session)

        if gui_msg:
            if gui_msg[1] == "017":
                msg = "Wrong report name '{0}'. GUI Message: {1}".format(self.report_name, gui_msg[2])
                raise ValueError(msg)

            elif gui_msg[1] == "322":
                msg = "Not authorized to execute '{0}' report. GUI Message: {1}".format(self.report_name, gui_msg[2])
                raise PermissionError(msg)

    def start_report(self, sap_session=None):
        if not sap_session:
            sap_session = self.sap_session

        transaction = TCode(Report.tcode_to_start_report, sap_session)
        transaction.call_transaction()

        self.__set_report_and_execute(sap_session)

    def need_to_save(self, folder_to_save):
        self.folder_to_save = folder_to_save
        self.save_to_file = True

    def save(self, sap_session=None):
        if not sap_session:
            sap_session = self.sap_session
        dialog = SaveToFile(self.folder_to_save, sap_session)
        dialog.save_to_file()
