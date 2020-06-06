import yaml
import datetime
import os
import logging
import sapsec.settings
from sapsec.checks.composite_check import CompositeCheck
from sapsec.sapgui.saplogon import SAPLogon
from sapsec.excelreport.report import SecurityReport
from sapsec.checks.users_by_privileges import UsersByPrivileges, RolesByPrivileges
from sapsec.checks.profile_param import CheckProfileParameter
from sapsec.checks.table_entries import CheckTableEntries


class SAPSecurityAnalysis:
    def __init__(self, do_log=True):
        self.composite_checks = list()
        self.sap_session = None
        self.session_info = None
        self.title = ""
        self.descr = ""
        self.do_log = do_log
        self.report_folder = None
        self.open_rep = True
        self.rules_file = None

        self.logger = self.__init_logger()

    @staticmethod
    def __get_own_report_dir():
        local_dir = os.path.abspath(os.getcwd())
        return os.path.join(local_dir, "reports")

    def set_rules_file(self, rules):
        if rules is not None:
            if os.path.exists(rules):
                self.rules_file = rules

    def __create_subdirs(self):
        local_dir = self.report_folder

        sid = self.session_info["sid"]
        local_dir = os.path.join(local_dir, sid)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        date_today = datetime.datetime.now().strftime("%Y%m%d")

        new_dir = os.path.join(local_dir, date_today)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
            self.report_folder = new_dir
            return
        else:
            for i in range(0, 100):
                new_dir = os.path.join(local_dir, date_today + "_" + str(i).zfill(2))
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                    self.report_folder = new_dir
                    return

    def __create_report_folder(self):
        if not self.report_folder:
            if hasattr(sapsec.settings, "REPORT_DIR"):
                local_dir = sapsec.settings.REPORT_DIR
                if not os.path.exists(local_dir):
                    try:
                        os.makedirs(local_dir)
                    except Exception as error:
                        if self.do_log:
                            self.logger.warning(str(error))

                if os.path.exists(local_dir):
                    self.report_folder = local_dir

            if not self.report_folder:
                local_dir = self.__get_own_report_dir()
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)
                self.report_folder = local_dir

            if self.report_folder:
                self.__create_subdirs()
                if self.do_log:
                    self.logger.info("Defined directory to final report {0}".format(self.report_folder))
            else:
                self.logger.error("Report folder not defined")

    def sap_login(self):
        try:
            sap_session, session_info = SAPLogon.get_sap_session_with_info()
        except RuntimeError as error:
            if self.do_log:
                self.logger.error(str(error))
        else:
            self.sap_session = sap_session
            self.session_info = session_info
            self.session_info["date"] = datetime.datetime.now()
            if self.do_log:
                self.logger.info("Successfully connected to {sid}, server {app_server}, user {user} ".format(
                    sid=self.session_info["sid"],
                    app_server=self.session_info["app_server"],
                    user=self.session_info["user"]))

    @staticmethod
    def __init_logger():
        logger = logging.getLogger('sapsec')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def start_analysis(self):
        if self.do_log:
            self.logger.info("-------------------------------------------------------------------")
            self.logger.info("-------------- SAP Logon Application initialization ---------------")
            self.logger.info("-------------------------------------------------------------------")
        self.sap_login()
        if self.sap_session:
            self.__add_config_from_settings()
            self.__create_report_folder()
            if self.do_log:
                self.logger.info("-------------------------------------------------------------------")
                self.logger.info("------------- Loading SAP security checks from config -------------")
                self.logger.info("-------------------------------------------------------------------")
            self.__add_checks()
            if self.do_log:
                self.logger.info("-------------------------------------------------------------------")
                self.logger.info("------------------ SAP security checks execution ------------------")
                self.logger.info("-------------------------------------------------------------------")
            self.__execute_all()
            if self.do_log:
                self.logger.info("-------------------------------------------------------------------")
                self.logger.info("------------------------ Report generating ------------------------")
                self.logger.info("-------------------------------------------------------------------")
            self.__create_report()

    def __add_checks(self):
        self.__add_security_checks()

    def __execute_all(self):
        for check in self.composite_checks:
            if self.do_log:
                self.logger.info("Processing composite check '{0}'".format(check.title.format(**check.__dict__)))
            if check.enable:
                check.execute(self.sap_session)

    @staticmethod
    def open_report(path):
        os.system(r'start Excel.exe "{0}"'.format(path))

    def __create_report(self):
        report = SecurityReport(self, self.report_folder)
        report_path = report.generate_report()
        if self.do_log:
            self.logger.info("Report generated: {0}".format(report_path))
        if self.open_rep:
            self.open_report(report_path)

    def __add_composite_check(self, composite_check):
        enable = composite_check["enable"] if "enable" in composite_check else True
        if not enable:
            return
        title = composite_check["title"] if "title" in composite_check else ""
        descr = composite_check["descr"] if "descr" in composite_check else ""
        do_log = composite_check["do_log"] if "do_log" in composite_check else ""
        new_composite_check = CompositeCheck(title, descr, do_log=do_log)
        new_composite_check.enable = enable
        self.composite_checks.append(new_composite_check)
        if self.do_log:
            self.logger.info("Added composite check with title '{0}'".format(
                new_composite_check.title.format(**new_composite_check.__dict__)))
        if "child_checks" in composite_check:
            for elementary_check in composite_check["child_checks"]:
                new_elementary_check = self.__get_elementary_check(elementary_check)
                if new_elementary_check:
                    new_composite_check.add_check(new_elementary_check)
                    if self.do_log:
                        self.logger.info("Added elementary check '{0}'".format(
                            new_elementary_check.title.format(**new_elementary_check.__dict__)))

    def __get_elementary_check(self, elementary_check):
        enable = elementary_check["enable"] if "enable" in elementary_check else True
        if not enable:
            return
        title = elementary_check["title"] if "title" in elementary_check else ""
        class_name = elementary_check["class"] if "class" in elementary_check else ""
        if not class_name:
            if self.do_log:
                self.logger.warning("Elementary check '{0}' aborted. 'class' not found ".format(title))
            return
        if class_name not in globals():
            if self.do_log:
                self.logger.warning("Elementary check '{0}' aborted. Class {1} not found".format(
                    title, class_name))
            return
        class_id = globals()[class_name]
        descr = elementary_check["descr"] if "descr" in elementary_check else ""
        do_log = elementary_check["do_log"] if "do_log" in elementary_check else ""
        new_elementary_check = class_id(title, descr, do_log)
        new_elementary_check.set_config_file(self.rules_file)
        new_elementary_check.add_additional_parameters(**elementary_check)
        new_elementary_check.folder_to_save = self.report_folder
        return new_elementary_check

    def __add_config_from_settings(self):
        if hasattr(sapsec.settings, "DO_LOG"):
            self.do_log = sapsec.settings.DO_LOG
        if hasattr(sapsec.settings, "OPEN_XLSX_REPORT"):
            self.open_rep = sapsec.settings.OPEN_XLSX_REPORT

    def __add_security_checks(self):
        if self.rules_file is None:
            if hasattr(sapsec.settings, "CONFIG_FILE"):
                config_file = sapsec.settings.CONFIG_FILE
                if os.path.exists(config_file):
                    self.rules_file = config_file
                else:
                    for i in range(0, len(sapsec.__path__)):
                        if os.path.exists(os.path.join(sapsec.__path__[i], config_file)):
                            self.rules_file = os.path.join(sapsec.__path__[i], config_file)
                            break
        if self.rules_file is None:
            self.logger.error("File with security checks configuration not found")
            return

        with open(self.rules_file) as file:
            if self.do_log:
                self.logger.info("Loading security checks from file {0}".format(self.rules_file))
            yaml_dict = yaml.full_load(file)

            if "security_checks" not in yaml_dict:
                if self.do_log:
                    self.logger.warning("Security checks not found in config file")

            for composite_check in yaml_dict["security_checks"]:
                self.__add_composite_check(composite_check)
