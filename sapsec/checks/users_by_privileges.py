import yaml
import os
from sapsec.checks.table_check import TableCheck
from sapsec.settings import CONFIG_FILE
from sapsec.sapgui.rsusr002 import Rsusr002Filter, Rsusr002
from sapsec.sapgui.rsusr070 import Rsusr070


class RsusrCheck(TableCheck):
    def get_table_filter(self, filter_name):
        if not self.config_file or not os.path.exists(self.config_file):
            return

        with open(self.config_file) as file:
            yaml_dict = yaml.full_load(file)

            if "rsusr_filters" in yaml_dict:
                if filter_name in yaml_dict["rsusr_filters"]:
                    filter_dict = yaml_dict["rsusr_filters"][filter_name]

                    outfilter = Rsusr002Filter()
                    outfilter.init_filter_by_dict(filter_dict)
                    return outfilter


class RolesByPrivileges(RsusrCheck):
    def execute(self, session):
        try:
            if not hasattr(self, "rsusr070_filter"):
                msg = "Required parameter 'rsusr070_filter' not set in configuration file."
                raise ValueError(msg)

            report_rsusr070 = Rsusr070(self.config_file)
            if hasattr(self, "save_to_file") and self.save_to_file:
                report_rsusr070.need_to_save(self.folder_to_save)
            rsusr070_filter = self.get_table_filter(self.rsusr070_filter)
            value = report_rsusr070.get_row_number_by_filter(session, rsusr070_filter)

        except (AttributeError, ValueError, TypeError, PermissionError) as error:
            self.problem = type(error)
            self.problem_text = str(error)
            if self.do_log:
                self.logger.error("Bad configuration for check '{0}'".format(self.title.forma(**self.__dict__)))
                self.logger.error("{0} - {1}".format(self.problem, self.problem_text))
            self.set_problem_status()
        else:
            if self.do_log:
                self.logger.info("Found {0} roles with the privileges".format(value))
            self.set_status(value)


class UsersByPrivileges(RsusrCheck):
    def execute(self, session):
        try:
            if not hasattr(self, "rsusr002_filter"):
                msg = "Required parameter 'rsusr002_filter' not set in configuration file."
                raise ValueError(msg)

            report_rsusr002 = Rsusr002(self.config_file)
            if hasattr(self, "save_to_file") and self.save_to_file:
                report_rsusr002.need_to_save(self.folder_to_save)
            rsusr002_filter = self.get_table_filter(self.rsusr002_filter)
            value = report_rsusr002.get_row_number_by_filter(session, rsusr002_filter)

        except (AttributeError, ValueError, TypeError, PermissionError) as error:
            self.problem = type(error)
            self.problem_text = str(error)
            self.set_problem_status()
            if self.do_log:
                self.logger.error("Bad configuration for check '{0}'".format(self.title.forma(**self.__dict__)))
                self.logger.error("{0} - {1}".format(self.problem, self.problem_text))
            self.set_problem_status()
        else:
            if self.do_log:
                self.logger.info("Found {0} users with the privileges".format(value))
            self.set_status(value)
