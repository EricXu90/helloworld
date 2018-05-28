# -*- coding: utf-8 -*-
# @Date    : 2015-04-02 15:40:29
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : www.trendmicro.com
# @Version : 0.1

import os
#from web.constants.pageinstantiation import SYSTEM_SETTINGS_PAGE
from web.pageobjects.systemsettingspage import SystemSettings

class SystemSettingsKeywords(object):
    """This class encapsulates possible operations on System Settings page
       and explore the keywords to RF.
    """
    def __init__(self):
        super(SystemSettingsKeywords, self).__init__()
        self.system_settings_page = SystemSettings()

    #====================================
    # Network tab
    #====================================
    def switch_to_network_tab(self):
        """ Switch to "Network" tab whenever needed
        @Params:
            None
        @Return:
            None
        Example:
        | Switch To Network Tab |
        """
        self.system_settings_page.switch_to_network()

    def select_operation_mode(self, mode):
        """ Select operation mode on the network tab, operation mode would be
            1. MTA
            2. BCC
            3. SPAN/TAP
        @Params:
            mode: operation mode (can be uppercase, lowercase or mix)
        @Return:
            None
        Example:
        | Select Operation Mode | MTA |
        """
        self.system_settings_page.select_operation_mode(mode)

    def switch_to_proxy_tab(self):
        """ Switch to "Proxy" tab whenever needed
        @Params:
            None
        @Return:
            None
        Example:
        | Switch To Proxy Tab |
        """
        # TBD
        pass

    #====================================
    # Notification SMTP tab
    #====================================
    def switch_to_smtp_tab(self):
        """ Switch to "Notification SMTP" tab whenever needed
        @Params:
            None
        @Return:
            None
        Example:
        | Switch To SMTP Tab |
        """
        self.system_settings_page.switch_to_smtp()

    def select_external_smtp(self):
        """ Select to enable external SMTP server
        @Params:
            None
        @Return:
            None
        Example:
        | Select External SMTP |
        """
        self.system_settings_page.enable_external_smtp()

    def input_external_smtp_name(self, host):
        """ Input the hostname or IP address to external SMTP server
        @Params:
            host: external SMTP server hostname or IP address
        @Return:
            None
        Example:
        | Input External SMTP Name | 10.204.253.111 |
        """
        self.system_settings_page.input_smtp_server_name(host)

    def input_external_smtp_port(self, port):
        """ Input the port listened by external SMTP server
        @Params:
            port: external SMTP server port
        @Return:
            None
        Example:
        | Input External SMTP Port | 25 |
        """
        self.system_settings_page.input_smtp_server_port(port)

    def select_internal_smtp(self):
        """ Select to enable internal postfix server
        @Params:
            None
        @Return:
            None
        Example:
        | Select Internal SMTP |
        """
        self.system_settings_page.enable_internal_postfix()

    def save_system_settings(self):
        """ Click "Save" button to save system Settings
        @Params:
            None
        @Return:
            None
        Example:
        | Save System Settings |
        """
        self.system_settings_page.click_save()

    def cancel_system_settings(self):
        """ Click "Cancel" button to cancel system Settings
        @Params:
            None
        @Return:
            None
        Example:
        | Save System Settings |
        """
        self.system_settings_page.click_cancel()

