

class SAPGuiNotRunning(Exception):
    def __init__(self, data):
        self.data = data


class SAPGuiNotFoundActiveConnections(Exception):
    def __init__(self, data):
        self.data = data


class SAPGuiScriptingDisabled(Exception):
    def __init__(self, data):
        self.data = data

class TcodeNotFound(Exception):
    pass

class ReportNotFound(Exception):
    pass

class SAPGuiElementNotFound(Exception):
    def __init__(self, element_id, session_id, purpose):
        self.element_id = element_id
        self.session_id = session_id
        self.purpose = purpose

    def __str__(self):
        return "Element '{0}' not found in session '{1}' while {2}".format(self.element_id,
                                                                          self.session_id,
                                                                          self.purpose)

class SAPGuiNullSession(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "while %s" % (self.data,)


class SAPGuiWrongElementType(Exception):
    def __init__(self, element_type, session_id, element_id, text, msg_template):
        self.element_type = element_type
        self.sesion_id = session_id
        self.element_id = element_id
        self.text = text
        self.msg_template = msg_template

    def __str__(self):
        return self.msg_template(**self.__dict__)

