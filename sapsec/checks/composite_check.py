from sapsec.checks.security_check import SecurityCheck, SecurityCheckStatus


class CompositeCheck(SecurityCheck):
    def __init__(self, title, descr="", do_log=False):
        super().__init__(title, descr, do_log=do_log)
        self.checks = list()

    def add_check(self, new_check):
        self.checks.append(new_check)

    def calc_global_status(self):
        self.status = SecurityCheckStatus.COMPLIED

        for sec_check in self.checks:
            if sec_check.status not in [SecurityCheckStatus.COMPLIED,
                                        SecurityCheckStatus.ERROR_WITHOUT_INFLUENCE_TO_STATUS]:
                self.status = SecurityCheckStatus.NOT_COMPLIED

        if self.do_log:
            self.logger.info("GL_{1} (composite check) - '{0}')".format(self.title.format(**self.__dict__), self.status))

    def execute(self, session):
        for check in self.checks:
            if self.do_log:
                self.logger.info("Processing elementary check '{0}'".format(check.title.format(**check.__dict__)))
            check.execute(session)
            if self.do_log:
                self.logger.info("{1} - '{0}'".format(check.title.format(**check.__dict__), check.status))
        self.calc_global_status()
