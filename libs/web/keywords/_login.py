# -*- coding: utf-8 -*-
# @Date    : 2015-03-27 09:42:19
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

import os

#from web.constants.pageinstantiation import LOGIN_PAGE, INITIALIZE
from web.pageobjects.loginpage import Login

class LoginPageKeywords(object):
    """This class encapsulates possible operations on login page
       and explore the keywords to RF.
    """
    def __init__(self):
        super(LoginPageKeywords, self).__init__()
        self.login_page = Login()

    def access_login_page(self, url):
        """ launch browser and access to the login page.

        @Param:

            url: destination url which will be accessed.

        Return:

            None

        Example:

        | Access Login Page | https://10.204.253.192/ |
        """
        self.login_page.open_login_page(url)

    def type_in_username(self, username):
        """ input login user name.

        @Param:

            username: login account

        Return:

            None

        Example:

        | Type In Userame | admin |
        """
        self.login_page.type_user_name(username)

    def type_in_password(self, password):
        """ input login password.

        @Param:

            password: login password

        Return:

            None

        Example:
        | Type In Password | trend#1 |
        """
        self.login_page.type_password(password)

    def click_logon(self):
        """ Click logon button to login

        @Param:

            None

        Return:

            None

        Example:
        | Click Logon |
        """
        self.login_page.exec_logon()