import os
from .saplogon import SAPLogon
import sapsec.settings

SUPPORTED_FORMAT = ['txt', 'html']
DEFAULT_FILE_FORMAT = 'html'
HTML_FORMAT = "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[3,0]"
CONFIRM_FORMAT_BUTTON = "wnd[1]/tbar[0]/btn[0]"
REPLACE_BUTTON = "wnd[1]/tbar[0]/btn[11]"
PATH_TEXT_FIELD = "wnd[1]/usr/ctxtDY_PATH"
FILENAME_TEXT_FIELD = "wnd[1]/usr/ctxtDY_FILENAME"


class SaveToFile:
    file_format = None

    def __init__(self, report_dir, sap_session=None):
        self.sap_session = sap_session
        self.report_dir = report_dir
        self.__load_configuration()

    @staticmethod
    def __load_configuration():
        if not SaveToFile.file_format:
            if hasattr(sapsec.settings, "SAVE_TO_FILE_FORMAT"):
                SaveToFile.file_format = sapsec.settings.SAVE_TO_FILE_FORMAT

            if not SaveToFile.file_format:
                SaveToFile.file_format = DEFAULT_FILE_FORMAT

    def __get_filename(self):
        file_template = "additional_report_{0}{1}"
        if self.file_format == 'html':
            file_extension = ".html"
        else:
            file_extension = ".txt"

        for i in range(0, 100):
            new_file = file_template.format(str(i).zfill(2), file_extension)
            if not os.path.exists(os.path.join(self.report_dir, new_file)):
                return new_file

    def __del_gif_files(self):
        folder = os.path.split(self.report_dir)[0]

        files_in_directory = os.listdir(folder)
        filtered_files = [file for file in files_in_directory if file.endswith(".gif")]
        for file in filtered_files:
            path_to_file = os.path.join(folder, file)
            os.remove(path_to_file)

    def save_to_file(self, sap_session=None):
        if not sap_session:
            sap_session = self.sap_session
        SAPLogon.press_keyboard_keys(sap_session, "Ctrl+Shift+F9")
        if self.file_format == 'html':
            SAPLogon.select_element(sap_session, HTML_FORMAT)
        SAPLogon.press_button(sap_session, CONFIRM_FORMAT_BUTTON)
        SAPLogon.set_text(sap_session, PATH_TEXT_FIELD, self.report_dir)
        SAPLogon.set_text(sap_session, FILENAME_TEXT_FIELD, self.__get_filename())
        SAPLogon.press_button(sap_session, REPLACE_BUTTON)
        self.__del_gif_files()
