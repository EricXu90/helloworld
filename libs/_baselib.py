__author__ = 'jone_zhang'

import os
import re
import subprocess
import time
import email
import ConfigParser
import SSHLibrary

import errno
import conf
import smtplib


from email.mime.text import MIMEText
from email import encoders
from email.header import Header
from email.utils import parseaddr,formataddr
from logger import logerror,loginfo

class KeywordBase:
    """
    This library is created to peform DDEI related basic operations.

    """

    def __init__(self):
        """ Init
        """
        self.ssh_conn = SSHLibrary.SSHLibrary()
        self.conn_id = None
        self.test_log_file = ''

    def _write_test_log(self, content):
        """ Write test log

        Internal use only


        self.test_log_file = conf.TEST_LOG_DIR + conf.CASE_ID + '.log'
        if not os.access(conf.TEST_LOG_DIR, os.F_OK):
            os.mkdir(conf.TEST_LOG_DIR)

        ## Get current time
        date_and_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        content = ('[%s]\t' % date_and_time) + content + '\n'
        log = open(self.test_log_file, 'a')
        log.writelines(content)
        log.close()
        """
        pass

    def connect_to_DDEI(self, host = conf.DDEI_IP, prompt = '#'):
        """ Perform connection to DDEI server

        @Param:

            host:   ip of DDEI server, default value is set at ..\common\conf.py

            prompt: default is '#'

        Return:

            If no error occur, it will return connection ID

        Example:

        | Connect To DDEI | 10.64.80.234 | |
        | Connect To DDEI |

        """
        self.conn_id = self.ssh_conn.open_connection(host, prompt)
        #time.sleep(2)
        test_log = 'Connect to DDEI server [%s]: ' % conf.DDEI_IP + str(self.conn_id) + '\n'
        print test_log
        self._write_test_log(test_log)
        return self.conn_id


    def login_DDEI(self, usr = conf.SSH_USR, pwd = conf.SSH_PWD):
        """ Login DDEI via ssh connection

        @Param:

            usr:    DDEI user name, default value is set at ..\common\conf.py

            pwd:    password of the user, default value is set at ..\common\conf.py

        Return:

            If no error occur, login information will be returned

        Example:

        | Login DDEI | root | 111111 |
        | Login DDEI |

        """
        if not self.conn_id:
            raise AssertionError('Connection is not establised yet!')
        else:
            ## Set user name and password as case specified
            conf.SSH_USR = usr
            conf.SSH_PWD = pwd
            rc = self.ssh_conn.login(usr, pwd)
            #time.sleep(2)
            test_log = 'Login DDEI as [%s]\n' % usr + rc
            print test_log
            self._write_test_log(test_log)
            return rc

    def login_DDEI_with_public_key(self, usr = conf.SSH_USR, pwd = conf.SSH_PWD, key = None):
        """ Login DDEI via ssh connection with public key

        @Param:

            usr:    DDEI user name, default value is set at ..\common\conf.py

            pwd:    password of the user, default value is set at ..\common\conf.py

            key:    the path of key file

        Return:

            If no error occur, login information will be returned

        Example:

        | Login DDEI with Public Key | root | 111111 |

        """
        default_key = "DDEI.pub"
        key_file = key
        
        if not key:
            key_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), default_key)

        self.ssh_conn.login_with_public_key(usr, key_file, pwd)

    def exec_command_on_DDEI(self, cmd):
        """ Execute command on DDEI and get result

        @Param:

            cmd:    command to be executed on

        Return:

            The result returned by command

        Example:

        | Exec Command On DDEI | ps |

        """
        result = self.ssh_conn.execute_command(cmd)
        return result.strip()

    def exec_sql_command_on_DDEI(self, sql_cmd):
        """ Execute sql command on DDEI and get result

        @Param:

            sql_cmd:    sql command to be executed on

        Return:

            The result returned by command

        Example:

        | Exec SQL Command On DDEI | select count(*) from tb_policy_event |

        """
        result = self.ssh_conn.execute_command('%s "%s"' % (conf.PSQL_EXE, sql_cmd))
        return result.strip()


    def upload_file_to_DDEI(self, local_file, remote_file):
        """ Upload one file from localhost to DDEI

        @Param:

            local_file:   the uploading file path in local machine

            remote_file:    the file path on DDEI

        Return:

            None

        Example:

        | Upload File To DDEI | c:\test.emal | /root/test.eml |

        """
        self.ssh_conn.put_file(local_file, remote_file)


    def get_file_from_DDEI(self, remote_file, local_file):
        """ Get one file from DDEI to localhost

        @Param:

            remote_file:   the file got from DDEI

            local_file:     the file on DDEI

        Return:

            None

        Example:

        | Get File From DDEI | /root/hello.text | c:\aa.text |

        """
        self.ssh_conn.get_file(remote_file, local_file)

    def get_email_info(self, name, email_path):
        """ Parse email information

        @Param:

            name:    the 'from', 'to', 'subject', 'attach', 'body', 'X-TM-AS-ERS', 'X-TM-AS-SMTP' info of email

            email_path:    the email local path

        Return:

            the 'subject', or 'from', or 'to', or 'attach', or 'body' information of email; if fail, return None

        Example:

        | ${msg_subject}= | Get Email Info | subject | c:\helo.eml |

        """
        info ={}
        attach = []
        body = []

        fp = open(email_path, "r")
        msg = email.message_from_file(fp)
        subject = msg.get("subject")
        h = email.header.Header(subject)
        dh = email.header.decode_header(h)
        info['subject'] = dh[0][0]
        info['from'] = msg.get('from')
        info['to'] = msg.get('to')
        info['x-tm-as-ers']=msg.get('X-TM-AS-ERS')
        info['x-tm-as-smtp']=msg.get('X-TM-AS-SMTP')
        #print info['x-tm-as-smtp'][0]

        for par in msg.walk():
            if not par.is_multipart():
                field = par.get_param("name")
                field_special =  par.get("Content-Disposition") # For parsing special email. Example value: 'attachment; filename=text.ini'
                if field:
                    attach_h = email.header.Header(field)
                    attach_dh = email.header.decode_header(attach_h)
                    attach.append(attach_dh[0][0])
                elif field_special:
                    fname = field.split('=')[1]
                    attach.append(fname)
                else:
                    body.append(par.get_payload(decode=True))

        attach.sort()
        info['attach'] = ';'.join(attach)
        info['body'] = ''.join(body)

        return info.get(name.lower())


    def set_global_setting_on_DDEI(self, section, option_name, option_value):
        """ Modify DDEI global setting on file /opt/trend/dde/config/imss.ini

        @Param:

            section:    the section name

            option_name:    the option setting name in system config file

            option_value:    the set option setting value

        Return:

            None

        Example:

        |Set Global Setting On DDEI | general | debug | debug |

        """
        imss = "/opt/trend/ddei/config/imss.ini"
        imss_local = os.path.join(conf.AUTO_ROOT, 'imss.ini')
        config = ConfigParser.ConfigParser()

        self.get_file_from_DDEI(imss, imss_local)
        config.read(imss_local)
        config.set(section, option_name, option_value)
        config.write(open(imss_local, 'w'))
        self.upload_file_to_DDEI(imss_local, imss)
        self.ssh_conn.execute_command("dos2unix %s" % imss)


    def set_postfix_setting_on_DDEI(self, option_name, option_value):
        """ Modify DDEI postfix setting on file /opt/trend/ddei/postfix/etc/postfix/main.cf

        @Param:

            option_name:    the option setting name in config file

            option_value:    the set option setting value

        Return:

            None

        Example:

        | Set Postfix Setting On DDEI | relayhost | 1.1.1.1 |

        """
        cmd = "%s -c /opt/trend/ddei/postfix/etc/postfix %s=%s" % (conf.POSTCONF, option_name, option_value)
        self.ssh_conn.execute_command(cmd)
        cmd = "service postfix reload"
        self.ssh_conn.execute_command(cmd)

    def get_log_count_on_DDEI(self, table_name, condition='1=1'):
        """ Get DDEI DB related Table log count

        @Param:

            table_name:    DDEI db table name

            condition:     the sql condition

        Return:

            Total log count

        Example:

        | Get Log Count On DDEI | tb_policy_event |

        """
        cmd = '%s "select count(*) from %s where %s"' % (conf.PSQL_EXE, table_name, condition)
        count = self.ssh_conn.execute_command(cmd)
        return count.strip()

    def table_field_value_should_be(self, table_name, field_name, expect_value):
        """ Check DDEI DB related Table field value should be expected

        @Param:

            table_name:    DDEI db table name

            field_name:    DDEI db table field name

            expected_value:     the expected field value

        Return:

            Total log count

        Example:

        | Table Field Value Should Be | tb_policy_event | overall_severity | 3 |

        """
        field_value = self.get_log_field_value_on_DDEI(table_name, field_name)

        if field_value != str(expect_value).strip():
            raise AssertionError("There is no logs found matching field value: %s" % expect_value)


    def set_proxy_server_on_DDEI(self, enable, proxy_ip=conf.LAB_PROXY_SERVER, proxy_port=conf.LAB_PROXY_PORT, proxy_type=conf.LAB_PROXY_TYPE, proxy_user=None, proxy_passwd=None):
        """ Set proxy server setting into database. Still need to reload services after calling.

        @Param:

            enable: enable/disable proxy. 1: enable; 0: disable

            proxy_ip:    the proxy server ip address

            proxy_port:  the proxy server port

            proxy_type:  the proxy server type

        Return:

            None

        Example:

        | Set Proxy Server On DDEI | 1 | 10.204.16.17 | 8087 | http |

        """
        """
        conf_file = "/opt/trend/ddei/config/imss.ini"
        cmd = "sed -i 's/#tmufe_proxy_enable=/tmufe_proxy_enable=yes/g' %s" % conf_file
        self.ssh_conn.execute_command(cmd)
        cmd = "sed -i 's/#tmufe_proxy_type=/tmufe_proxy_type=%s/g' %s" % (proxy_type, conf_file)
        self.ssh_conn.execute_command(cmd)
        cmd = "sed -i 's/#tmufe_proxy_server=/tmufe_proxy_server=%s/g' %s" % (proxy_ip, conf_file)
        self.ssh_conn.execute_command(cmd)
        cmd = "sed -i 's/#tmufe_proxy_port=80/tmufe_proxy_port=%s/g' %s" % (proxy_port, conf_file)
        self.ssh_conn.execute_command(cmd)
        cmd = "sed -i 's/#tmufe_proxy_auth=/tmufe_proxy_auth=/g' %s" % conf_file
        self.ssh_conn.execute_command(cmd)
        self.ssh_conn.execute_command("/opt/trend/ddei/script/S99WRSAGENT restart")
        """

        ##########################################
        # Change to update proxy settings into DB
        # @ Author: Todd_Tong
        # @ Date: 2016/04/11
        ##########################################
##        conf_file = "/opt/trend/ddei/config/imss.ini"
##        cmd = "sed -i 's/^tmufe_proxy_enable/#tmufe_proxy_enable/g' %s" % conf_file
##        self.ssh_conn.execute_command(cmd)
##        cmd = "sed -i 's/^tmufe_proxy_type/#tmufe_proxy_type/g' %s" % conf_file
##        self.ssh_conn.execute_command(cmd)
##        cmd = "sed -i 's/^tmufe_proxy_server/#tmufe_proxy_server/g' %s" % conf_file
##        self.ssh_conn.execute_command(cmd)
##        cmd = "sed -i 's/^tmufe_proxy_port/#tmufe_proxy_port/g' %s" % conf_file
##        self.ssh_conn.execute_command(cmd)
##        cmd = "sed -i 's/^tmufe_proxy_auth/#tmufe_proxy_auth/g' %s" % conf_file
##        self.ssh_conn.execute_command(cmd)
        # SQLs for setting proxy
        sql_enable_proxy = "update tb_global_setting set value='yes' where section='Update' and name='UseProxySetting'"
        sql_disable_proxy = "update tb_global_setting set value='no' where section='Update' and name='UseProxySetting'"
        sql_set_proxy_ip = "update tb_global_setting set value='%s' where section='Update' and name='HTTPProxy'" % proxy_ip
        sql_set_proxy_port = "update tb_global_setting set value='%s' where section='Update' and name='HTTPPort'" % proxy_port
        sql_set_proxy_type = "update tb_global_setting set value='%s' where section='Update' and name='ProxyType'" % proxy_type

        if enable == "0":  # If enable=0, disable proxy
            try:
##                cmd = "sed -i 's/^tmufe_proxy_enable/#tmufe_proxy_enable/g' %s" % conf_file
##                self.ssh_conn.execute_command(cmd)
##                cmd = "sed -i 's/^tmufe_proxy_type/#tmufe_proxy_type/g' %s" % conf_file
##                self.ssh_conn.execute_command(cmd)
##                cmd = "sed -i 's/^tmufe_proxy_server/#tmufe_proxy_server/g' %s" % conf_file
##                self.ssh_conn.execute_command(cmd)
##                cmd = "sed -i 's/^tmufe_proxy_port/#tmufe_proxy_port/g' %s" % conf_file
##                self.ssh_conn.execute_command(cmd)
##                cmd = "sed -i 's/^tmufe_proxy_auth/#tmufe_proxy_auth/g' %s" % conf_file
##                self.ssh_conn.execute_command(cmd)
                self.exec_sql_command_on_DDEI(sql_disable_proxy)
            except Exception as err:
                print("Disable global proxy fail for %s." % err)
                raise
        elif enable == "1":  # If enable=1, enable proxy and set proxy parameters
            try:
##                cmd = "sed -i 's/#tmufe_proxy_enable=.*/tmufe_proxy_enable=yes/g' %s" % conf_file
##                self.ssh_conn.execute_command(cmd)
##                cmd = "sed -i 's/#tmufe_proxy_type=.*/tmufe_proxy_type=%s/g' %s" % (proxy_type, conf_file)
##                self.ssh_conn.execute_command(cmd)
##                cmd = "sed -i 's/#tmufe_proxy_server=.*/tmufe_proxy_server=%s/g' %s" % (proxy_ip, conf_file)
##                self.ssh_conn.execute_command(cmd)
##                cmd = "sed -i 's/#tmufe_proxy_port=.*/tmufe_proxy_port=%s/g' %s" % (proxy_port, conf_file)
##                self.ssh_conn.execute_command(cmd)
##                cmd = "sed -i 's/#tmufe_proxy_auth=.*/tmufe_proxy_auth=/g' %s" % conf_file
##                self.ssh_conn.execute_command(cmd)
                self.exec_sql_command_on_DDEI(sql_enable_proxy)
##                self.exec_sql_command_on_DDEI(sql_set_proxy_type)
##                self.exec_sql_command_on_DDEI(sql_set_proxy_ip)
##                self.exec_sql_command_on_DDEI(sql_set_proxy_port)
            except Exception as err:
                print("Enable global proxy fail for %s." % err)
                raise
        else:
            print("The value for the first argument should be 1 or 0.")
            return
##        cmd = conf.CMD_RESTART_WRSAGENT
##        try:
##            self.exec_command_on_DDEI(cmd)
##        except Exception as err:
##            print("Stop WRSAGENT fail for : %s" % err)
##            raise
##        cmd = conf.CMD_RESTART_SAAGENT
##        try:
##            self.exec_command_on_DDEI(cmd)
##        except Exception as err:
##            print("Stop SAAGENT fail for : %s" % err)
##            raise
##        cmd_stop = conf.CMD_RESTART_TASKPROCESSOR
##        cmd_start = "python /opt/trend/ddei/bin/sandbox/TaskProcessor.pyc >/dev/null 2>&1 &"
##        try:
##            self.exec_command_on_DDEI(cmd_stop)
##            time.sleep(1)
##        except Exception as err:
##            print("Stop TaskProcessor fail for : %s" % err)
##            raise
##        cmd = conf.CMD_USBX_RELOAD_PROXY
##        try:
##            self.exec_command_on_DDEI(cmd)
##        except Exception as err:
##            print("Reload usandbox proxy fail for : %s" % err)
##            raise

    def get_log_field_value_on_DDEI(self, table_name, field_name, sql_condition='1=1'):
        """ Get DDEI DB Log field value

        @Param:

            table_name:    DDEI db table name

            field_name:    the field name of table

        Return:

            the log field value

        Example:

        |Get Log Field Value On DDEI | tb_policy_event | overall_severity | overall_severity=0 |

        """
        cmd = '%s "select %s from %s where %s limit 1"' % (conf.PSQL_EXE, field_name, table_name, sql_condition)
        value = self.ssh_conn.execute_command(cmd)
        return value.strip()

    def send_test_report(self, cmd = conf.CMD_SEND_REPORT):
        """ Send Test Report By Email

        @Param:

            cmd:    the command for sending report

        Return:

            None

        Example:

        | Send Test Report |

        """
        subprocess.Popen(cmd, shell = True)

    def setup_DDEI_configuration(self, host = conf.DDEI_IP, usr = conf.SSH_USR, pwd = conf.SSH_PWD):
        """
        """
        pass

    def purge_DB(self, db_name, table_name):
        """ Purge database of DDEI via ssh connection, if connection is not establised, it will raise an error

        @Param:

            db_name:    name of database of DDEI (ddei or usboxdb)

            table_name: name of the table that want to purge

        Return:

            None

        Example:

        | Purge DB | ddei | tb_archive |

        """
        if not self.conn_id:
            raise AssertionError('Connection is not established yet!')
        else:
            purge_cmd = '%s -d %s -U %s -c "delete from %s"' % (conf.PSQL_BIN, db_name, conf.DB_USER, table_name)
            stdout = self.ssh_conn.execute_command(purge_cmd)
            test_log = 'Purge DDEI DB:\n' + stdout
            print test_log
            self._write_test_log(test_log)

    def get_process_pid_on_ddei(self, process_name):
        """ Get specific process id on DDEI

        @Param:

            process_name:    the running process name on ddei

        Return:

            process id

        Example:

        | Get Process PID On DDEI | httpd |

        """
        cmd_get_process_id = "ps -ef | grep %s | grep -v grep |sort -n -k3 | head -1 | awk '{print $2}'" % process_name
        pid_number=self.exec_command_on_DDEI(cmd_get_process_id)
        print 'pid_number:',pid_number
        return pid_number

    def wait_until_process_restart(self, process_name, original_process_id, time_out=60):
        """

        @Param:

            process_name:    the running process name on ddei

            original_process_id:    the original process id

            time_out:   the max wait time

        Return:

            None

        Example:

        | Wait Until Process Restart | httpd | 3241 | 300 |

        """
        cnt = 0
        pid = ''

        if not original_process_id.isdigit():
            raise AssertionError("The compared original PID is a illegal number: %s" % original_process_id)

        while cnt < int(time_out):
            pid = self.get_process_pid_on_ddei(process_name)
            if pid.isdigit() and int(pid) != int(original_process_id):
                return
            time.sleep(2)
            cnt += 2

        raise AssertionError("Wait for %s seconds, but the last returned process PID '%s' is still NOT changed!" % (time_out, pid) )

    def wait_until_process_started(self, process_name, time_out=90):
        """

        @Param:

            process_name:    the running process name on ddei

            time_out:   the max wait time

        Return:

            None

        Example:

        | Wait Until Process Started | httpd | 300 |

        """
        cnt = 0
        pid = ''

        while cnt < int(time_out):
            pid = self.get_process_pid_on_ddei(process_name)
            if pid.isdigit():
                return
            time.sleep(2)
            cnt += 2

        raise AssertionError("Wait for %s seconds, but the process: %s is not started successfully." % (time_out, process_name) )

    def disconnect_from_DDEI(self):
        """ Disconnect from DDEI server, if connection is not establised, it will do nothing except write a 'INFO' log

        @Param:

            None

        Return:

            None

        Example:

        | Disconnect From DDEI |

        """
        if not self.conn_id:
            print 'No connection exists'
        else:
            self.ssh_conn.close_connection()
            print 'Close ssh connection'

    def case_id(self, case_id):
        """ Record case name to name the log

        @Param:

            case_id:    The test name of this case, usually we use robotframework automatic variable ${TEST_NAME}

        Return:

            None

        Example:

        | Case ID | ${TEST_NAME} |
        | Case ID | TS0001 |

        """
        conf.CASE_ID = case_id

    def process_scanner(self):
        """Get scanner process count
        @Param:
            None
        Return:
            Ture or False

        """
        scan_cmd='ps -ef |grep scanner | grep -v grep | wc -l'
        result=self.exec_command_on_DDEI(scan_cmd)
        loginfo("scanner process number:")
        loginfo(result)
        #unicode to int
        result=int(result)
        return result

    def send_one_email(self, to=conf.MAIL_TO, smtp_server = conf.SMTP_SERVER, mail_path = '', mail_from = "bvt@test.com"):
        """ Send an email by ...

        @Param:

            to: receiver or receivers of this mail

            smtp_server:    SMTP server used to delivery this email

            mail_path:  path of eml file

            mail_from:  the email sender address

        Return:

            None

        Example:

        | Send One Email | admin@DDEI.com.cn | 10.204.253.1 | /root/TestDDEI/testdata/testMail.eml |
        | Send One Email | | | /root/TestDDEI/testdata/testMail.eml |

        """
        for num in range(0,10):
            result=self.process_scanner()
            if result > 1:
                break
            elif result == 1:
                loginfo("process scanner is starting")
                time.sleep(4)
            elif result == 0 and num < 3:
                time.sleep(1)
            elif result == 0 and num >= 3:
                logerror("scanner is not started!!!!!")
                return False
        f= open(mail_path,'r')
        msg=email.message_from_file(f)
        f.close()
        to_addr=to.split(';')
        try:
            server=smtplib.SMTP()
            server.connect(smtp_server,25)
            server.sendmail(mail_from,to_addr,msg.as_string())
        except Exception,e:
            logerror(e) 
            time.sleep(5)
            server=smtplib.SMTP()
            server.connect(smtp_server,25)
            server.sendmail(mail_from,to_addr,msg.as_string())
            print 'send retry'
        finally:
            server.quit()
        print 'send successful'

    def send_one_email_with_attachement(self, attach_folder, options):
        """ Send an email with attachement TeMail tool

        @Param:
        options :   -SUBJECT=xxx  -ATTACH=xxxx  body.txt

        Return:

            None

        Example:

        | Send One Email | -ATTACH='details_cedeab.js;WebSecurityLog_MOHW_192.168.23.41_1050630.csv' [body.txt]
        """
        
        save_dir = os.path.abspath(os.curdir)
        os.chdir(attach_folder)
        send_parameters = ' -PORT=25 -FROM=%s -TO=%s -SMTP=%s %s' % ("bvt@test.com", conf.MAIL_TO, conf.SMTP_SERVER, options)
        send_cmd = conf.TEMAIL_BIN + send_parameters
        test_log = 'Send one email with command: %s\n' % send_cmd
        subprocess.Popen(send_cmd, shell=True)
        os.chdir(save_dir)
        self._write_test_log(test_log)
        time.sleep(2)

        
    def get_email_fingerprint_list(self, email_list):
        """ Get email's fingerprint list

        @Param:

            email_path:    the email local path

        Return:

            fingerprint list.

        Example:

        | ${fingerprint_list}= | Get Email Fingerprint List | c:\helo.eml |

        """
        checkpoint_list=[]

        for email_path in email_list:
            if self.get_email_info('subject', email_path).find("Security Warning: Threats or Unscannable Attachments in Email Message")==-1:
                checkpoint_list.append(self.get_email_info('subject', email_path))
            else:
                checkpoint_list.append(self.get_email_info('body', email_path))
        return checkpoint_list

    def check_mail_fingerprint(self, check_type, checkpoint_list, original_subject):
        """ Check mail fingerprint

        @Param:

            check_type:    strip_notify, tag_notify, pass_notify
            checkpoint_list:   ${fingerprint_list}
            original_subject:  ${original_subject}

        Return:

            fingerprint list.

        Example:

        | Get Email Info | strip_notify | ${fingerprint_list} | ${original_subject} |

        """
        mapping_type={'strip_notify':': Pass; Strip; Tag;',
                      'tag_notify':': Pass; Tag;',
                      'pass_notify':'Pass'}
        keyword=mapping_type[check_type]
        
        for checkpoint in checkpoint_list:
            if checkpoint.find(keyword)>-1:
                continue
            elif checkpoint.find(original_subject)> -1:
                continue
            else:
                raise AssertionError("There is a mail which is not expected, the fingerprint: %s"%checkpoint)

        return None
    def get_sbx_task_id(self):
        """ Get running task id from usandbox by parsing "op-getstatus --all" result

        Param:

            None

        Return:

            tuple: return_code (0:success;1:fail); task_list: list which stores all of exist task id

        Example:

            | Get Sbx Task ID |

        """
        task_list = []
        return_code = 0 # 0: success; 1: fail

        try:
            # Get the tasks status
            cmd = ''.join([conf.CMD_USBX_GET_TASK_STATUS, " --all"])
            status = self.exec_command_on_DDEI(cmd)

            # Transfer status string to python dictionary object
            transfered_status = eval(status)
            tasks = transfered_status["Tasks"]

            # Exit if no task
            if not tasks:
                return_code = 1
                return (return_code, task_list)

            # Iterate each task
            for task in transfered_status["Tasks"]:
                task_list.append(task["TaskID"])
        except Exception as err:
            print "Get task id from usandbox fail for %s." % err
            raise

        return (return_code, task_list)

    def parse_sbx_task_status(self, task_id):
        """ Parse out tasks status running inside u-sandbox

        Param:

            task_id: task id which identify a individual task

        Return:

            status_dict: dictionary which store the task status

        Example:

            | Parse Sbx Task Status | 20 |
        """
        try:
            # Get the task status using cli
            cmd = ''.join([conf.CMD_USBX_GET_TASK_STATUS, " --id ", str(task_id)])
            status = self.exec_command_on_DDEI(cmd)

            # Transfer status string to python dictionary object
            transfered_status = eval(status)

            # Parse the transfered status to get specific status and save to a new simple dictionary
            status_dict = transfered_status["Tasks"][0]
        except Exception as err:
            print "Parse usandbox task status fail for %s." % err
            raise

        return status_dict

    def start_usandbox(self):
        """ Start internal usandbox manually

            Author: Todd Tong
            Date: 2016-08-25

        Params:
            None
        Return:
            None
        Example:
            | Start Usandbox |
        """

        cur_stat = self.exec_command_on_DDEI(conf.CMD_USBX_GET_STATE).strip().split("\n")[0]
        if cur_stat == "running":
            print "Internal usandbox is already in state: %s" % cur_stat
            return
        elif cur_stat == "maintenance":
            self.exec_command_on_DDEI(conf.CMD_USBX_START)
            new_stat = self.exec_command_on_DDEI(conf.CMD_USBX_GET_STATE).strip().split("\n")[0]
            if new_stat != "running":
                raise AssertionError("Start usandbox fail.")
            return
        else:
            raise AssertionError("Usandbox is under %s state which cannot be started!" % cur_stat)

    def stop_usandbox(self):
        """ Stop internal usandbox manually

            Author: Todd Tong
            Date: 2016-08-25

        Params:
            None
        Return:
            None
        Example:
            | Stop Usandbox |
        """

        cur_stat = self.exec_command_on_DDEI(conf.CMD_USBX_GET_STATE).strip().split("\n")[0]
        if cur_stat == "maintenance":
            print "Internal usandbox is already in state: %s" % cur_stat
            return
        elif cur_stat == "running":
            self.exec_command_on_DDEI(conf.CMD_USBX_STOP)
            new_stat = self.exec_command_on_DDEI(conf.CMD_USBX_GET_STATE).strip().split("\n")[0]
            if new_stat != "maintenance":
                raise AssertionError("Stop usandbox fail.")
            return
        else:
            raise AssertionError("Usandbox is under %s state which cannot be stopped!" % cur_stat)

    def is_valid_date(self,string,time_format):
        print string
        try:
            time.strptime(string, time_format)
            return True
        except:
            return False

    def change_date_time(self,current,date_time):
        print current
        current_date_time = time.strptime(current,'%Y-%m-%d %H:%M:%S' )
        timestamp = int(time.mktime(current_date_time))
        dateArray = datetime.datetime.fromtimestamp(timestamp)
        new_date = dateArray + datetime.timedelta(minutes=2)
        print new_date
        return new_date


if __name__ == '__main__':
    test=KeywordBase()
    test.process_scanner()