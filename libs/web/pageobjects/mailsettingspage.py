# -*- coding: utf-8 -*-
# @Date    : 2015-03-26 19:14:07
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

import os

from selenium.webdriver.common.by import By

from web.constants.elemlocators import *
import common as cm

class MailSettings(object):
    """Encapsulate operations which may be done in MailSettings Page"""
    
    def __init__(self):
        super(MailSettings, self).__init__()

    def switch_to_connections(self):
        MailSettings._switch_to_top_document()
        cm.FIREFOX_DRIVER.find_element(By.ID, TAB_CONNECTIONS).click()

    def switch_to_message_delivery(self):
        MailSettings._switch_to_top_document()
        cm.FIREFOX_DRIVER.find_element(By.ID, TAB_MESSAGE_DELIVERY).click()

    def switch_to_limits_Exceptions(self):
        MailSettings._switch_to_top_document()
        cm.FIREFOX_DRIVER.find_element(By.ID, TAB_LIMITS_EXCEPTIONS).click()

    def switch_to_smtp_greeting(self):
        pass