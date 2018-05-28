__author__ = 'jone_zhang'

from _baselib import KeywordBase
import conf
import subprocess
import os
import shutil
import time

class DPSKeyword(KeywordBase):
    """
    This library contain all related keywords about MTA setting function
    """

    def dps_set_next_deliver_mta(self, mta_addr=conf.LOCAL_HOST, domain='*'):
        """ Set static next delivering MTA. Default is to deliver all emails

        @Param:

            mta_addr:    the next MTA address

            domain:     the email address domain

        Return:

            None

        Example:

        | Set Next Deliver MTA | 192.168.1.1 | test.com |

        """

	deliver_details = "<details><destination address=\\\"%s\\\" port=\\\"25\\\" preference=\\\"10\\\" status=\\\"1\\\" addtime=\\\"1438928752052\\\"/></details>" % (mta_addr)
	current_time =  time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time()))

	insert_deliver_mta_sql = "INSERT INTO tb_delivery_policies (target, policy_type, details, addtime, status) VALUES (\'%s\', 1, \'%s\', \'%s\', 1)" % (domain, deliver_details, current_time)

	self.exec_sql_command_on_DDEI(insert_deliver_mta_sql)

        cmd_reload_dps= "/opt/trend/ddei/script/S99DELIVERY reload"
        self.exec_command_on_DDEI(cmd_reload_dps)
        self.exec_command_on_DDEI("/opt/trend/ddei/postfix/usr/sbin/postfix reload")

        self.exec_command_on_DDEI("postsuper -d ALL")
        time.sleep(10)

    def dps_set_next_deliver_mta_servers(self, deliver_details, domain='*'):
        """ Set static next delivering MTA. Default is to deliver all emails

        @Param:

            mta_addr:    the next MTA address

            domain:     the email address domain

        Return:

            None

        Example:

        | Set Next Deliver MTA Servers | deliver_details | test.com |
	deliver_detials's format is like following:
	
	deliver_details = "<details>\
			<destination address=\\\"192.168.1.1\\\" port=\\\"25\\\" preference=\\\"10\\\" status=\\\"1\\\" addtime=\\\"1438928752052\\\"/>\
			<destination address=\\\"192.168.1.2\\\" port=\\\"25\\\" preference=\\\"10\\\" status=\\\"1\\\" addtime=\\\"1438928752052\\\"/>\
			<destination address=\\\"192.168.1.3\\\" port=\\\"25\\\" preference=\\\"10\\\" status=\\\"1\\\" addtime=\\\"1438928752052\\\"/>\
			<destination address=\\\"host.test.com\\\" port=\\\"25\\\" preference=\\\"10\\\" status=\\\"1\\\" addtime=\\\"1438928752052\\\"/>\
			</details>" 
        """
	print deliver_details
	current_time =  time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time()))

	insert_deliver_mta_sql = "INSERT INTO tb_delivery_policies (target, policy_type, details, addtime, status) VALUES (\'%s\', 1, \'%s\', \'%s\', 1)" % (domain, deliver_details, current_time)

	self.exec_sql_command_on_DDEI(insert_deliver_mta_sql)

        cmd_reload_dps= "/opt/trend/ddei/script/S99DELIVERY reload"
        self.exec_command_on_DDEI(cmd_reload_dps)
        self.exec_command_on_DDEI("/opt/trend/ddei/postfix/usr/sbin/postfix reload")

        self.exec_command_on_DDEI("postsuper -d ALL")
        time.sleep(5)

    def dps_set_next_deliver_mta_as_mx_type(self, mta_mx_record=conf.LOCAL_HOST, domain='*'):
        """ Set next delivering MTA's mx record. Default is to deliver all emails

        @Param:

            mta_mx_record:    the next MTA address (FQDN)

            domain:     the email address domain

        Return:

            None

        Example:

        | Set Next Deliver MTA AS MX TYPE | ddeilab.com | test.com |

        """
#	mta=ddeilab.com
	deliver_details = "<details><mx record=\\\"%s\\\" port=\\\"25\\\"/></details>" % (mta_mx_record)
	current_time =  time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time()))

	insert_deliver_mta_sql = "INSERT INTO tb_delivery_policies (target, policy_type, details, addtime, status) VALUES (\'%s\', 0, \'%s\', \'%s\', 1)" % (domain, deliver_details, current_time)

	self.exec_sql_command_on_DDEI(insert_deliver_mta_sql)

        cmd_reload_dps= "/opt/trend/ddei/script/S99DELIVERY reload"
        self.exec_command_on_DDEI(cmd_reload_dps)
        self.exec_command_on_DDEI("/opt/trend/ddei/postfix/usr/sbin/postfix reload")

        self.exec_command_on_DDEI("postsuper -d ALL")
        time.sleep(10)

    def dps_set_empty_mta(self):
        """ Set next deliver MTA to empty

        @Param:

            None

        Return:

            None

        Example:

        | Set Empty MTA |

        """
	delete_deliver_mta_sql = "delete from tb_delivery_policies"
	self.exec_sql_command_on_DDEI(delete_deliver_mta_sql)

        cmd_reload_dps= "/opt/trend/ddei/script/S99DELIVERY reload"
        self.exec_command_on_DDEI(cmd_reload_dps)

    def dps_clean_email_from_local_mta(self):
        """ Start up local fake MTA

        Return:

            None

        Example:

        | Start Up Local MTA | c:\fakeMTA.exe |

        """
	current_dir = os.path.abspath(os.curdir)
	print current_dir

        for f in os.listdir(current_dir):
            if os.path.isdir(f) and f.isdigit():
                shutil.rmtree(os.path.join(current_dir, f))
