# -*- coding: utf-8 -*-
# @Date    : 2015-04-15 15:40:21
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1


from web.pageobjects.scanandanalysispage import ScanAndAnalysis


class AnalysisKeywords(object):
    """ Class AnalysisKeywords provides keywords which can be
    used to operate on page Archive Passwords.
    """

    def __init__(self):
        """ Initialization on creating ScanAndAnalysis object """
        super(AnalysisKeywords, self).__init__()
        self.scan_and_analysis = ScanAndAnalysis()

    def switch_to_archive_passwords(self):
        """ Click "Archive Passwords" in the left menu to
        enter page which add archive passwords.

        @Params:
            None
        @Return:
            None
        Example:
        | Switch To Archive Passwords |
        """
        self.scan_and_analysis.switch_to_archive_passwords_page()

    def add_password(self, password):
        """ Click "Add Password" link to add a password.

        @Params:
            None
        @Return:
            None
        Example:
        | Add Password |
        """
        self.scan_and_analysis.add_password(password)

    def import_password(self, file_path):
        """ Click "Import Password" link to import passwords from a file.

        @Params:
            file_path: absolute file path of password file
        @Return:
            None
        Example:
        | Import Password | C:\Users\Administrator\Desktop\password.txt |
        """
        self.scan_and_analysis.import_password(file_path)

    def import_invalid_password(self, file_path):
        """ Click "Import Password" link to import passwords
        which may have invalid format from a file.

        @Params:
            file_path: absolute file path of password file
        @Return:
            err_msg: message indicated the invalidation
        Example:
        | Import Invalid Password | C:\Users\Administrator\Desktop\password.txt |
        """
        return self.scan_and_analysis.import_invalid_password(file_path)

    def get_password(self, index=0):
        """ Get the specific password from web console.

        @Params:
            index: location of the password which will be gotten out
                   (start from 0).
        @Return:
            value: string of password
        Example:
        | Get Password | 2 |
        """
        return self.scan_and_analysis.get_password(int(index))

    def get_all_passwords(self):
        """ Get all of passwords from web console.

        @Params:
            None
        @Return:
            list: list of password
        Example:
        | Get All Passwords |
        """
        return self.scan_and_analysis.get_password(-1)

    def delete_password(self, index):
        """ Delete the specific password from web console.

        @Params:
            index: location of the password which will be deleted
                   (start from 0)
        @Return:
            None
        Example:
        | Delete Password | 2 |
        """
        self.scan_and_analysis.delete_password(int(index))

    def delete_all_passwords(self):
        """ Delete all of exist passwords.

        @Params:
            None
        @Return:
            None
        Example:
        | Delete All Passwords |
        """
        self.scan_and_analysis.delete_password(-1)

    def download_sample_password(self):
        """ Download the sample password file to local.

        @Params:
            None
        @Return:
            None
        Example:
        | Download Sample Password |
        """
        self.scan_and_analysis.download_sample_password()

    def save_password_setting(self):
        """ Click "Save" button to save the added/imported passwords.

        @Params:
            None
        @Return:
            None
        Example:
        | Save Password Setting |
        """
        self.scan_and_analysis.save()

    def cancel_password_setting(self):
        """ Click "Cancel" to cancel the operations on passwords.

        @Params:
            None
        @Return:
            None
        Example:
        | Cancel Password Setting |
        """
        self.scan_and_analysis.cancel()

    def cancel_import_password(self):
        """ Cancel to import passwords.

        @Params:
            None
        @Return:
            None
        Example:
        | Cancel Import Password |
        """
        self.scan_and_analysis.cancel_import()

    def confirm_import_password(self):
        """ Confirm to import passwords.

        @Params:
            None
        @Return:
            None
        Example:
        | Confirm Import Password |
        """
        self.scan_and_analysis.confirm_import()

    def filter_password(self, filter_value):
        """ Filter the specifict passwords out of which will be imported.

        @Params:
            filter_value: text indicates what kinds of passwords
                          will be filtered.
        @Return:
            count: how many passwords were filtered out.
        Example:
        | Filter Password | To Be Imported |
        """
        return self.scan_and_analysis.filter_import_password(filter_value)
