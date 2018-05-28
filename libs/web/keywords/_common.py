# -*- coding: utf-8 -*-
# @Date    : 2015-04-22 11:19:15
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

import os

from web.pageobjects.common import Common

class CommonKeywords(object):
    """ CommonKeywords defines several keywords used for common operations
        except page operations
    """
    def __init__(self):
        super(CommonKeywords, self).__init__()
        self.common_operation = Common()

    def launch_browser(self):
        """ Open browser to start web test
            @Params:
                None
            @Return:
                None
            Example:
            | Launch Browser |
        """
        self.common_operation.launch_browser()

    def close_open_browser(self):
        """ Close browser whenever needed
        @Param:
            None
        @Return:
            None
        Example:
        | Close Open Browser |
        """
        self.common_operation.close_browser()

    def get_error_message(self):
        """ Get the error message triggered by FE operation
            @Params:
                None
            @Return:
                error_message: message indicated the invalid operation or setting
            Example:
            | Get Error Message |
        """
        return self.common_operation.get_err_msg()