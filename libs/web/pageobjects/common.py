# -*- coding: utf-8 -*-
# @Date    : 2015-04-15 09:31:31
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

import os

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert

from web.constants.elemlocators import *
from web.constants.constants import *

# webdriver -- Global variable
FIREFOX_DRIVER = None
ERROR_MESSAGE = ""

class Common(object):
    """ Common class define the page operations which may be widely used by different pages"""
    def __init__(self):
        super(Common, self).__init__()
        self._firefox_profile = webdriver.FirefoxProfile()

    def set_firefox_profile(self):
        """ Set the preference of firefox before initializing firefox webdriver
            Preferences which will be set:
            1. Auto download file while click <a href="..." /> link without confirmation window
            @Params:
                None
            @Return:
                None
        """
        # Set firefox profile to enable auto download
        self._firefox_profile.set_preference("browser.download.folderList", 2)
        self._firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
        self._firefox_profile.set_preference("browser.download.dir", DOWNLOAD_DIR)
        self._firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/xml,text/plain,text/xml,image/jpeg,text/csv")

    def switch_to_left_frame(self):
        """ Switch to the left menu frame if have
            @Params:
                None
            @Return:
                None
        """
        global FIREFOX_DRIVER

        # 1. Switch to top document
        FIREFOX_DRIVER.switch_to_default_content()
        # 2. Enter left frame
        left_frame = WebDriverWait(FIREFOX_DRIVER, EXPLICIT_WAIT_TIME).until(
            ec.presence_of_element_located((By.ID, IFRAME_LEFT_PAGE))
        )
        FIREFOX_DRIVER.switch_to_frame(left_frame)

    def switch_to_middle_frame(self):
        """ Switch to the middle frame (always exist)
            @Params:
                None
            @Return:
                None
        """
        global FIREFOX_DRIVER

        # 1. Switch to top document
        FIREFOX_DRIVER.switch_to_default_content()
        # 2. Enter middle frame
        middle_frame = WebDriverWait(FIREFOX_DRIVER, EXPLICIT_WAIT_TIME).until(
            ec.presence_of_element_located((By.ID, IFRAME_MIDDLE_PAGE))
        )
        FIREFOX_DRIVER.switch_to_frame(middle_frame)


    def launch_browser(self):
        """ Initialize WebDriver to open the specific browser
            @Params:
                None
            @Return:
                None
        """
        global FIREFOX_DRIVER

        # Set firefox profile
        self.set_firefox_profile()

        # Initilize firefox driver
        FIREFOX_DRIVER = webdriver.Firefox(firefox_profile = self._firefox_profile)
        		
        # Maximuze browser window
        FIREFOX_DRIVER.maximize_window()
        # Set implicit wait time in which driver wait for the element load.
        # and it is set for the life of the WebDriver object instance
        #FIREFOX_DRIVER.implicitly_wait(IMPLICIT_WAIT_TIME)

    def close_browser(self):
        """ Close the browser if it has been opened
            @Params:
                None
            @Return:
                None
        """
        global FIREFOX_DRIVER

        if FIREFOX_DRIVER:
            FIREFOX_DRIVER.close()
            FIREFOX_DRIVER = None

    def confirm(self):
        """ Do confirm while an alert window popup and return the alert message
            @Params:
                None
            @Return:
                msg: alert message
        """
        global FIREFOX_DRIVER
        alert = Alert(FIREFOX_DRIVER)

        # Get the alert message
        msg = alert.text

        # Confirm the alert
        alert.accept()

        return msg

    def not_confirm(self):
        """ Do not confirm (usually cancel) while an alert window popup
            @Params:
                None
            @Return:
                None
        """
        global FIREFOX_DRIVER
        Alert(FIREFOX_DRIVER).dismiss()

    def get_err_msg(self):
        """ Get the page error message whenever do FE operations
            @Params:
                None
            @Return:
                ERROR_MESSAGE: error message (value of global variable)
        """
        global ERROR_MESSAGE

        # Return the error message if it was updated
        return ERROR_MESSAGE
