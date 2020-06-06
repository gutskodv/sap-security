import yaml
import os
from sapsec.checks.table_check import TableCheck
from sapsec.sapgui.se16 import TCodeSE16, FieldFilters
from sapsec.settings import CONFIG_FILE


class CheckTableEntries(TableCheck):
    def __init__(self, title, descr=None, do_log=False):
        super().__init__(title, descr,  do_log)

    def get_table_filter(self):
        if not self.config_file or not os.path.exists(self.config_file):
            return

        with open(self.config_file) as file:
            yaml_dict = yaml.full_load(file)

            if "table_filters" not in yaml_dict:
                if self.do_log:
                    print("Table filters not found in config file")

            if self.table_filter in yaml_dict["table_filters"]:
                filters = FieldFilters()
                filters.init_filter_by_dict(yaml_dict["table_filters"][self.table_filter])
                return filters

    def execute(self, session):
        try:
            if not hasattr(self, "table_name"):
                msg = "Required parameter 'table_name' not set in configuration file"
                raise ValueError(msg)
            se16 = TCodeSE16(self.table_name, do_log=self.do_log)
            table_filter = self.get_table_filter() if hasattr(self, "table_filter") else None
            result = se16.get_row_number_by_filter(session, table_filter)

        except (AttributeError, ValueError, TypeError, PermissionError) as error:
            self.problem = type(error)
            self.problem_text = str(error)
            if self.do_log:
                self.logger.error("Bad configuration for check '{0}'".format(self.title.forma(**self.__dict__)))
                self.logger.error("{0} - {1}".format(self.problem, self.problem_text))
            self.set_problem_status()
        else:
            if self.do_log:
                self.logger.info("Found {1} entries in table {0}".format(self.table_name, result))
            self.set_status(result)
