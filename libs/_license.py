__author__ = 'jone_zhang'

from _baselib import KeywordBase
import conf
import time
import datetime

class LicenseKeyword(KeywordBase):
    """
    This library contain all related keywords about update function: license activation
    """

    def activate_product_with_code(self, ac_type, ac_code):
        """ Activate product with AC code

        @Param:

            ac_code:    product AC code

        Return:

            None

        Example:

        | Activate Product With Code | DE-3HNV-SYP2C-73JZ3-4JVZM-NJDE9-PNLDM |

        """
        ac_num = 0
        ac_file = ""
        if ac_type == "atd":
            ac_num = 0
            ac_file = "accode_atd"
        elif ac_type == "seg":
            ac_num =1
            ac_file = "accode_seg"
        activate_cmd = "/opt/trend/ddei/script/pr_active.sh -registini %s %s" % (ac_num, ac_code)
        message = self.exec_command_on_DDEI(activate_cmd)
        #self.exec_command_on_DDEI(conf.CMD_RESTART_SCANNER)
        print message
        write_to_file_cmd = "echo -n %s > /opt/trend/ddei/config/%s" % (ac_code, ac_file)
        res = self.exec_command_on_DDEI(write_to_file_cmd)
        print res
        return message


    def get_license_status(self, ac_type):
        """ Get current license status

        @Param:

            None

        Return:

            None

        Example:

        | ${license_status}= | Get License Status |

        """
        ac_num = 0
        if ac_type == "atd":
            ac_num = 0
        elif ac_type == "seg":
            ac_num =1
        get_ac_status = "/opt/trend/ddei/script/pr_active.sh -stat %s | grep 'PR_ID'" % ac_num
        return self.exec_command_on_DDEI(get_ac_status)


    def license_status_should_be_equal(self, current_status, expected_status):
        """ Check the product license status

        @Param:

            expected_status:    product license status ( Include: 'EXPIRED', 'NON_EXPIRED', 'NON_ACTIVATED' )

            current_status:     current license status got from ddei

        Return:

            None

        Example:

        | License Status Should Be Equal | ${license_status} | {License_Activated} |

        """
        if current_status.find(expected_status.upper()) == -1:
            raise AssertionError("Current license status: %s is not expected." % current_status)


    def au_should_be_disabled(self):
        """ Check the au function should be disabled when license is expired or not activated

        @Param:

            None

        Return:

            None

        Example:

        | AU Should Be Disabled |

        """
        self.exec_command_on_DDEI(conf.CMD_UPDATE_SC)

        mark = "not allowed to do update by current product license status"
        check_cmd = "tail /opt/trend/ddei/log/imsstasks.* | grep '%s'" % mark
        result = self.exec_command_on_DDEI(check_cmd)

        if result == '':
            raise AssertionError("The au function is NOT disabled.")


    def scan_should_be_disabled(self):
        """ Check that the scan function should be disabled

        @Param:

            None

        Return:

            None

        Example:

        | Scan Should Be Disabled |

        """
        mark = "license wasn't activated"
        check_cmd = 'grep "%s" /opt/trend/ddei/log/log.imss.*' % mark
        result = self.exec_command_on_DDEI(check_cmd)

        if result == '':
            raise AssertionError("The scan function is NOT disabled.")


    def change_license_to_expired(self):
        """ Change license status to expired by modifying system time setting

        @Param:

            None

        Return:

            None

        Example:

        | Change License To Expired |

        """
        self.exec_command_on_DDEI("date -s '%s'" % conf.CMD_SET_EXPIRE_TIME)
        #self.exec_command_on_DDEI(conf.CMD_RESTART_SCANNER)



    def change_license_to_not_activated(self, ac_type="both"):
        """ Change license to not activated

        @Param:

            None

        Return:

            None

        Example:

        | Change License To Not Activated |

        """
        deactivate_cmd = "/var/app_data/pr_ddei_test.sh clear_ac %s" % ac_type
        self.exec_command_on_DDEI(deactivate_cmd)
        #self.exec_command_on_DDEI(conf.CMD_RESTART_SCANNER)


    def restore_license_expired_status(self):
        """ Restore system time

        @Param:

            None

        Return:

            None

        Example:

        | Restore License Expired Status |

        """
        self.exec_command_on_DDEI("date -s '%s'" % self.cur_ddei_time)
        #self.exec_command_on_DDEI(conf.CMD_RESTART_SCANNER)

    def get_func_stauts(self, func_type = "all"):
        func_list = []
        lnum = 0
        sh_cmd = "/var/app_data/pr_ddei_test.sh func_status"
        func_content = self.exec_command_on_DDEI(sh_cmd)
        print(func_content)
        fp = open("func_file" , "w")
        fp.write(func_content)
        fp.close()
        fp = open("func_file" , "r")
        if func_type == "atd":
            for line in fp.readlines()[0:11]:
                func_list.append(line.strip("\n"))
        elif func_type == "seg":
            for line in fp.readlines()[11:17]:
                func_list.append(line.strip("\n"))
        elif func_type == "au":
            for line in fp.readlines()[25:27]:
                func_list.append(line.strip("\n"))
        elif func_type == "common":
           for line in fp.readlines()[17:25]:
               func_list.append(line.strip("\n"))
        elif func_type == "all":
            return func_content
        return func_list

    def Restore_system_time(self):
        """ Change license status to expired by modifying system time setting

        @Param:

            None

        Return:

            None

        Example:

        | Change License To Expired |

        """
        current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        utc_time = datetime.datetime.utcnow()
        print utc_time
        self.exec_command_on_DDEI("date -s '%s'" % utc_time)
        #self.exec_command_on_DDEI(conf.CMD_RESTART_SCANNER)


    def change_license_to_golden_expired(self):
        """ Change license status to expired by modifying system time setting

        @Param:

            None

        Return:

            None

        Example:

        | Change License To Expired |

        """
        self.exec_command_on_DDEI(conf.CMD_SET_GRACE_EXPIRE_TIME)
        #self.exec_command_on_DDEI(conf.CMD_RESTART_SCANNER)

    def change_system_time(self, specific_time):
        self.exec_command_on_DDEI("date -s '%s'" % specific_time)
        #self.exec_command_on_DDEI(conf.CMD_RESTART_SCANNER)

    def pr_server_check_active(self):
        mark = "PrServerUpdateURL"
        check_cmd = "tail -80 /opt/trend/ddei/log/pr_cmd.log | grep '%s'" % mark
        #cmd = "tail /opt/trend/ddei/log/pr_cmd.log"
        result = self.exec_command_on_DDEI(check_cmd)
        print result

        if result == '':
            raise AssertionError(" pr didn't try to connect PR server to do online check")

    def pr_server_check_refresh(self):
        mark = "PrServerUpdateURL"
        check_cmd = "tail -320 /opt/trend/ddei/log/pr_cmd.log | grep '%s'" % mark
        #cmd = "tail /opt/trend/ddei/log/pr_cmd.log"
        result = self.exec_command_on_DDEI(check_cmd)
        print result

        if result == '':
            raise AssertionError(" pr didn't try to connect PR server to do online check")

    def change_fake_pr_server(self, ip):
        sql_change_cmd = "update tb_global_setting set value='http://%s/PR/PrSrv.dll' where name='PrServerUpdateURL';" % ip
        sql_check_cmd = "select * from tb_global_setting where section='Registration';"
        sql_off_proxy_cmd = "update tb_global_setting set value='no' where section = 'Update' and name = 'UseProxySetting';"
        self.exec_sql_command_on_DDEI(sql_change_cmd)
        self.exec_sql_command_on_DDEI(sql_off_proxy_cmd)
        check_pr_server = self.exec_sql_command_on_DDEI(sql_check_cmd)
        print check_pr_server

    def change_pr_server_back(self):
        sql_change_cmd = "update tb_global_setting set value='http://licenseupdate.trendmicro.com/ollu/license_update.aspx' where name='PrServerUpdateURL';"
        sql_check_cmd = "select * from tb_global_setting where section='Registration';"
        sql_on_proxy_cmd = "update tb_global_setting set value='yes' where section = 'Update' and name = 'UseProxySetting';"
        self.exec_sql_command_on_DDEI(sql_change_cmd)
        self.exec_sql_command_on_DDEI(sql_on_proxy_cmd)
        check_pr_server = self.exec_sql_command_on_DDEI(sql_check_cmd)
        print check_pr_server