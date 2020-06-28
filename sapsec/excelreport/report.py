import os
import sapsec.settings
from .xlsxreport import XlsxReport

DEFAULT_REPORT_NAME = "sapresults.xlsx"
DEFAULT_TITLE = "SAP Security Analysis Report"


class SecurityReport:
    def __init__(self, main_process, folder_report):
        self.main_process = main_process
        self.dir = folder_report
        self.filename = self.__get_report_name()

    def __get_report_title(self):
        if hasattr(sapsec.settings, "MAIN_REPORT_TITLE"):
            session, session_info = self.main_process.sap_sessions[0]
            return sapsec.settings.MAIN_REPORT_TITLE.format(**session_info)
        return DEFAULT_TITLE

    def __get_report_name(self):
        if hasattr(sapsec.settings, "REPORT_FILE_NAME"):
            session, session_info = self.main_process.sap_sessions[0]
            return sapsec.settings.REPORT_FILE_NAME.format(**session_info)
        return DEFAULT_REPORT_NAME

    def __get_scan_descr(self):
        descr = list()
        session, session_info = self.main_process.sap_sessions[0]
        if "date" in session_info.keys():
            descr.append("Scan Date: {datescan}".format(
                datescan=session_info["date"].strftime("%d-%b-%Y (%H:%M)")))
        if "user" in session_info.keys():
            descr.append("SAP User: {user}".format(user=session_info["user"]))
        return ", ".join(descr)

    def __get_system_descr(self):
        descr = list()
        session, session_info = self.main_process.sap_sessions[0]
        if True:
            if "sid" in session_info.keys():
                descr.append("SAP system: {sid}".format(sid=session_info["sid"]))
            if "client" in session_info.keys():
                descr.append("Client: {client}".format(client=session_info["client"]))
            if "app_server" in session_info.keys():
                descr.append("Application server: {app_server}".format(
                    app_server=session_info["app_server"]))
        return ", ".join(descr)

    def generate_report(self):
        main_report = XlsxReport(os.path.join(self.dir, self.filename), "Results")

        main_report.insert_main_header(self.__get_report_title(), self.__get_scan_descr(), self.__get_system_descr())

        columns = {'Security Check Title': 80,
                   'Description': 40,
                   '': 5,
                   'Critical Level': 20,
                   'Status': 25,
                   'Comment': 30}
        main_report.insert_columns(list(columns.keys()), list(columns.values()))
        start_filter_pos = main_report.current_row
        for composite_check in self.main_process.composite_checks:
            main_report.insert_composite_header(composite_check.title, composite_check.descr.strip(),
                                                "GL_" + composite_check.status)
            for elementary_check in composite_check.checks:
                main_report.insert_elementary_header(elementary_check.title.format(**elementary_check.__dict__),
                                                     elementary_check.descr.format(**elementary_check.__dict__).strip(),
                                                     elementary_check.critical,
                                                     elementary_check.status,
                                                     elementary_check.comment.strip())
        main_report.add_filters(start_filter_pos)
        main_report.close()
        return os.path.join(self.dir, self.filename)
