__author__ = 'Marks_Shen'

from _baselib import KeywordBase
import os
import conf
import time
import shutil
import zipfile
import ConfigParser

class SyncUSBXdataKeywords(KeywordBase):
    """
    Keywords for usandbox detection uploading feature in 2.0 SP1

    """

    SFTP_SVR_PATH = os.path.join(conf.TEST_TOOL_DIR, "sftp")
    SFTP_TEMP = os.path.join(conf.TEST_TOOL_DIR, "sftp_tmp")
    SFTP_INI = "/opt/trend/ddei/config/sftp_upload.ini"

    __unzipPWD = ''
    __uuid = ''
    __filecontain = ''



    def _set_value_in_local_ini(self, iniName, section, option_name, option_value):
        config = ConfigParser.ConfigParser()
        try:
            config.read(iniName)
            config.set(section, option_name, option_value)
            config.write(open(iniName, 'w'))
        except IOError, e:
            raise AssertionError(">> [SFTP]_set_value_in_ini failed: %s" % e)

    def _set_value_in_ini(self, iniName, session, option_name, option_value):
        """
        set DDEI ini setting remotely
        """
        try:
            #sed -i "s/^gogo.*/gogo=enable/g" a
            cmd = 'sed -i \"s/^%s.*/%s=%s/g\" %s' % (option_name, option_name, option_value, iniName)
            print cmd
            self.ssh_conn.execute_command(cmd)
        except IOError, e:
            raise AssertionError(">> [SFTP]_set_value_in_ini failed: %s" % e)

    def _get_value_in_DB(self, table_name, field_name, sql_condition='1=1'):
        """
        Get  field value in table
        """
        cmd = '%s "select %s from %s where %s"' % (conf.PSQL_EXE, field_name, table_name, sql_condition)
        value = self.ssh_conn.execute_command(cmd)
        return value.strip()

    def wait_for_VA_finish(self):
        """
        wait until the VA analysis done
        """
        threshold = 40
        i=0

        while i<=threshold:
            va_status = self._get_value_in_DB("tb_sandbox_tasks_history", "status")
            print "va_status: %s" % va_status
            if va_status != '3':
                time.sleep(10)
            else:
                break
            i+=1
        time.sleep(25)


    def Enable_SFTP_sync(self, SFTP_FILE, SFTP_Svr, SFTP_User,SFTP_Pwd, SFTP_Encrypt, SFTP_Remote_Folder):
        """
        enable the detection sync function
        """
        self.__unzipPWD = SFTP_Encrypt
        print self.SFTP_INI
        self._set_value_in_ini(self.SFTP_INI, "general", "enable", "true")

        self._set_value_in_ini(self.SFTP_INI, "general", "file_contain", SFTP_FILE)
        self.__filecontain = SFTP_FILE
        self._set_value_in_ini(self.SFTP_INI, "sandbox", "sftp_server", SFTP_Svr)
        self._set_value_in_ini(self.SFTP_INI, "sandbox", "sftp_user", SFTP_User)
        self._set_value_in_ini(self.SFTP_INI, "sandbox", "sftp_password", SFTP_Pwd)
        self._set_value_in_ini(self.SFTP_INI, "sandbox", "sftp_put_path", SFTP_Remote_Folder)
        self._set_value_in_ini(self.SFTP_INI, "sandbox", "encrypt_pwd", SFTP_Encrypt)

    def check_SFTP_Server_Files(self, check_option='3'):
        """
        check the data on server after finish uploading
        in this case, sftp server is the same machine of BVT controller
        check_option:
        1: file
        2: url
        3: file and url
        """
        self.__uuid = self._get_value_in_DB("tb_sandbox_tasks_history", "msg_id")

        sftp_server_file = "%s\%s.zip" % (self.SFTP_SVR_PATH, self.__uuid)
        print sftp_server_file
        #start checking the file
        #extract to temp folder
        try:
            zfile = zipfile.ZipFile(sftp_server_file,'r')
            print self.__unzipPWD
            dest_path = "%s\%s" % (self.SFTP_TEMP, self.__uuid)
            zfile.extractall(dest_path, None, self.__unzipPWD)

            #tar = tarfile.open(sftp_server_file)
            #tar.extract(conf.SFTP_TEMP_FOLDER)
            #tar.close()
        except IOError, e:
            raise AssertionError(">> [SFTP]extract zip fail: %s" % e)

        if "1" in self.__filecontain:
            #do the sample check
            self._chkSample(check_option)

        if "2" in self.__filecontain:
            #do the original mail check
            self._chkMail()

        if "3" in self.__filecontain:
            #do the report check
           self._chkReport()

    def _chkSample(self, type):
        print "Checking samples"
        sample_list = ["attachment.txt", "url.txt", "password.txt", "attachment"]
        for sample_file in sample_list:
            if not os.path.exists("%s\%s\%s" % (self.SFTP_TEMP, self.__uuid, sample_file)):
                raise AssertionError("The specified file does not exist: %s\%s\%s" % (self.SFTP_TEMP, self.__uuid, sample_file))
            #check attachment
            if type is '1':
                #check file sample
                self.__checkattachment()
            if type is '2':
                #check url
                self.__checkurl()
            if type is '3':
                self.__checkattachment()
                self.__checkurl()


    def __checkattachment(self):

        a=1


    def __checkurl(self):
        b=1

    def _chkMail(self):
        print "Checking samples"
        self.chk_item("%s\%s\%s.AF" % (self.SFTP_TEMP, self.__uuid, self.__uuid))
        self.chk_item("%s\%s\%s.DF" % (self.SFTP_TEMP, self.__uuid, self.__uuid))


    def _chkReport(self):
        print "Checking reports"
        self.chk_item("%s\%s\%s_report.zip" % (self.SFTP_TEMP,self.__uuid, self.__uuid))

        if 0:
            try:
                zfile = zipfile.ZipFile("%s\%s\%s_report.zip" % (self.SFTP_TEMP, self.__uuid, self.__uuid),'r')
                dest_path = "%s\%s\%s_report" % (self.SFTP_TEMP, self.__uuid, self.__uuid)
                zfile.extractall(dest_path)
            except IOError, e:
                raise AssertionError(">> [SFTP]extract report zip fail: %s" % e)

            file_sha1 = self._get_value_in_DB("tb_object_file", "sha1", "severity!=0")
            url_sha1 = self._get_value_in_DB("tb_object_url", "sha1", "severity!=0")

            allsha1 = file_sha1 + url_sha1
            print "***file sh1: %s" % allsha1
            for sha1 in allsha1:
                self.chk_item("%s\%s_report\%s.zip" % (self.SFTP_TEMP, self.__uuid, sha1))
                self.chk_item("%s\%s_report\%s.report.xml" % (self.SFTP_TEMP, self.__uuid, sha1))


    def chk_item(self, itempath):
        if not os.path.exists(itempath):
            raise AssertionError("The specified file does not exist: %s" % itempath)
        if os.path.getsize(itempath) == 0:
            raise AssertionError("The specified file size = 0: %s" % itempath)

    def Disable_and_Clear_SFTP_sync(self):
        """
        change config to disable the uploading function
        """
        self._set_value_in_ini(self.SFTP_INI, "general", "enable", "false")
        #clear env
        os.remove("%s\%s.zip" % (self.SFTP_SVR_PATH, self.__uuid))
        shutil.rmtree("%s\%s" % (self.SFTP_TEMP, self.__uuid))


if __name__ == "__main__":
    sftpsync = SyncUSBXdataKeywords()
    sftpsync.check_SFTP_Server_Files()
