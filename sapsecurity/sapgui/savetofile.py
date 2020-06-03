import yaml
import os
from .saplogon import SAPLogon
from sapsecurity.settings import CONFIG_FILE

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
            with open(CONFIG_FILE) as file:
                yaml_dict = yaml.full_load(file)

                if "save_to_file_format" in yaml_dict:
                    if yaml_dict["save_to_file_format"] in SUPPORTED_FORMAT:
                        SaveToFile.file_format = yaml_dict["save_to_file_format"]

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

    def __del_gif_file(self):
        path = os.path.split(self.report_dir)[0]
        folder = os.path.split(self.report_dir)[1]

        gif_extension = "s_b_spce.gif"
        if os.path.exists(os.path.join(path, folder + gif_extension)):
            os.remove(os.path.join(path, folder + gif_extension))

        gif_extension = "s_actgro.gif"
        if os.path.exists(os.path.join(path, folder + gif_extension)):
            os.remove(os.path.join(path, folder + gif_extension))

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
        self.__del_gif_file()
