import yaml
from sapsecurity.checks.table_check import TableCheck
from sapsecurity.settings import CONFIG_FILE
from sapsecurity.sapgui.rsusr002 import Rsusr002Filter, Rsusr002
from sapsecurity.sapgui.rsusr070 import Rsusr070


class RsusrCheck(TableCheck):
    @staticmethod
    def get_table_filter(filter_name):
        with open(CONFIG_FILE) as file:
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
                msg = "An error occurred while executing the script. Details:\n"
                msg += "Required parameter 'rsusr070_filter' not set in configuration file."
                raise ValueError(msg)

            report_rsusr070 = Rsusr070()
            if hasattr(self, "save_to_file") and self.save_to_file:
                report_rsusr070.need_to_save(self.folder_to_save)
            rsusr070_filter = self.get_table_filter(self.rsusr070_filter)
            value = report_rsusr070.get_row_number_by_filter(session, rsusr070_filter)

        except (AttributeError, ValueError, TypeError, PermissionError) as error:
            self.problem = type(error)
            self.problem_text = str(error)
            self.set_problem_status()
            if self.do_log:
                print(self.problem_text)
        else:
            self.set_status(value)


class UsersByPrivileges(RsusrCheck):
    def execute(self, session):
        try:
            if not hasattr(self, "rsusr002_filter"):
                msg = "An error occurred while executing the script. Details:\n"
                msg += "Required parameter 'rsusr002_filter' not set in configuration file."
                raise ValueError(msg)

            report_rsusr002 = Rsusr002()
            if hasattr(self, "save_to_file") and self.save_to_file:
                report_rsusr002.need_to_save(self.folder_to_save)
            rsusr002_filter = self.get_table_filter(self.rsusr002_filter)
            value = report_rsusr002.get_row_number_by_filter(session, rsusr002_filter)

        except (AttributeError, ValueError, TypeError, PermissionError) as error:
            self.problem = type(error)
            self.problem_text = str(error)
            self.set_problem_status()
            if self.do_log or True:
                print(self.problem_text)
        else:
            self.set_status(value)
