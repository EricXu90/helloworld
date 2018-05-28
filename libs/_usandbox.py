__author__ = 'jone_zhang'

from _baselib import KeywordBase
import time
import conf
import os

class SandboxKeywords(KeywordBase):
    """
    This library contain all related keywords about U-sandbox function
    """
    def set_sandbox_switch(self, parameter=0):
        """ Close or Open usandbox ...

        @Param:

            parameter: Default parameters is 0
                       0 indicates closing usandbox,
                       1 indicates opening usandbox

        Return:

            None

        Example:

        | Set Sandbox Switch | 1 |

        """
        SANDBOX_SETTING_FILE = "/opt/trend/ddei/config/sandbox_filter.xml"
        cmd_sandbox_swtich = "sed -i -e '/va_is_ready/d' -e '/<config>/a <va_is_ready>%s<\/va_is_ready>' %s" % (parameter, SANDBOX_SETTING_FILE)
        self.exec_command_on_DDEI(cmd_sandbox_swtich)
        self.exec_command_on_DDEI(conf.RELOAD_POLICY_CMD)


    def email_should_be_analyzed_by_sandbox(self, severity):
        """ Check the final severity should be expected after analysis

        @Param:

            severity:    the expected severity after analysis

        Return:

            None

        Example:

        | Email Should Be Analyzed By Sandbox | 3 |

        """
        #check whether sandbox finish analyzing
        sleep_time = 10*60
        while True:
            cmd = "%s 'select %s from %s'" % (conf.PSQL_EXE, 'status','tb_sandbox_tasks_history')
            value = self.ssh_conn.execute_command(cmd)
            if value.strip() and int(value.strip()) >= 3 :
                break
            time.sleep(2)
            sleep_time -= 2
            if sleep_time < 0:
                raise AssertionError('analyzing time exceeds 5 min')

        cmd = "%s 'select count(*) from %s'" % (conf.PSQL_EXE, 'tb_sandbox_task_details where task_id != 0')
        value = self.ssh_conn.execute_command(cmd)
        if int(value.strip()) == 0:
            raise AssertionError('This sample has not been submit to U-sandbox! Task_id = %s'%value.strip())

        #check policy_event table
	if int(severity) > 0: 
	    cmd = "%s 'select %s from %s'" % (conf.PSQL_EXE, 'msg_id','tb_sandbox_tasks_history')
       	    msg_id = self.ssh_conn.execute_command(cmd)
	    msg_id = msg_id.strip()
            sleep_time = 30
            while True:
                #cmd = "%s 'select %s from %s'" % (conf.PSQL_EXE,'overall_severity','tb_policy_event_total')

		cmd="grep %s /opt/trend/ddei/log/polevt.imss.* | awk -F'\t' '{print $8}' | tail -1" % msg_id
	    	#print cmd 
	    	#print msg_id 
                status = self.ssh_conn.execute_command(cmd)
		print status
		value = status.find('4')
                if value == -1 or sleep_time <= 0:
                    break
                time.sleep(3)
                sleep_time -= 3

            sleep_time = 30
            while True:
                #cmd = "%s 'select %s from %s'" % (conf.PSQL_EXE,'overall_severity','tb_policy_event_total')
	    	cmd = "%s 'select %s from %s'" % (conf.PSQL_EXE, 'overall_severity','tb_policy_event')
            	overall_severity_value = self.ssh_conn.execute_command(cmd)
	    	overall_severity_value = overall_severity_value.strip()	

		if overall_severity_value != '' or sleep_time <=0:
                    break
                time.sleep(2)
                sleep_time -= 2

            if  int(overall_severity_value) != int(severity):
                raise AssertionError('table policy event: overall_severity = %d; it should be %d' % (int(overall_severity_value), int(severity)))

    def config_so_detection(self, value):
        """ Enalbe or Diable SO detection

        Return:

            None

        Example:

        | Config SO Detection| 1 | 

        """
        #update tb_global_setting
        cmd = "%s \"update tb_global_setting set value=%s where name='so_detection_enable'\"" % (conf.PSQL_EXE, value)
        self.ssh_conn.execute_command(cmd)

        self.ssh_conn.execute_command("/opt/trend/ddei/script/S99SO_DETECTION restart")

    def config_TrendX(self, value):
        """ Config TrendX

        Return:

            None

        Example:

        | Config TrendX| 0 | 

        """
        #update tb_global_setting
        cmd = "%s \"update tb_global_setting set value=%s where section='trendx' and name='enable'\"" % (conf.PSQL_EXE, value)
        self.ssh_conn.execute_command(cmd)

        self.ssh_conn.execute_command("/opt/trend/ddei/script/S99IMSS restart")

    def va_report_path(self, msg_id):
        """ Get VA Report Path

        Return:

           VA Report Path 

        Example:

        | VA Report Path | MSG_ID | 

        """
        
        first_dir = msg_id[0]
        second_dir = msg_id[1]
        va_report_dir = '/opt/trend/ddei/queue/sandbox_reports_history/' + first_dir + '/' + second_dir + '/'
        va_report_path = va_report_dir + msg_id + '_report.zip'
        return va_report_path


    def config_sandbox_timeout(self, value):
        """  Config VA timeout setting

        Return:

            None

        Example:

        | Config Sandbox Timeout | 600 | 

        """
        self.ssh_conn.execute_command("sed  -i 's/sandbox_task_timeout *=.*$/sandbox_task_timeout = %s/' /opt/trend/ddei/config/imss.ini" % (value))

        self.force_process_exit("TaskProcessor.pyc", 0)
        self.force_process_exit("task_monitor.pyc", 0)
        self.wait_until_process_is_alive("task_monitor")

    def config_sandbox_network(self, value):
        """  Config Sandbox Network

        Return:

            None

        Example:

        | Config Sandbox Network| management | 

        """
	print "start" 
        self.ssh_conn.execute_command("sed  -i 's/sandbox_network_type *=.*$/sandbox_network_type= %s/' /opt/trend/ddei/config/imss.ini" % (value))
        self.ssh_conn.execute_command("/opt/trend/ddei/script/S99TASKMONITOR restart")
	print "end" 

        self.wait_until_process_is_alive("task_monitor")
        self.wait_until_process_is_alive("TaskProcessor")

    def restore_sandbox_setting(self):
        """ Restore Sandbox Setting

        Return:

            None

        Example:

        | Restore Sandbox Setting

        """
        #debug_all_as_unrated yes or no
        self.ssh_conn.execute_command("mv /etc/resolv.conf.bak /etc/resolv.conf")
	print "Try to restore DNS Setting"

        string=self.ssh_conn.execute_command("/opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py set-cache")
	if string.find('CacheEnable: on') < 0:
		self.config_sandbox_cache('on')
		print "Restored Sandbox Cache"

        string=self.ssh_conn.execute_command("grep ^debug_all_as_unrated /opt/trend/ddei/config/imss.ini")
	print string
	print string.find('yes')
	if string.find('yes') < 0 : 
		self.config_all_url_as_unrated('yes')
		print "Configured all URL as unrated"

        string=self.ssh_conn.execute_command("grep ^sandbox_network_type /opt/trend/ddei/config/imss.ini")
	print string
	print string.find('management')
	if string.find('management') < 0 : 
        	self.ssh_conn.execute_command("sed  -i 's/sandbox_network_type *=.*$/sandbox_network_type= management/' /opt/trend/ddei/config/imss.ini")
        	self.ssh_conn.execute_command("/opt/trend/ddei/script/S99TASKMONITOR restart > /dev/null")
		print "Restored sandbox network to management"

        string=self.ssh_conn.execute_command("grep ^TaskAmountLimit /opt/trend/ddei/u-sandbox/usandbox/config/usandbox.ini")
	print string 
	if string.find('50') < 0 and string.find('100') < 0: 
		self.ssh_conn.execute_command("sed -i 's/^TaskAmountLimit =.*/TaskAmountLimit = 50/' /opt/trend/ddei/u-sandbox/usandbox/config/usandbox.ini")
		self.sandbox_cli('sys-restart')
		print "Restored Sandbox TaskAmountLimit"

        string=self.ssh_conn.execute_command("/opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py sys-getstate")
	#print string.find('maintenance')
	if string.find('maintenance') >= 0:
        	self.ssh_conn.execute_command("/opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py sys-start")
		print "Start Sandbox again!!!"

        string=self.ssh_conn.execute_command("grep ^sandbox_log_level /opt/trend/ddei/config/imss.ini")

	restart_task_agent=0
	if string.find('DEBUG') < 0: 
		self.ssh_conn.execute_command("sed  -i 's/sandbox_log_level *=.*$/sandbox_log_level = DEBUG/' /opt/trend/ddei/config/imss.ini")
		restart_task_agent=1
		print "Restored Sandbox log Level to DEBUG"

        string=self.ssh_conn.execute_command("grep ^sandbox_task_timeout /opt/trend/ddei/config/imss.ini")
	#print string.find('600') 
	if string.find('600') < 0: 
		restart_task_agent=1
        	self.ssh_conn.execute_command("sed  -i 's/sandbox_task_timeout *=.*$/sandbox_task_timeout = 600/' /opt/trend/ddei/config/imss.ini")
		print "Restored Sandbox Timeout"

	if restart_task_agent==1:
        	self.force_process_exit("TaskProcessor.pyc", 0)
        	self.force_process_exit("task_monitor.pyc", 0)

        self.wait_until_process_is_alive("task_monitor")
        self.wait_until_process_is_alive("TaskProcessor")

    def config_sandbox_cache(self, value):
        """  Config Sanbox Cache

        Return:

            None

        Example:

        | Config Sandbox Cache | off | 

        """
        #debug_all_as_unrated yes or no
        self.ssh_conn.execute_command("/opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py set-cache --switch=%s" % (value))

    def sandbox_cli(self, param):
        """  Run U-Sanbox Cli

        Return:

            None

        Example:

        | Sandbox Cli| set-cache --switch off| 

        """
        self.ssh_conn.execute_command("/opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py %s" % (param))

    def config_all_url_as_unrated(self, value):
        """ Make all URL sent to U-sandbox

        Return:

            None

        Example:

        | Config All Url As Unrated|

        """
        #debug_all_as_unrated yes or no
        self.ssh_conn.execute_command("sed  -i '/debug_all_as_unrated *=/d' /opt/trend/ddei/config/imss.ini")
        self.ssh_conn.execute_command("sed  -i '/^\[wrsagent/a\\debug_all_as_unrated=%s' /opt/trend/ddei/config/imss.ini" % (value))
        self.ssh_conn.execute_command("/opt/trend/ddei/script/S99WRSAGENT restart")

    def config_all_as_suspicious(self, value):
        """ Make all URL sent to U-sandbox

        Return:

            None

        Example:

        | Config All As Suspicious | yes | 

        """
        #debug_all_as_unrated yes or no
        self.ssh_conn.execute_command("sed  -i '/^#*debug_all_as_suspicious=.*$/d' /opt/trend/ddei/config/imss.ini")
        self.ssh_conn.execute_command("sed  -i '/^\[email-scan/a\\debug_all_as_suspicious=%s' /opt/trend/ddei/config/imss.ini" % (value))
        self.ssh_conn.execute_command("/opt/trend/ddei/script/S99IMSS restart")

    def blacklist_should_be_parsed(self, type, para_input):
        """ Check the expected blacklist could be output from analysis

        @Param:

            type:    the type of blacklist including file, url, host

            para_input:   the expected blacklist value

        Return:

            None

        Example:

        | Blacklist Should Be Parsed | url | wwww.aaadd.com |

        """
        #check whether sandbox finish analyzing
        sleep_time = 4*60
        while True:
            cmd = "%s 'select %s from %s'" % (conf.PSQL_EXE, 'status','tb_sandbox_tasks_history')
            value = self.ssh_conn.execute_command(cmd)
            if value.strip() and int(value.strip()) == 3:
                break
            time.sleep(20)
            sleep_time -= 20
            if sleep_time < 0:
                raise AssertionError('analyzing time exceeds 4 min')

        #check whether blacklist exists
        if type == 'FILE':
            query_table = 'tb_object_file'
            query_column = 'filename'
            cmd = "%s 'select %s from %s where found_as = 2'" % (conf.PSQL_EXE, query_column,query_table)
        elif type == 'URL':
            cmd = "/opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py op-getblacklist --id %d|grep '<Type>%d'"%(1,conf.URL)
            cli_return = self.ssh_conn.execute_command(cmd)
            if cli_return.strip():
                query_table = 'tb_object_url'
                query_column = 'urlname'
                cmd = "%s 'select %s from %s where found_as = 2'" % (conf.PSQL_EXE, query_column,query_table)
            else:
                raise AssertionError('No %s type blacklist generated!'%type)
        elif type == 'DOMAIN':
            cmd = "/opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py op-getblacklist --id %d|grep '<Type>%d'"%(1,conf.DOMAIN)
            cli_return = self.ssh_conn.execute_command(cmd)
            if cli_return.strip():
                query_table = 'tb_object_host'
                query_column = 'hostname'
                cmd = "%s 'select %s from %s'" % (conf.PSQL_EXE, query_column,query_table)
            else:
                raise AssertionError('No %s type blacklist generated!'%type)
        elif type == 'IP':
            cmd = "/opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py op-getblacklist --id %d|grep '<Type>%d'"%(1,conf.IP)
            cli_return = self.ssh_conn.execute_command(cmd)
            if cli_return.strip():
                query_table = 'tb_object_host'
                query_column = 'hostname'
                cmd = "%s 'select %s from %s'" % (conf.PSQL_EXE, query_column,query_table)
            else:
                raise AssertionError('No %s type blacklist generated!'%type)
        else:
            raise AssertionError('blacklist wrong type:%s'%type)


        rc = self.ssh_conn.execute_command(cmd)
        value_object = rc.strip()

        if (not value_object) or (value_object.find(para_input) == -1):
            print 'value_object:',value_object,'\npara_input:',para_input
            raise AssertionError('blacklist parse not right')

    def set_password_for_sandbox(self, pswd):
        """ Set password used for analyzing compressed file with password

        @Param:

            pswd:    the configured password

        Return:

            None

        Example:

        | Set Password For Sandbox | virus |

        """

        cmd = '%s "%s"' % (conf.CMD_USBX_SET_PSWD, pswd)
        value = self.ssh_conn.execute_command(cmd)
        if pswd not in value:
            raise AssertionError("The password %s can't be set"% pswd)

    def reset_password_for_sandbox(self):
        """ Clear the existing configured passwords

        @Param:

            None

        Return:

            None

        Example:

        | Clear Password For Sandbox |

        """

        cmd = '%s --clear' % conf.CMD_USBX_SET_PSWD
        value = self.ssh_conn.execute_command(cmd)
        if "No password" not in value:
            raise AssertionError("The password can't be reset")

    def check_process_is_alive(self,process):
        """ Check Whether certain process in DDEI is alive

        @Param:

            process:    the process name

        Return:

            None

        Example:

        | Check Process Is Alive | task_monitor |

        """
        if process != 'tmfbed':
            cmd = "ps -ef|grep %s|grep -v grep|awk '{print $2}'" % process
        else:
            cmd = "ps -ef|grep tmfbed|grep -v grep|grep -v feeding|awk '{print $2}'"
        value = self.ssh_conn.execute_command(cmd)
        pid = value.strip()
        if not pid:
            raise AssertionError('the process %s is not alive'% process)

    def wait_until_process_is_alive(self,process):
        """ Wait until certain process in DDEI is alive

        @Param:

            process:    the process name

        Return:

            None

        Example:

        | Wait Until Process Is Alive | task_monitor |

        """
	retry_cnt=0
	while retry_cnt <= 150:
            if process != 'tmfbed':
                cmd = "ps -ef|grep %s|grep -v grep|awk '{print $2}'" % process
            else:
                cmd = "ps -ef|grep tmfbed|grep -v grep|grep -v feeding|awk '{print $2}'"
            value = self.ssh_conn.execute_command(cmd)
            pid = value.strip()
            if not pid:
                retry_cnt += 1
                time.sleep(1)
	    else: 
		break

    def force_process_exit(self, process, sleeptime):
        """ Force certain process to exit in DDEI and sleep for a while

        @Param:

            process:    the process name

            sleeptime:  sleep time for next check

        Return:

            None

        Example:

        | Force Process Exit | task_monitor | 60 |

        """
        if process != 'tmfbed':
            query_cmd = "ps -ef|grep %s|grep -v grep|awk '{print $2}'" % process
        else:
            query_cmd = "ps -ef|grep tmfbed|grep -v grep|grep -v feeding|awk '{print $2}'"
        value = self.ssh_conn.execute_command(query_cmd)        
        pid = value.strip()
        if not pid:
            raise AssertionError('the process %s does not exist'% process)

        kill_cmd = "kill -9 %s" % pid
        self.ssh_conn.execute_command(kill_cmd)
        
        value = self.ssh_conn.execute_command(query_cmd)
        pid = value.strip()
        #if pid:
        #    raise AssertionError('the process %s [pid:%s] has not been killed'% (process,pid))

        time.sleep(int(sleeptime))

    def purge_sandbox_tasks(self):
        """ Purge sandbox tasks of DDEI via ssh connection, if connection is not establised, it will raise an error

        @Param:

            None

        Return:

            None

        Example:

        | Purge Sandbox Tasks |

        """
        purge_cmd = '%s -d %s -U %s -c "delete from %s"' % (conf.PSQL_BIN, conf.DB_NAME, conf.DB_USER, 'tb_sandbox_tasks')
        stdout0 = self.ssh_conn.execute_command(purge_cmd)
        purge_cmd = '%s -d %s -U %s -c "delete from %s"' % (conf.PSQL_BIN, conf.DB_NAME, conf.DB_USER, 'tb_sandbox_tasks_history')
        stdout1 = self.ssh_conn.execute_command(purge_cmd)
        purge_cmd = '%s -d %s -U %s -c "delete from %s"' % (conf.PSQL_BIN, conf.DB_NAME, conf.DB_USER, 'tb_sandbox_task_details')
        stdout2 = self.ssh_conn.execute_command(purge_cmd)
        print 'Delete from sandbox table:\n tasks: ' + stdout0 + ' history: ' + stdout1 + ' details: ' + stdout2

        #purge from sandbox queue
        #self.ssh_conn.execute_command(conf.CMD_USBX_PURGE_BLACKLIST)
        #stdout_cache = self.ssh_conn.execute_command(conf.CMD_USBX_PURGE_CACHE)
        #stdout_task = self.ssh_conn.execute_command(conf.CMD_USBX_PURGE_TASK)

        print 'Purge sandbox tasks success'

    def add_custom_file_type(self, file_type):
        """ Add Custom File Type For U-Sandbox Setting

        @Param:

            file_type:   the custom file type value

        Return:

            None

        Example:

        | Add Custom File Type | pdf |

        """
        cmd_add_file_type = conf.CMD_ADD_FILE_TYPE % file_type

        self.ssh_conn.execute_command(conf.CMD_RESET_ALL_FILE_TYPE)
        self.ssh_conn.execute_command(cmd_add_file_type)
        self.ssh_conn.execute_command(conf.RELOAD_POLICY_CMD)

    def clear_custom_file_type(self):
        """ Clear All custom file type setting

        @Param:

            None

        Return:

            None

        Example:

        | Clear Custom File Type |

        """
        self.add_custom_file_type('')
    def check_sandbox_ramdisk_is_enable(self):
        """ Check Whether RAMDISK in DDEI is enable.

        @Param:

            None

        Return:

            None

        Example:

        | Check Sandbox Ramdisk Is Enable |

        """
        cmd = "df |grep /var/app_data/VM_ramdisk | awk '{print $3}'"
        value = self.ssh_conn.execute_command(cmd)
        used = value.strip()
        if not used:
            raise AssertionError('the RAMDISK is not enable')

    def check_sandbox_mip_is_loaded(self):
        """ Check Whether MIP Pattern is loaded in sandbox.

        @Param:

            None

        Return:

            None

        Example:

        | Check Sandbox Mip Is Loaded |

        """
        cmd = "/opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py version"
        value = self.ssh_conn.execute_command(cmd)
        if "ATSE SMV pattern" not in value:
            raise AssertionError("The MIP isn't loaded")

    def check_vbox_memory_leak_monitor(self):
        """ Check Whether Vbox Memory Leak Monitor is enable in sandbox.

        @Param:

            None

        Return:

            None

        Example:

        | Check Vbox Memory Leak Monitor |

        """
        cmd = "grep 'MonitorMemUsageEnable' /opt/trend/ddei/u-sandbox/usandbox/config/watchdog.ini"
        value = self.ssh_conn.execute_command(cmd)
        if "MonitorMemUsageEnable = 1" not in value:
            raise AssertionError("The VBoxSVC Memory Leak Monitor is not enabled")

        cmd = "grep 'MonitorMemUsageProcessList' /opt/trend/ddei/u-sandbox/usandbox/config/watchdog.ini"
        value = self.ssh_conn.execute_command(cmd)
        if "MonitorMemUsageProcessList = VBoxSVC" not in value:
            raise AssertionError("The VBoxSVC Memory Leak Monitor is not enabled")

    def check_sandbox_wrs_reason(self):
        """ Check Whether Sandbox WRS Reason is enable in sandbox.

        @Param:

            None

        Return:

            None

        Example:

        | Check Sandbox Wrs Reason | 

        """
        cmd = "sed -n '/^\[WIS/{n;p}' /opt/trend/ddei/u-sandbox/usandbox/config/usandbox.ini"
        value = self.ssh_conn.execute_command(cmd)
        if "Enabled = 1" not in value:
            raise AssertionError("The Sandbox WRS Reason is not enabled")

    def check_sandbox_network_type(self):
        """ Check Whether Sandbox Network type should be correct. 

        @Param:

            None

        Return:

            None

        Example:

        | Check Sandbox Network Type | 

        """
        cmd = " grep sandbox_network_type /opt/trend/ddei/imss.ini"
        value = self.ssh_conn.execute_command(cmd)

        cli_cmd = "/opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py set-gateway"
        cli_return= self.ssh_conn.execute_command(cli_cmd)
        if "management" in value and "Type: nat" not in cli_return:
            raise AssertionError("The Sandbox network type: management is configured failed")
        if "management" in value and "Type: nat" in cli_return and "NatBindIP: N/A" not in cli_return:
            raise AssertionError("The Sandbox network type: management is configured failed")
        if "isolated" in value and "Type: isolated" not in cli_return:
            raise AssertionError("The Sandbox network type: isloated is configured failed")
        if "specified" in value and "Type: nat" not in cli_return:
            raise AssertionError("The Sandbox network type: custom is configured failed")

    def URL_should_be_send_to_sandbox(self, url):
        """ Check the final severity should be expected after analysis

        @Param:

            url:    the url detail sent to sandbox

        Return:

            None

        Example:

        | url Should Be send to Sandbox | http://www.baidu.com/|

        """
        #check whether sandbox finish analyzing
        sleep_time = 10*60
        while True:
            cmd = "%s 'select %s from %s'" % (conf.PSQL_EXE, 'status','tb_sandbox_tasks_history')
            value = self.ssh_conn.execute_command(cmd)
            if value.strip() and int(value.strip()) >= 1 :
                break
            time.sleep(2)
            sleep_time -= 2
            if sleep_time < 0:
                raise AssertionError('analyzing time exceeds 5 min')

        cmd = "%s \"select count(*) from %s where file_url = '%s' \"" % (conf.PSQL_EXE, 'tb_sandbox_task_details',url)
        value = self.ssh_conn.execute_command(cmd)
        if int(value.strip()) == 0:
            raise AssertionError('This sample has not been submit to U-sandbox!')
	

    def connection_type_should_be_correct(self):
        """ Check Connnection Type Value in DB Should Be Correct

        @Param:

            connnection_type:   the connection type value

        Return:

            None

        Example:

        | Connection Type Should Be Correct |

        """
        cmd = " grep sandbox_network_type /opt/trend/ddei/imss.ini"
        value = self.ssh_conn.execute_command(cmd)

        if "management" in value:
            cnt = self.get_log_count_on_DDEI(conf.TABLE_SBX_REPORT_IMAGES, "connection_type='management'")
            if int(cnt) == 0:
                raise AssertionError("The Connection isn't correct")
        if "specified" in value:
            cnt = self.get_log_count_on_DDEI(conf.TABLE_SBX_REPORT_IMAGES, "connection_type='custom'")
            if int(cnt) == 0:
                raise AssertionError("The Connection isn't correct")
        if "isolated" in value:
            cnt = self.get_log_count_on_DDEI(conf.TABLE_SBX_REPORT_IMAGES, "connection_type='isolate'")
            if int(cnt) == 0:
                raise AssertionError("The Connection isn't correct")
