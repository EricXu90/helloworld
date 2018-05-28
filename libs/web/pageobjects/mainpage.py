# -*- coding: utf-8 -*-
# @Date    : 2015-03-30 13:08:08
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from web.constants.constants import *
from web.constants.elemlocators import *
import common as cm

class Main(object):
    """Encapsulate operations which may be done in MainPage"""
    def __init__(self):
    	super(Main, self).__init__()

    def navigate_to_detections_page(self):
        """ Click "Detections" menu to navigate to detection query page
        """
        # Switch focus to the top document
        cm.FIREFOX_DRIVER.switch_to_default_content()
        # Click the "Detections" menu
        menu_detection = cm.FIREFOX_DRIVER.find_element(By.ID, MENU_DETECTIONS)
        menu_detection.click()
        # Wait for the sub menu to be available, then click
        #sub_menu_detected_msg = WebDriverWait(cm.FIREFOX_DRIVER, 10).until(
        #    ec.presence_of_element_located((By.ID, SUB_MENU_THREAT))
        #)
        sub_menu_detected_msg = cm.FIREFOX_DRIVER.find_element(By.ID, SUB_MENU_THREAT)
        sub_menu_detected_msg.click()

    def navigate_to_mail_settings_page(self):
        """ Click the "Administration" menu to  navigate to "Mail Settings" page
            @Params:
                None
            @Return:
                None
        """
        # Switch focus to the top document
        cm.FIREFOX_DRIVER.switch_to_default_content()
        # Click the "Administration" menu
        menu_admin = cm.FIREFOX_DRIVER.find_element(By.ID, MENU_ADMIN)
        menu_admin.click()
        # Wait for the sub menu to be available, then click
        #sub_menu_mail_settings = WebDriverWait(cm.FIREFOX_DRIVER, 10).until(
        #    ec.presence_of_element_located((By.ID, SUB_MENU_MAIL_SETTINGS))
        #)
        sub_menu_mail_settings = cm.FIREFOX_DRIVER.find_element(By.ID, SUB_MENU_MAIL_SETTINGS)
        sub_menu_mail_settings.click()

    def navigate_to_system_settings_page(self):
        """ Click the "Administration" menu to  navigate to "System Settings" page
            @Params:
                None
            @Return:
                None
        """
        # Switch focus to the top document 
        cm.FIREFOX_DRIVER.switch_to_default_content()
		
        # Click the "Administration" menu
        menu_admin = cm.FIREFOX_DRIVER.find_element(By.ID, MENU_ADMIN)
        ac = ActionChains(cm.FIREFOX_DRIVER)
        ac.move_to_element(menu_admin)
        ac.perform()
        #menu_admin.click()
        
        #time.sleep(10)
        # Wait for the sub menu to be available, then click
        #sub_menu_system_settings = WebDriverWait(cm.FIREFOX_DRIVER, 10).until(
        #    ec.presence_of_element_located((By.ID, SUB_MENU_SYSTEM_SETTINGS))
        #)
        sub_menu_system_settings = cm.FIREFOX_DRIVER.find_element(By.ID, SUB_MENU_SYSTEM_SETTINGS)
        sub_menu_system_settings.click()

    def navigate_to_va_settings_page(self):
        """ Click "Administration > Scanning / Analysis" to enter VA settings pages
            @Params:
                None
            @Return:
                None
        """
        # Switch focus to the top document 
        cm.FIREFOX_DRIVER.switch_to_default_content()
		
        # Click the "Administration" menu
        menu_admin = cm.FIREFOX_DRIVER.find_element(By.ID, MENU_ADMIN)
        #ac = ActionChains(cm.FIREFOX_DRIVER)
        #ac.move_to_element(menu_admin)
        #ac.perform()
		#menu_admin = WebDriverWait(cm.FIREFOX_DRIVER, EXPLICIT_WAIT_TIME).until(
        #    ec.presence_of_element_located((By.ID, MENU_ADMIN))
        #)
        menu_admin.click()
        # Wait for the sub menu to be available, then click
        sub_menu_va_settings = cm.FIREFOX_DRIVER.find_element(By.ID, SUB_MENU_VA_SETTINGS)
        sub_menu_va_settings.click()

