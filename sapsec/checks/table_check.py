from sapsec.checks.elementary_check import ElementaryCheck


class TableCheck(ElementaryCheck):
    def __init__(self, title, descr=None, do_log=False):
        super().__init__(title, descr, do_log)
        self.comment_template = "Found {result} entries (but required {req})"

    def compare_result(self, result):
        try:
            result = int(result)
            if hasattr(self, "entries_complied_limit"):
                return self.compare_with_entries_complied_limit(result)

            elif hasattr(self, "entries_not_empty"):
                return self.compare_with_entries_not_empty(result)

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

    def compare_with_entries_complied_limit(self, result):
        self.req_text = "less or equal to {0}". format(self.entries_complied_limit)
        compare_with = int(self.entries_complied_limit)
        if result <= compare_with:
            return True
        return False

    def compare_with_entries_not_empty(self, result):
        self.req_text = "more than 0 entries"
        if result > 0:
            return True
        return False
