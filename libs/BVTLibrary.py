__author__ = 'jone_zhang'

from _alert import AlertKeywords
from _scanner import ScannerKeywords
from _db import DatabaseKeywords
from _usandbox import SandboxKeywords
from _update import UpdateKeywords
from _license import LicenseKeyword
from _report import ReportKeyword
from _msgtrace import MsgTraceKeyword
from _mta import MTAKeyword
from _feedback import FeedbackKeyWords
from _usbx_sync import SyncUSBXdataKeywords
from RF_int import RF_Int_Keywords
from _PasswordAnalyzer import PA_Keywords
from _syslog import SyslogKeywords
from _keyword import search_Keywords
from _dps import DPSKeyword
from _snmp import SnmpKeywords
from _tmsps import SpsKeywords
from _http import HTTTPKeywords
from _yara import YaraKeywords
from _webservice import WebServiceKeywords
from _msgQ import MsgQKeywords
from _trendX import TrendXKeywords
from _upgrade import UpgradeKeywords

class BVTLibrary(
    AlertKeywords,
    ScannerKeywords,
    DatabaseKeywords,
    SandboxKeywords,
    UpdateKeywords,
    LicenseKeyword,
    ReportKeyword,
    MsgTraceKeyword,
    MTAKeyword,
    FeedbackKeyWords,
    SyncUSBXdataKeywords,
    RF_Int_Keywords,
    PA_Keywords,
    SyslogKeywords,
    search_Keywords,
    DPSKeyword,
    SnmpKeywords,
    SpsKeywords,
    HTTTPKeywords,
    YaraKeywords,
    WebServiceKeywords,
    MsgQKeywords,
    TrendXKeywords,
    UpgradeKeywords
):

    """
        The entry of BVT keywords
    """
    def _show_usage(self):
        print """
            This BVT Library contains all the BVT keywords used by tess cases, when you want to extend new words, please follow
        below steps:

        1. Add you new words in related module file; maybe need to create new module file
            a. If you need to create new keyword class, you should import the module file '_baselib.py'
            b. Then the new keyword class should inherit the class 'KeywordBase'

        2. Import new keyword class in this file ( BVTLibrary.py )

        3. Add new base class for class "BVTLibrary"

        When the steps complete, you can use the new added keywords in test case.

        """
