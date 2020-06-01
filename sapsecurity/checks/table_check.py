from sapsecurity.checks.elementary_check import ElementaryCheck


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
                self.problem = ElementaryCheck.BAD_CONFIG_PARAMS
                self.problem_text = "Bad configuration"

        except Exception as ex:
            if self.do_log:
                print(str(ex))
            self.problem = ElementaryCheck.BAD_CONFIG_PARAMS
            self.problem_text = "Bad 'param_type'"

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
