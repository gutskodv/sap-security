from sapsecurity.checks.security_check import SecurityCheckStatus, SecurityCheck


class ElementaryCheck(SecurityCheck):
    BAD_CONFIG_PARAMS = "BAD_CONFIG_PARAMS"

    def __init__(self, title, descr=None, do_log=False):
        super().__init__(title, descr, do_log=do_log)

        self.problem = None
        self.problem_text = ""
        self.req_text = "not loaded yet"

    def add_additional_parameters(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key) and key not in ["class"]:
                self.__setattr__(key, value)

    def set_problem_status(self):
        not_critical_errors = [ValueError, TypeError, AttributeError]

        if self.problem in not_critical_errors:
            self.status = SecurityCheckStatus.ERROR_WITHOUT_INFLUENCE_TO_STATUS
        else:
            self.status = SecurityCheckStatus.ERROR_WITH_INFLUENCE_TO_STATUS
        self.comment = self.problem_text

    def set_status(self, result):
        comp_result = self.compare_result(result)
        if self.problem:
            self.set_problem_status()
        elif comp_result:
            self.status = SecurityCheckStatus.COMPLIED
        else:
            self.status = SecurityCheckStatus.NOT_COMPLIED
            self.comment = self.comment_template.format(result=result, req=self.req_text)

    def compare_result(self, result):
        return True
