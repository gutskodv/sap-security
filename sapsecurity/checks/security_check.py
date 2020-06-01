

class SecurityCheckStatus:
    COMPLIED = 'COMPLIED'
    NOT_COMPLIED = 'NOT_COMPLIED'
    ERROR_WITH_INFLUENCE_TO_STATUS = 'ERROR_WITH_INFLUENCE_TO_STATUS'
    ERROR_WITHOUT_INFLUENCE_TO_STATUS = 'ERROR_WITHOUT_INFLUENCE_TO_STATUS'
    AVAILABLE_STATUS = [COMPLIED, NOT_COMPLIED,
                        ERROR_WITH_INFLUENCE_TO_STATUS,
                        ERROR_WITHOUT_INFLUENCE_TO_STATUS]


class SecurityCheck:
    def __init__(self, title, descr, do_log=False):
        self.title = title
        self.descr = descr
        self.do_log = do_log

        self.status = SecurityCheckStatus.ERROR_WITHOUT_INFLUENCE_TO_STATUS
        self.comment = ""
        self.comment_template = ""
        self.problem = None
