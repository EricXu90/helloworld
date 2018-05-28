# -*- coding: utf-8 -*-
# @Date    : 2015-03-27 09:42:19
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1


from selenium.webdriver.common.by import By

from web.constants.elemlocators import *
import common as cm


class Login(object):
    """Encapsulate operations which may be done in LoginPage"""

    def __init__(self):
        super(Login, self).__init__()

    def open_login_page(self, url):
        """ Open web console with the url
            @Params:
                url: url to be accessed
            @Return:
                None
        """
        cm.FIREFOX_DRIVER.get(url)

    def type_user_name(self, username):
        """ Type in login username
            @Params:
                username: account name
            @Return:
                None
        """
        input_element = cm.FIREFOX_DRIVER.find_element(By.ID, INPUT_USER_NAME)
        input_element.send_keys(username)

    def type_password(self, password):
        """ Type in login user password
            @Params:
                password: account password
            @Return:
                None
        """
        input_element = cm.FIREFOX_DRIVER.find_element(By.ID, INPUT_PASSWORD)
        input_element.send_keys(password)

    def exec_logon(self):
        """ Click the button to logon after input account name/password
            @Params:
                None
            @Return:
                None
        """
    	btn_element = cm.FIREFOX_DRIVER.find_element(By.CSS_SELECTOR, BUTTON_LOG_ON)
    	btn_element.click()
