import yaml
import datetime
import os
from sapsecurity.checks.composite_check import CompositeCheck
from sapsecurity.sapgui.saplogon import SAPLogon
from sapsecurity.excelreport.report import SecurityReport
from sapsecurity.settings import CONFIG_FILE
from sapsecurity.checks.users_by_privileges import UsersByPrivileges, RolesByPrivileges
from sapsecurity.checks.profile_param import CheckProfileParameter
from sapsecurity.checks.table_entries import CheckTableEntries


class SAPSecurityAnalysis:
    def __init__(self, title, descr=None, do_log=True):
        self.date_scan = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
        self.composite_checks = list()
        self.sap_session = None
        self.session_info = None
        self.title = title
        self.descr = descr
        self.do_log = do_log
        self.report_folder = None

    def __create_report_folder(self):
        if not self.report_folder:
            local_dir = os.path.abspath(os.getcwd())
            sid = self.session_info["sid"]
            local_dir = os.path.join(local_dir, "reports")
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            local_dir = os.path.join(local_dir, sid)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            date_today = datetime.datetime.now().strftime("%Y%m%d")

            new_dir = os.path.join(local_dir, date_today)
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
                self.report_folder = new_dir
            else:
                for i in range(0, 100):
                    new_dir = os.path.join(local_dir, date_today + "_" + str(i).zfill(2))
                    if not os.path.exists(new_dir):
                        os.makedirs(new_dir)
                        self.report_folder = new_dir
                        break

    def __add_composite_check(self, composite_check):
        self.composite_checks.append(composite_check)

    def sap_login(self):
        try:
            sap_session, session_info = SAPLogon.get_sap_session_with_info()
        except RuntimeError as error:
            print(str(error))
        else:
            self.sap_session = sap_session
            self.session_info = session_info
            self.__create_report_folder()

    def start_analysis(self):
        self.sap_login()
        if self.sap_session:
            self.__add_checks()
            self.__execute_all()
            self.__create_report()

    def __add_checks(self):
        self.__add_security_checks()

    def __execute_all(self):
        for check in self.composite_checks:
            if check.enable:
                check.execute(self.sap_session)
                if self.do_log:
                    print("Check '{title}' complited with status - {status}".format(
                        title=check.title.format(**check.__dict__),
                        status=check.status))

    def __create_report(self):
        report = SecurityReport(self, self.report_folder)
        report.generate_report()

    def __add_security_checks(self):
        with open(CONFIG_FILE) as file:
            yaml_dict = yaml.full_load(file)

            if "main_title" in yaml_dict:
                self.title = yaml_dict["main_title"]

            if "security_checks" not in yaml_dict:
                if self.do_log:
                    print("Security checks not found in config file")

            for composite_check in yaml_dict["security_checks"]:
                enable = composite_check["enable"] if "enable" in composite_check else True
                if not enable:
                    continue
                title = composite_check["title"] if "title" in composite_check else ""
                descr = composite_check["descr"] if "descr" in composite_check else ""
                do_log = composite_check["do_log"] if "do_log" in composite_check else ""
                new_composite_check = CompositeCheck(title, descr, do_log=do_log)
                new_composite_check.enable = enable
                self.composite_checks.append(new_composite_check)
                if self.do_log:
                    print("Composite check with title '{0}' added".format(
                        new_composite_check.title.format(new_composite_check.__dict__)))
                if "child_checks" in composite_check:
                    for elementary_check in composite_check["child_checks"]:
                        enable = elementary_check["enable"] if "enable" in elementary_check else True
                        if not enable:
                            continue
                        title = elementary_check["title"] if "title" in elementary_check else ""
                        descr = elementary_check["descr"] if "descr" in elementary_check else ""
                        do_log = elementary_check["do_log"] if "do_log" in elementary_check else ""
                        class_name = elementary_check["class"] if "class" in elementary_check else ""

                        if not class_name:
                            if self.do_log:
                                print("Elementary check with title '{0}' aborted. 'class' not found ".format(title))
                            continue
                        if class_name not in globals():
                            if self.do_log:
                                print("Elementary check with title '{0}' aborted. Class {1} not found".format(
                                    title, class_name))
                            continue
                        class_id = globals()[class_name]
                        new_elementary_check = class_id(title, descr, do_log)
                        new_elementary_check.add_additional_parameters(**elementary_check)
                        new_elementary_check.folder_to_save = self.report_folder
                        new_composite_check.add_check(new_elementary_check)
                        if self.do_log:
                            print("Elementary check with title '{0}' added".format(
                                new_elementary_check.title.format(**new_elementary_check.__dict__)))
