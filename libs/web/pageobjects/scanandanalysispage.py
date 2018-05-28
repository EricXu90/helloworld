# -*- coding: utf-8 -*-
# @Date    : 2015-04-14 16:46:04
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select

from web.constants.elemlocators import *
from web.constants.constants import *
import common as cm


class ScanAndAnalysis(object):

    """ Class ScanAndAnalysis encapsulates the operations of Scanning / Analysis page. """

    def __init__(self):
        """ Initialize Common operation object. """
        super(ScanAndAnalysis, self).__init__()
        self.common_operation = cm.Common()

    ############################### Archive Passwords ###############################
    def switch_to_archive_passwords_page(self):
        """ Click the left menu to archive passwords setting page.

        @Params:
            None
        @Return:
            None
        """
        # Enter left menu frame
        self.common_operation.switch_to_left_frame()

        # Click Archive Passwords sub menu
        element = WebDriverWait(cm.FIREFOX_DRIVER, EXPLICIT_WAIT_TIME).until(
            ec.presence_of_element_located((By.ID, LEFT_MENU_ARCHIVE_PASSWORDS))
        )
        element.click()

        # Enter Archive Passwords settings page
        self.common_operation.switch_to_middle_frame()

    # ==============================
    # Add passwords manually
    # ==============================
    def add_password(self, password):
        """ Add a specific password manually.

        @Params:
            password: password string needs to be added
        @Return:
            None
        """
        # Click "Add Password" link
        cm.FIREFOX_DRIVER.find_element_by_id(SPAN_ADD_PASSWORD).click()

        # Find the input box list
        pw_list = cm.FIREFOX_DRIVER.find_elements_by_xpath(INPUT_PASSWORD_LIST)

        # Add password into the last input box
        pw_list[len(pw_list) - 1].send_keys(password)

    # ==============================
    # Import passwords
    # ==============================
    def import_password(self, file_path):
        """ Imput password(s) stored in a file.

        @Params:
            file_path: absolute path of password file
        @Return:
            None
        """
        # Click "Import Password" link to open import window
        cm.FIREFOX_DRIVER.find_element_by_id(SPAN_IMPORT_PASSWORD).click()

        # Enter sub frame id="ui-tmPopup-Content-Iframe-ui-dialog-title-import"
        frame = WebDriverWait(cm.FIREFOX_DRIVER, EXPLICIT_WAIT_TIME).until(
            ec.presence_of_element_located((By.ID, IFRAME_IMPORT_PASSWORD))
        )
        cm.FIREFOX_DRIVER.switch_to_frame(frame)

        time.sleep(1)

        # Mouse over onto "Browse" button to unhidden the <input> file element
        action_chains = ActionChains(cm.FIREFOX_DRIVER)
        btn_browse = cm.FIREFOX_DRIVER.find_element_by_id(BTN_BROWSE_FILE)
        action_chains.move_to_element(btn_browse).perform()

        # Click the "Input" button to open file select Window
        input_file_btn = WebDriverWait(cm.FIREFOX_DRIVER, EXPLICIT_WAIT_TIME).until(
            ec.presence_of_element_located((By.XPATH, INPUT_UPLOAD_PASSWORD))
        )
        input_file_btn.send_keys(file_path)

    def import_invalid_password(self, file_path):
        """ Import file with certain invalid passwords, then return the error message.

        @Params:
            file_path: absolute path of password file
        @Return:
            error_msg: message indicated the invalidation
        """
        # Import the passwords
        self.import_password(file_path)

        time.sleep(1)

        # Scenario of import more than maximum supported passwords
        # Locate the error message
        cm.ERROR_MESSAGE = cm.FIREFOX_DRIVER.find_element_by_id(SPAN_TOP_ERROR_MSG).text

    def filter_import_password(self, filter_value):
        """ Query the invalid (has unsupported chars or duplicated).

        Note: it should be called after <import_password()>
        @Params:
            filter_value: text selected to filter the expected passwords
        @Return:
            count: the count of invalid passwords
        """
        # find the drop down list in the import review table
        selector = Select(cm.FIREFOX_DRIVER.find_element_by_id(SELECT_PASSWORD_FILTER))
        # Select the expected option based on the filter_value
        filter_value_lower_case = filter_value.lower()
        if filter_value_lower_case == "all items":
            selector.select_by_visible_text(SELECT_OPTION_OF_ALL)
        elif filter_value_lower_case == "to be imported":
            selector.select_by_visible_text(SELECT_OPTION_OF_TO_BE_IMPORTED)
        else:
            selector.select_by_visible_text(SELECT_OPTION_OF_INVALID_PASSWORD)

        tr_list = cm.FIREFOX_DRIVER.find_elements_by_css_selector(TABLE_FILTER_RESULT)
        return len(tr_list)

    def confirm_import(self):
        """ Confirm to import passwords.

        @Params:
            None
        @Return:
            None
        """
        # Click "Import" button to confirm importing
        print "Confirm import..."
        self.common_operation.switch_to_middle_frame()
        print "Switch to middle frame..."
        cm.FIREFOX_DRIVER.find_element_by_xpath(BTN_IMPORT).click()
        print "import completely..."

    def cancel_import(self):
        """ Cancel import passwords.

        @Params:
            None
        @Return:
            None
        """
        # Click "Import" button to confirm importing
        self.common_operation.switch_to_middle_frame()
        cm.FIREFOX_DRIVER.find_element_by_xpath(BTN_CLOSE).click()

    def download_sample_password(self):
        """ Dowload the sample password file by click the <a> link on import password window.

        @Params:
            None
        @Return:
            None
        """
        # Click "Import Password" link to open import window
        cm.FIREFOX_DRIVER.find_element_by_id(SPAN_IMPORT_PASSWORD).click()

        # Enter sub frame id="ui-tmPopup-Content-Iframe-ui-dialog-title-import"
        frame = WebDriverWait(cm.FIREFOX_DRIVER, EXPLICIT_WAIT_TIME).until(
            ec.presence_of_element_located((By.ID, IFRAME_IMPORT_PASSWORD))
        )
        cm.FIREFOX_DRIVER.switch_to_frame(frame)

        time.sleep(1)

        # Click the <a> link "Download sample file"
        cm.FIREFOX_DRIVER.find_element_by_xpath(A_DOWNLOAD_SAMPLE_PASSWORD).click()

        time.sleep(1)

        # Close import password window
        self.common_operation.switch_to_middle_frame()
        time.sleep(1)
        cm.FIREFOX_DRIVER.find_element_by_xpath(BTN_CLOSE).click()

    # ==============================
    # Other operations
    # ==============================
    def get_password(self, passwd_loc):
        """ Get the specific password from UI password list.

        @Params:
            passwd_loc: index of password which will be gotten out (start from 0)
        @Return:
            password: string of the specific password (if passwd_loc >= 0)
            password list: list of all of passwords (if passwd_loc < 0)
        """
        # Find the password input box list
        elems_input_passwd = cm.FIREFOX_DRIVER.find_elements_by_xpath(INPUT_PASSWORD_LIST)

        # Return if the password list is None for there's no exist passwords
        if not elems_input_passwd:
            return None

        # Return all password if passwd_loc < 0
        password_list = []
        if passwd_loc < 0:
            for password in elems_input_passwd:
                value = password.get_attribute("value")
                password_list.append(value)
            return password_list

        # Return the specific password based on passwd_loc if passwd_loc >=0
        value = elems_input_passwd[passwd_loc].get_attribute("value")
        return value

    def update_password(self, passwd_loc, new_passwd):
        """ Update a specific password with a new password.

        @Params:
            passwd_loc: No.X password needs to be updated
            new_passwd: new password string
        @Return:
            None
        """
        pass

    def delete_password(self, passwd_loc):
        """ Delete a specific password.

        @Params:
            passwd_loc: No.x password needs to be deleted
        @Return:
            None
        """
        # Find the remove button list
        rm_btn_list = cm.FIREFOX_DRIVER.find_elements_by_css_selector(SPAN_REMOVE_PASSWORD)

        # Return if the rm_btn_list is None for there's no exist passwords
        if not rm_btn_list:
            return None

        # delete all password if passwd_loc = -1
        if passwd_loc < 0:
            for btn in rm_btn_list:
                btn.click()
            return None

        # delete the specific password based on passwd_loc
        rm_btn_list[passwd_loc].click()

    def save(self):
        """ Save Archive Passwords settings.

        @Params:
            None
        @Return:
            None
        """
        # Click the save button
        cm.FIREFOX_DRIVER.find_element_by_css_selector(BTN_SAVE).click()

        # Wait for the save result message
        WebDriverWait(cm.FIREFOX_DRIVER, EXPLICIT_WAIT_TIME).until(
                    ec.text_to_be_present_in_element((By.ID, SPAN_PASSWORD_INLINE_MESSAGE), SAVE_SUCCESS))

    def cancel(self):
        """ Cancel Archive Passwords settings.

        @Params:
            None
        @Return:
            None
        """
        cm.FIREFOX_DRIVER.find_element_by_css_selector(BTN_CANCEL).click()
