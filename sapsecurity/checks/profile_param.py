from sapsecurity.checks.elementary_check import ElementaryCheck
from sapsecurity.sapgui.rpsfpar import Rspfpar


class CheckProfileParameter(ElementaryCheck):
    def __init__(self, title, descr="", do_log=False):
        super().__init__(title, descr, do_log)
        self.comment_text = "Parameter is set to {result} (but required {req_text})"

    def __compare_result(self, result):
        try:
            if hasattr(self, "param_type") and self.param_type == 'int':
                result = int(result)
            else:
                result = str(result)

            if hasattr(self, "param_complied_values"):
                return self.__compare_with_param_complied_values(result)

            elif hasattr(self, "param_complied_value"):
                return self.__compare_with_param_complied_value(result)

            elif hasattr(self, "more_or_equal_to"):
                return self.__compare_with_more_or_equal_to(result)

            elif hasattr(self, "less_or_equal_to"):
                return self.__compare_with_less_or_equal_to(result)

            else:
                self.problem = ElementaryCheck.BAD_CONFIG_PARAMS
                self.problem_text = "Bad configuration"

        except Exception as ex:
            if self.do_log:
                print(str(ex))
            self.problem = ElementaryCheck.BAD_CONFIG_PARAMS
            self.problem_text = "Bad 'param_type'"

    def __compare_with_param_complied_values(self, result):
        self.req_text = " or ".join([str(item) for item in self.param_complied_values])

        if hasattr(self, "param_type") and self.param_type == 'int':
            compare_with = [int(item) for item in self.param_complied_values]
        else:
            compare_with = [str(item) for item in self.param_complied_values]

        if result in compare_with:
            return True
        return False

    def __compare_with_param_complied_value(self, result):
        self.req_text = str(self.param_complied_value)
        if hasattr(self, "param_type") and self.param_type == 'int':
            compare_with = int(self.param_complied_value)
        else:
            compare_with = str(self.param_complied_value)

        if result == compare_with:
            return True
        return False

    def __compare_with_more_or_equal_to(self, result):
        self.req_text = "more or equal to " + str(self.more_or_equal_to)
        if hasattr(self, "param_type") and self.param_type == 'int':
            compare_with = int(self.more_or_equal_to)
            if result >= compare_with:
                return True
            return False

    def __compare_with_less_or_equal_to(self, result):
        self.req_text = "less or equal to " + str(self.less_or_equal_to)
        if hasattr(self, "param_type") and self.param_type == 'int':
            compare_with = int(self.less_or_equal_to)
            if result <= compare_with:
                return True
            return False

    def execute(self, sap_session):
        try:
            if not hasattr(self, "param_name"):
                msg = "An error occurred while executing the script. Details:\n"
                msg += "Required parameter 'param_name' not set in configuration file."
                raise ValueError(msg)

            report_rspfpar = Rspfpar(self.param_name, sap_session, do_log=self.do_log)
            value = report_rspfpar.get_param_value()
        except (AttributeError, ValueError, TypeError, PermissionError) as error:
            self.problem = type(error)
            self.problem_text = str(error)
            self.set_problem_status()
        else:
            self.set_status(value)
