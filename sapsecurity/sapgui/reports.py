import yaml
from .transactions import TCode
from .saplogon import SAPLogon
from sapsecurity.settings import CONFIG_FILE
from .savetofile import SaveToFile

SA38_TCODE = 'SA38'
SE38_TCODE = 'SE38'
DEFAULT_TCODE = SA38_TCODE
PROGRAM_FIELD = 'wnd[0]/usr/ctxtRS38M-PROGRAMM'


class Report:
    tcode_to_start_report = None

    def __init__(self, report_name, sap_session=None, do_log=False):
        self.report_name = report_name
        self.load_tcode_to_start_report()
        self.sap_session = sap_session
        self.do_log = do_log
        self.problem = None
        self.problem_text = ""

    def load_tcode_to_start_report(self):
        if self.tcode_to_start_report:
            return

        with open(CONFIG_FILE) as file:
            yaml_dict = yaml.full_load(file)

            if "tcode_to_execute_reports" in yaml_dict:
                if yaml_dict['tcode_to_execute_reports'].upper() == SA38_TCODE:
                    self.tcode_to_start_report = SA38_TCODE
                elif yaml_dict['tcode_to_execute_reports'].upper() == SE38_TCODE:
                    self.tcode_to_start_report = SE38_TCODE

        if not self.tcode_to_start_report:
            self.tcode_to_start_report = DEFAULT_TCODE

    def __set_report_and_execute(self, sap_session):
        SAPLogon.set_text(sap_session, PROGRAM_FIELD, self.report_name)
        SAPLogon.press_keyboard_keys(sap_session, "F8")
        gui_msg = SAPLogon.get_status_message(sap_session)

        if gui_msg:
            if gui_msg[1] == "017":
                msg = "An error occurred while executing the script. Details:\n"
                msg += "Wrong report name '{0}'. GUI Message: {1}".format(self.report_name, gui_msg)
                raise ValueError(msg)

            elif gui_msg[1] == "322":
                msg = "An error occurred while executing the script. Details:\n"
                msg += "Not authorized to execute '{0}' report. GUI Message: {1}".format(self.report_name, gui_msg)
                raise PermissionError(msg)

    def start_report(self, sap_session=None):
        if not sap_session:
            sap_session = self.sap_session

        transaction = TCode(self.tcode_to_start_report, sap_session)
        transaction.call_transaction()

        self.__set_report_and_execute(sap_session)

    def need_to_save(self, folder_to_save):
        self.save_to_file = True
        self.folder_to_save = folder_to_save

    def save(self, sap_session):
        dialog = SaveToFile(self.folder_to_save, sap_session)
        dialog.save_to_file()

