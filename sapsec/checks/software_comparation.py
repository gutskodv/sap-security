from pysapgui.software_components import SAPSoftwareComponents
from sapsec.checks.elementary_check import ElementaryCheck
from sapsec.excelreport.software_version import SoftwareVersionReport


class SoftwareComponent:
    def __init__(self, component, descr):
        self.component = component
        self.comp_ver = dict()
        self.sp_ver = dict()
        self.max_sp = dict()
        self.descr = descr
        self.same_version = None

    def check_same_version(self, system_count):
        self.same_version = True

        if (len(self.comp_ver) != system_count) or (len(self.sp_ver) != system_count):
            self.same_version = False
            return
        if len(self.comp_ver) == 1 and len(self.sp_ver) == 1:
            return

        comp_ver = None
        for dict_key in self.comp_ver.keys():
            if comp_ver is None:
                comp_ver = self.comp_ver[dict_key]
            elif comp_ver != self.comp_ver[dict_key]:
                self.same_version = False
                return

        sp_ver = None
        for dict_key in self.sp_ver.keys():
            if sp_ver is None:
                sp_ver = self.sp_ver[dict_key]
            elif sp_ver != self.sp_ver[dict_key]:
                self.same_version = False
                return

    def add_ver(self, sid, comp_ver, sp_ver, max_sp):
        self.comp_ver[sid] = comp_ver
        self.sp_ver[sid] = sp_ver
        self.max_sp[sid] = max_sp

    def __str__(self):
        out_text = list()
        out_text.append("Component: %s" % (self.component, ))
        out_text.append("Description: %s" % (self.descr, ))
        out_text.append("Component versions: %s" % (", ".join(list(self.comp_ver.values()), )))
        out_text.append("Support package levels: %s" % (", ".join(list(self.sp_ver.values()), )))
        return "\n".join(out_text)


class SoftwareComparation:
    def __init__(self):
        self.components = list()
        self.sids = list()

    def __add_components_from_sap(self, sid, data_list):
        if len(data_list):
            for item in data_list:
                self.__add_component(sid, item)

    def __add_component(self, sid, row):
        if len(row) != 5:
            return

        component = row[0]
        component_in_list = self.__get_component_by_name(component)
        if component_in_list is None:
            descr = row[4]
            component_in_list = SoftwareComponent(component, descr)
            self.components.append(component_in_list)
        comp_ver = row[1]
        sp_ver = row[2]
        max_sp = row[3]
        component_in_list.add_ver(sid, comp_ver, sp_ver, max_sp)

    def __add_sid(self, sid):
        self.sids.append(sid)

    def __get_component_by_name(self, comp_name):
        for item in self.components:
            if item.component == comp_name:
                return item

    def sort_components(self):
        self.components = sorted(self.components, key=lambda comp: comp.component)

    def print_all(self):
        for item in self.components:
            if item.same_version:
                print(item)

    def calc_same_version(self):
        for item in self.components:
            item.check_same_version(len(self.sids))

    def load_components(self, sap_session, sap_info):
        data = SAPSoftwareComponents.load_software_components(sap_session)
        self.__add_components_from_sap(sap_info["sid"], data)
        self.__add_sid(sap_info["sid"])


class CheckSameSoftwareVersion(ElementaryCheck):
    def __init__(self, title, descr=None, do_log=False):
        super().__init__(title, descr, do_log)

    def compare_result(self, compare):
        for item in compare.components:
            if not item.same_version:
                return False

        return True

    def create_excel_report(self, compare):
        report = SoftwareVersionReport(compare, self.folder_to_save)
        return report.generate_report()

    def execute(self, sap_sessions):
        sap_sessions = sap_sessions
        compare = SoftwareComparation()

        try:
            for sap_session, sap_info in sap_sessions:
                compare.load_components(sap_session, sap_info)

        except (AttributeError, ValueError, TypeError, PermissionError) as error:
            self.process_error(error)
        else:
            compare.calc_same_version()
            compare.sort_components()
            self.set_status(compare)
            self.comment = '=HYPERLINK("{0}", "more details")'.format(self.create_excel_report(compare))
