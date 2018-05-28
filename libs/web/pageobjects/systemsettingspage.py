# -*- coding: utf-8 -*-
# @Date    : 2015-03-27 09:42:19
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from web.constants.elemlocators import *
from web.constants.constants import *
import common as cm

class SystemSettings(object):
    """Encapsulates operations which may be done in System Settings page.
    """
    def __init__(self):
        super(SystemSettings, self).__init__()
        self._current_tab = ""
        self.common_operation = cm.Common()

    #====================================
    # Network tab
    #====================================
    def switch_to_network(self):
        """Click the "Network" tab in System Settings page
            @Param:
                None
            @Return:
                None
        """
        self.common_operation.switch_to_middle_frame()
        cm.FIREFOX_DRIVER.find_element(By.ID, TAB_NETWORK).click()
        self._current_tab = "network"

    def select_operation_mode(self, mode):
        """ Select the specific operation mode
            @Params:
                mode: operation mode (MTA, BCC, SPAN/TAP)
            @Return:
                None
        """
        # lower case the string
        mode = mode.lower()

        # find the corresponding element
        if mode == "mta":
            radio_element = cm.FIREFOX_DRIVER.find_element(By.ID, RADIO_MTA_MODE)
        elif mode == "bcc":
            radio_element = cm.FIREFOX_DRIVER.find_element(By.ID, RADIO_BCC_MODE)
        else:
            radio_element = cm.FIREFOX_DRIVER.find_element(By.ID, RADIO_TAP_MODE)

        # Click the element
        radio_element.click()

    #====================================
    # Notification SMTP tab
    #====================================
    def switch_to_smtp(self):
        """Click the "Notification SMTP" tab in System Settings page
            @Param:
                None
            @Return:
                None
        """
        self.common_operation.switch_to_middle_frame()
        cm.FIREFOX_DRIVER.find_element(By.ID, TAB_NOTIFICATION_SMTP).click()
        self._current_tab = "smtp"

    def enable_internal_postfix(self):
        """ Click "Internal postfix server" to enable internal SMTP
            @Params:
                None
            @Return:
                None
        """
        cm.FIREFOX_DRIVER.find_element(By.ID, RADIO_BTN_INTERNAL).click()

    def enable_external_smtp(self):
        """ Click "External SMTP server" to enable external SMTP 
            @Params:
                None
            @Return:
                None
        """
        cm.FIREFOX_DRIVER.find_element(By.ID, RADIO_BTN_EXTERNAL).click()

    def input_smtp_server_name(self, server_name):
        """ Input SMTP server name
            @Params:
                server_name: Hostname/port of SMTP server
            @Return:
                None
        """
        input_element = cm.FIREFOX_DRIVER.find_element(By.ID, INPUT_SERVER_NAME)
        input_element.clear()
        input_element.send_keys(server_name)

    def input_smtp_server_port(self, server_port):
        """ Input SMTP server port
            @Params:
                server_port: Port on which SMTP server licent
            @Return:
                None
        """
        input_element = cm.FIREFOX_DRIVER.find_element(By.ID, INPUT_SERVER_PORT)
        input_element.clear()
        input_element.send_keys(server_port)

    #=============================================
    # Common operation
    #=============================================
    def click_save(self):
        """ Click save button to save configuration
            @Params:
                None
            @Return:
                None
            @Exception:
                Exception
        """
        try:
            # Save button in SMTP tab page
            if self._current_tab == "smtp":
                save_btn = cm.FIREFOX_DRIVER.find_element(By.CSS_SELECTOR, BTN_SMTP_SAVE)
                save_btn.click()
                WebDriverWait(cm.FIREFOX_DRIVER, 30).until(
                    ec.text_to_be_present_in_element((By.ID, SPAN_SMTP_INLINE_MESSAGE), SAVE_SUCCESS))
                return
            # Save button in network tab page
            elif self._current_tab == "network":
                cm.FIREFOX_DRIVER.find_element(By.CSS_SELECTOR, BTN_NETWORK_SAVE).click()
                while True:
                    save_ret = cm.FIREFOX_DRIVER.find_element(By.ID, SPAN_NETWORK_INLINE_MESSAGE).text
                    if save_ret == SAVE_SUCCESS:
                        return
                    time.sleep(2)
                raise Exception("Save network settings fail!")
        except Exception as err:
            raise

    def click_cancel(self):
        """ Click "Cancel" button to cancel configuration
            @Params:
                None
            @Return:
                None
        """
        try:
            # Current tab is "Notification SMTP"
            if self._current_tab == "smtp":
                cancel_btn = cm.FIREFOX_DRIVER.find_element(By.CSS_SELECTOR, BTN_SMTP_CANCEL)
                cancel_btn.click()
                return
            # Current tab is "Network"
            elif self._current_tab == "network":
                cancel_btn = cm.FIREFOX_DRIVER.find_element(By.CSS_SELECTOR, BTN_NETWORK_CANCEL)
                cancel_btn.click()
                return
        except Exception as err:
            raise