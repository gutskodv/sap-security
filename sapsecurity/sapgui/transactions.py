from .saplogon import SAPLogon


class TCode:
    def __init__(self, tcode, sap_session=None, do_log=False):
        self.tcode = tcode
        self.do_log = do_log
        self.sap_session = sap_session

    def call_transaction(self, sap_session=None):
        if not sap_session:
            sap_session = self.sap_session

        SAPLogon.call_transaction(sap_session, self.tcode)
        gui_msg = SAPLogon.get_status_message(sap_session)

        if gui_msg:
            if gui_msg[1] == "343":
                msg = "An error occurred while executing the script. Details:\n"
                msg += "Wrong transaction name '{0}'. GUI Message: {1}".format(self.tcode, gui_msg)
                raise ValueError(msg)

            elif gui_msg[1] == "077":
                msg = "An error occurred while executing the script. Details:\n"
                msg += "Not authorized to execute '{0}' transaction. GUI Message: {1}".format(self.tcode, gui_msg)
                raise PermissionError(msg)

    def exit_transaction(self, sap_session=None):
        if not sap_session:
            sap_session = self.sap_sesion
        SAPLogon.call_transaction(sap_session, "")
