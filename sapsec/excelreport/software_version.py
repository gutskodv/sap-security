from .xlsxreport import XlsxReport
import os


class SoftwareVersionReport:
    def __init__(self, data, folder_report):
        self.data = data
        self.folder_report = folder_report

    def generate_report(self):
        filename = "soft_versions.xlsx"
        soft_report = XlsxReport(os.path.join(self.folder_report, filename), "Results")

        column_list = list()
        column_list.append(("Component", 20))
        for sid in self.data.sids:
            column_list.append((sid, 20))
        column_list.append(("Status", 20))
        status_column = len(column_list)
        column_list.append(("Comment", 20))
        soft_report.inc_current_row()
        soft_report.insert_software_columns(column_list)
        start_filter_pos = soft_report.current_row

        for item in self.data.components:
            soft_report.insert_software_data(item, self.data.sids)

        soft_report.add_soft_ver_filters(start_filter_pos, status_column)
        return filename

