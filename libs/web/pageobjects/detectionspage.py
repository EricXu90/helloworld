# -*- coding: utf-8 -*-
# @Date    : 2015-04-02 13:17:59
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : www.trendmicro.com
# @Version : 0.1

import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from web.constants.elemlocators import *
import common as cm

class Detections(object):
    """ Encapsulate the operations in Detections Page"""
    def __init__(self):
        super(Detections, self).__init__()
        self.common_operation = cm.Common()

    def result_should_have_value(self, msg):
        """ After the detections page load, there should have or not
            something shown in the result table.
            @Params:
                msg: message which is supposely exist in the page
            @Return:
                True: message exist in the result
                False: message doesn't exist in the result
        """
        # Switch to middle frame
        self.common_operation.switch_to_middle_frame()

        # Initialize tr locator
        tr_locator = "//table[@id='" + TABLE_QUERY_RESULT + "']/tbody/tr"

        # find tr and initialize tr list
        tr_list = cm.FIREFOX_DRIVER.find_elements(By.XPATH, tr_locator)

        # iterate the tr list
        for i in range(1, len(tr_list) + 1):
            # Initialize each td locator
            td_locator = tr_locator + "[" + str(i) + "]/td"

            # find td and initialize td list in this tr
            td_list = cm.FIREFOX_DRIVER.find_elements(By.XPATH, td_locator)

            # iterate the td list
            for j in range(1, len(td_list) + 1):
                # Initialize cell locator
                cell_locator = td_locator + "[" + str(j) + "]"

                # Extract the cell value in "row i, column j"
                cell_value = cm.FIREFOX_DRIVER.find_element(By.XPATH, cell_locator).text

                # Check if the cell_value == msg
                if cell_value.find(msg) >= 0:
                    # msg exist in the result, then return True
                    return True

        # msg doesn't exist in the result. Then False
        return False

    def result_should_have_rows(self):
        """ After the detections page load, there should have specific
            in the result table.
            @Params:
                None
            @Return:
                Number of rows
        """

    def select_risk_level(self, level=None):
        pass

    def select_action(self, level=None):
        pass

    def input_recipient(self, recipient=None):
        pass

    def select_time_period(self, index=0):
        pass

    def show_advanced_filter(self):
        pass

    def click_search(self):
        pass
