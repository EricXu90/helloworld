# -*- coding: utf-8 -*-
# @Date    : 2015-03-30 13:08:08
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

""" This class defines keywords related to main page. """

from web.pageobjects.mainpage import Main


class MainPageKeywords(object):

    """This class encapsulates possible operations on main page after login.

    Then exports the following keywords to RF:
    Navigate To Detections
    Navigate To Mail Settings
    Navigate To System Settings
    Navigate To Scan And Analysis
    """

    def __init__(self):
        """ Initialize main page. """
        super(MainPageKeywords, self).__init__()
        self.main_page = Main()

    def navigate_to_detections(self):
        """ Navigate to detections page.

        @Param:
            None
        @Return:
            None
        Example:
        | Navigate To Detections |
        """
        # MAIN_PAGE.navigate_to_detections()
        self.main_page.navigate_to_detections_page()

    def navigate_to_mail_settings(self):
        """ Navigate to mail setting page.

        @Param:
            None
        @Return:
            None
        Example:
        | Navigate To Mail Settings |
        """
        # MAIN_PAGE.navigate_to_mail_settings()
        self.main_page.navigate_to_mail_settings_page()

    def navigate_to_system_settings(self):
        """ Navigate to system setting page.

        @Param:
            None
        @Return:
            None
        Example:
        | Navigate To System Settings |
        """
        # MAIN_PAGE.navigate_to_system_settings()
        self.main_page.navigate_to_system_settings_page()

    def navigate_to_scan_and_analysis(self):
        """ Navigate to system setting page.

        @Param:
            None
        @Return:
            None
        Example:
        | Navigate To Scan And Analysis |
        """
        # MAIN_PAGE.navigate_to_system_settings()
        self.main_page.navigate_to_va_settings_page()
