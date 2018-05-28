# -*- coding: utf-8 -*-
# @Date    : 2015-03-30 13:08:08
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

from web.keywords._login import LoginPageKeywords
from web.keywords._main import MainPageKeywords
from web.keywords._detections import DetectionsKeywords
from web.keywords._systemsettings import SystemSettingsKeywords
from web.keywords._mailsettings import MailSettingsKeywords
from web.keywords._scanandanalysis import AnalysisKeywords
from web.keywords._common import CommonKeywords

class WebLibrary(
    CommonKeywords,
    LoginPageKeywords,
    MainPageKeywords,
    DetectionsKeywords,
    SystemSettingsKeywords,
    MailSettingsKeywords,
    AnalysisKeywords
):

    """
        The entry of all of web console keywords
        TBD
        <This BVT Library contains all the BVT keywords used by tess cases, when you want to extend new words, please follow
        below steps:

        1. Add you new words in related module file; maybe need to create new module file
            a. If you need to create new keyword class, you should import the module file '_baselib.py'
            b. Then the new keyword class should inherit the class 'KeywordBase'

        2. Import new keyword class in this file ( BVTLibrary.py )

        3. Add new base class for class "BVTLibrary"

        When the steps complete, you can use the new added keywords in test case.
        >
    """
