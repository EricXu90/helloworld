__author__ = 'jone_zhang'

from _baselib import KeywordBase
from _pdf_parser import get_pages, get_toc
import os

class ReportKeyword(KeywordBase):
    """
    This library contain all related keywords about report function: Reports
    """

    def generate_report(self, type):
        """ Generate Report File

        @Param:

            type:    the ondemmand report type ( 1-daily, 2-weekly, 3-monthly )

        Return:

            None

        Example:

        | Generate Report | ${DailyReport} |

        """
        php_bin = "/opt/trend/ddei/UI/php/bin/php"
        php_script = "/opt/trend/ddei/UI/adminUI/ROOT/report/report_generation/common/generateReport.php"
        sql_delete_old_reports = "delete from tb_report_results"

        ddei_system_date = self.exec_command_on_DDEI("date +'%Y-%m-%d'")
        cmd_generate = "%s %s %s %s" % (php_bin, php_script, int(type), ddei_system_date)

        self.exec_sql_command_on_DDEI(sql_delete_old_reports)
        self.exec_command_on_DDEI(cmd_generate)


    def report_should_be_generated(self, type):
        """ Check the report file on disk existing

        @Param:

            type:    the ondemmand report type ( 1-daily, 2-weekly, 3-monthly )

        Return:

            None

        Example:

        | Report Should Be Generated | ${DailyReport} |

        """
        type_name_map = {
            "1": "DailyReport",
            "2": "WeeklyReport",
            "3": "MonthlyReport"
        }

        sql_query_path = "select report_pdfpath from tb_report_results"
        report_path  = self.exec_sql_command_on_DDEI(sql_query_path)

        report_exist_cmd = "ls %s" % report_path
        result = self.exec_command_on_DDEI(report_exist_cmd)

        if report_path.find(type_name_map[type]) == -1 or result.find("No such file") != -1:
            raise AssertionError("The report file is not generated.")

    def get_generated_report_path(self):
        """ Return the generated report file path on DDEI

        @Param:

            None

        Return:

            None

        Example:

        | ${report_path}= | Get Generated Report Path |

        """
        sql_query_path = "select report_pdfpath from tb_report_results"
        report_path  = self.exec_sql_command_on_DDEI(sql_query_path)

        if report_path.strip() == "":
            raise AssertionError("The report file path is empty. Need to check whether it is generated.")

        return report_path


    def get_report_table_list(self, pdf_report=""):
        """ Return the report table list item title

        @Param:

            pdf_report:    the report path name on local machine

        Return:

            None

        Example:

        | ${report_table}= | Get Report Table List | c:\\123.pdf |

        """
        if not os.path.exists(pdf_report):
            raise AssertionError("The following report file does not exist: %s" % pdf_report)

        table = get_toc(pdf_report)

        return ''.join(str(i) for i in table)

    def get_report_content(self, pdf_report=""):
        """ Return the report content

        @Param:

            pdf_report:    the report path name on local machine

        Return:

            None

        Example:

        | ${report_content}= | Get Report Content | c:\\123.pdf |

        """
        if not os.path.exists(pdf_report):
            raise AssertionError("The following report file does not exist: %s" % pdf_report)

        content = get_pages(pdf_report)

        return str(content)