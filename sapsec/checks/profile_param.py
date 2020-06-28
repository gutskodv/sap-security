from sapsec.checks.elementary_check import ElementaryCheck
from sapsec.sapgui.rpsfpar import Rspfpar


class CheckProfileParameter(ElementaryCheck):
    def __init__(self, title, descr="", do_log=False):
        super().__init__(title, descr, do_log)
        self.comment_text = "Parameter is set to {result} (but required {req_text})"

    def compare_result(self, result):
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
                msg = "Bad configuration for check '{0}'".format(self.title.forma(**self.__dict__))
                raise AttributeError(msg)

        except AttributeError as error:
            self.problem = type(error)
            self.problem_text = str(error)
            if self.do_log:
                self.logger.error("Bad configuration for check '{0}'".format(self.title.forma(**self.__dict__)))
                self.logger.error("{0} - {1}".format(self.problem, self.problem_text))
            self.set_problem_status()

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

    def execute(self, sap_sessions, session_num=0):
        sap_session, sap_info = sap_sessions[session_num]
        try:
            if not hasattr(self, "param_name"):
                msg = "Required parameter 'param_name' not set in configuration file."
                raise ValueError(msg)

            report_rspfpar = Rspfpar(self.param_name, self.config_file, sap_session=sap_session, do_log=self.do_log)
            value = report_rspfpar.get_param_value()
        except (AttributeError, ValueError, TypeError, PermissionError) as error:
            self.problem = type(error)
            self.problem_text = str(error)
            if self.do_log:
                if type(error) is not PermissionError:
                    self.logger.error("Bad configuration for check '{0}'".format(self.title.format(**self.__dict__)))
                else:
                    self.logger.error("No authority")
                self.logger.error("{0} - {1}".format(self.problem, self.problem_text))
            self.set_problem_status()
        else:
            if self.do_log:
                self.logger.info("Parameter {0} is set to {1}".format(self.param_name, value))
            self.set_status(value)
