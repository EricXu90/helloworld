__author__ = 'anne_zhao'

from _baselib import KeywordBase
import conf
import time
import os
import SSHLibrary

class SyslogKeywords(KeywordBase):
    """
    This library contain all related keywords about Syslog function
    """

    def make_connection_to_syslog_server(self, host = '10.204.253.133', usr_nm = 'root', passwd = '123456'):
        """ Perform connection to syslog server

        @Param:

            host:               ip of Syslog server
            user name:          name of login user
            user password:      password of login user

        Return:

            If no error occur, it will return connection ID

        Example:

        | Make Connection To Syslog Server | 10.64.80.234 | admin | 123 |
        | Make Connection To Syslog Server |

        """
        self.syslog_server_ssh_conn = SSHLibrary.SSHLibrary()
        self.syslog_server_conn_id = None
        self.syslog_server_conn_id = self.syslog_server_ssh_conn.open_connection(host)
        print 'Connect to Syslog server: ' + host + str(self.syslog_server_conn_id) + '\n'
        #return self.syslog_server_conn_id
        rc = self.syslog_server_ssh_conn.login(usr_nm, passwd)
        return rc


    def exec_command_on_syslog_server(self, cmd):
        """ Execute command on syslog server and get result

        @Param:

            cmd:    command to be executed on

        Return:

            The result returned by command

        Example:

        | Exec Command On Syslog Server | ps |

        """
        result = self.syslog_server_ssh_conn.execute_command(cmd)
        return result.strip()


    def clean_syslog_on_server(self, log_protocol, ip_tpye = 'IPv4'):
        """ Clean specific syslog on syslog server

        @Param:

            log_protocol:       Send protocol (TCP\UDP\SSL)
            ip_tpye:            IPv4 or IPv6

        Return:

            None

        Example:

        | Clean Syslog On Server | TCP | IPv4 |

        """
        protocol_to_name = {'TCPIPv4':'syslog_via_tcp.log', 'UDPIPv4':'syslog_via_udp.log', 'SSLIPv4':'syslog_via_ssl.log', 'TCPIPv6':'syslog_via_tcp.log', 'UDPIPv6':'syslog_via_udp.log', 'SSLIPv6':'syslog_via_ssl.log'}
        self.exec_command_on_syslog_server('> /var/log/%s' % protocol_to_name[log_protocol + ip_tpye])
        print '" ' + self.exec_command_on_syslog_server('cat /var/log/%s' % protocol_to_name[log_protocol + ip_tpye]) + '" <- should be empty'


    def disconnect_from_syslog_server(self):
        """ Disconnect from syslog server

        @Param:

            None

        Return:

            None

        Example:

        | Disconnect From Syslog Server |

        """
        self.syslog_server_ssh_conn.close_connection()
        print 'Close ssh connection with syslog server'


    def check_login_record_whether_be_recorded(self, log_tpye, log_protocol, ip_tpye = 'IPv4'):
        """ Check if login record is sent to syslog server 

        @Param:

            log_tpye:           the log tpye DDEI send to syslog server (CEF\LEEF\TMEF)
            log_protocol:       Send protocol (TCP\UDP\SSL)
            ip_tpye:            IPv4 or IPv6

        Return:

            None

        Example:

        | Check Login Record Whether Be Recorded | CEF | UDP | IPv4 |

        """
        protocol_to_name = {'TCPIPv4':'syslog_via_tcp.log', 'UDPIPv4':'syslog_via_udp.log', 'SSLIPv4':'syslog_via_ssl.log', 'TCPIPv6':'syslog_via_tcp.log', 'UDPIPv6':'syslog_via_udp.log', 'SSLIPv6':'syslog_via_ssl.log'}

        #db_syslog = self.exec_command_on_DDEI('/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "select * from tb_system_event;" | grep admin | grep Login | grep on')
        logserver_syslog =  self.exec_command_on_syslog_server('cat /var/log/%s' % protocol_to_name[log_protocol + ip_tpye])

        if log_tpye == 'CEF':
            if logserver_syslog.find('CEF') == -1:
                print logserver_syslog
                raise AssertionError("Log type(CEF) error!")
            #db_cef_time = db_syslog.split('\n')[-1].split('|')[2].split()[1]
            #server_cef_time = logserver_syslog.split('|')[-1].split()[3]
            if logserver_syslog == "":
                #print db_cef_time + '!=' + server_cef_time
                raise AssertionError("CEF + %s syslog error!" % log_protocol)
            #print db_cef_time + '?=' + server_cef_time

        elif log_tpye == 'LEEF':
            if logserver_syslog.find('LEEF') == -1:
                print logserver_syslog
                raise AssertionError("Log type(LEEF) error!")
            #db_leef_time = db_syslog.split('\n')[-1].split('|')[2].split()[1]
            #server_leef_time = logserver_syslog.split('\t')[2].split()[-2]
            if logserver_syslog == "":
                #print db_leef_time + '!=' + server_leef_time
                raise AssertionError("LEEF + %s syslog error!" % log_protocol)
            #print db_leef_time + '?=' + server_leef_time

        elif log_tpye == 'TMEF':
            #Reserved to be modified
            if logserver_syslog.find('CEF') == -1:
                print logserver_syslog
                raise AssertionError("Log type(TMEF) error!")
            #db_tmef_time = db_syslog.split('\n')[-1].split('|')[2].split()[1]
            #server_lmef_time = logserver_syslog.split('|')[-1].split()[3]
            if logserver_syslog == "":
                #print db_tmef_time + '!=' + server_lmef_time
                raise AssertionError("LEEF + %s syslog error!" % log_protocol)
            #print db_tmef_time + '?=' + server_lmef_time

        else:
            raise AssertionError("Log_tpye input wrong!")


    def start_syslog_process(self, syslog_conf):
        """ Check db log that email is analyzed
        @Param:
            num=1
        Return:
            None
        Example:
        | Start Syslog Process (syslog_server1_CEF_System.conf) |

        """
        print "Start syslog process..."
        self.is_ok('conf')
        #cmd = 'sudo python /opt/trend/ddei/script/syslog.py /opt/trend/ddei/config/%s > /dev/null 2>&1 &' %(syslog_conf)
        cmd = 'cd /opt/trend/ddei/script/; ./S99SYSLOG restart'
        ret=self.ssh_conn.execute_command(cmd)
        self.is_ok('process')
        print "Start syslog process success."

    def insert_data_into_db(self, table_name, data_file):
        """ Check db log that email is analyzed
        @Param:
            table_name, data_file
        Return:
            None
        Example:
        | insert_data_into_db('tb_policy_event', 'syslog_data') |

        """
        print "Start insert data into db..."
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "\\copy %s from \'%s\' delimiter\',\' csv header;"' % (table_name, data_file)
        self.ssh_conn.execute_command(cmd)
        self.is_ok('data', table_name)
        print "Finished insert data into db."


    def clean_ddei_syslog_env(self, syslog_conf):
        """ Clean ddei syslog environment
        @Param:
            path
        Return:
            None
        Example:
        | clean_syslog_env (syslog_server1.conf)|
        """
        print "Start clean ddei syslog env..."
        
        """stop process"""
        cmd  = 'rm -f /opt/trend/ddei/bin/syslog_server*.pid'
        self.ssh_conn.execute_command(cmd)
        cmd = 'tmp=`ps -ef|grep syslog.py|grep python|awk -F" " \'{print $2}\'`; kill -9 `pidof python /opt/trend/ddei/script/syslog.py /opt/trend/ddei/config/%s`' % (syslog_conf)
        self.ssh_conn.execute_command(cmd)

        """stop db_maintain"""
        cmd = '/bin/sh /opt/trend/ddei/script/db_maintain.sh stop'
        self.ssh_conn.execute_command(cmd)

        """delete data /root/tb_syslog_data.csv """
        cmd = 'rm -f /root/*.csv'
        self.ssh_conn.execute_command(cmd)

        """delete syslog conf"""
        cmd = 'rm -f /opt/trend/ddei/config/syslog_server1*'
        self.ssh_conn.execute_command(cmd)

        """delete bookmark"""
        cmd = 'rm -f /opt/trend/ddei/bin/syslog_server*_bookmark'
        self.ssh_conn.execute_command(cmd)

        """delete syslog debug log"""
        cmd = 'rm -f /opt/trend/ddei/log/syslog_server*.log'
        self.ssh_conn.execute_command(cmd)

        time.sleep(1)
        """delete data from db"""
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "delete from tb_system_event;"'
        self.ssh_conn.execute_command(cmd)
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "delete from tb_policy_event;"'
        self.ssh_conn.execute_command(cmd)
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "delete from tb_object_file;"'
        self.ssh_conn.execute_command(cmd)
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "delete from tb_object_url;"'
        self.ssh_conn.execute_command(cmd)
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "delete from tb_alert_triger_event;"'
        self.ssh_conn.execute_command(cmd)
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "delete from tb_fox_event;"'
        self.ssh_conn.execute_command(cmd)
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "delete from tb_msg_tracing;"'
        self.ssh_conn.execute_command(cmd)
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "delete from tb_msgtracing_update_event;"'
        self.ssh_conn.execute_command(cmd)

        print "Finished clean ddei syslog env."


    def clean_syslog_server_env(self):
        """ Clean syslog server environment
        @Param:
            path
        Return:
            None
        Example:
        | clean_syslog_server_env |

        """
        print "Start clean syslog server env..."
        #cmd  = '> /var/log/syslog_via_udp.log'
        cmd = '> /var/log/syslog_via_udp.log'
        self.ssh_conn.execute_command(cmd)
        cmd = '> /var/log/syslog_via_tcp.log'
        self.ssh_conn.execute_command(cmd)
        cmd = '> /var/log/syslog_via_ssl.log'
        self.ssh_conn.execute_command(cmd)
        time.sleep(2)
        #cmd = 'service syslog-ng restart'
        #self.ssh_conn.execute_command(cmd)
        self.is_ok('syslog_server_process')
        print "Finished clean syslog server env."


    def connect_to_syslog_server(self, host, prompt = '#'):
        """ Perform connection to syslog server
        @Param:
            host:   ip of syslog server
            prompt: default is '#'
        Return:
            If no error occur, it will return connection ID
        Example:
        | Connect To Syslog Server | 10.64.80.234 | |

        """
        self.conn_id = self.ssh_conn.open_connection(host, prompt)
        time.sleep(2)
        print "Connection id: ", self.conn_id 
        return self.conn_id


    def login_syslog_server(self, usr = 'root', pwd = '111111'):
        """ Login syslog server via ssh connection
        @Param:
            usr:    syslog server user name, default value is root
            pwd:    password of the user, default value is 111111
        Return:
            If no error occur, login information will be returned
        Example:
        | Login syslog server | root | 111111 |
        | Login syslog server |

        """
        if not self.conn_id:
            raise AssertionError('Connection is not establised yet!')
        else:
            ## Set user name and password as case specified
            conf.SSH_USR = usr
            conf.SSH_PWD = pwd
            rc = self.ssh_conn.login(usr, pwd)
            #time.sleep(2)
            test_log = 'Login syslog server as [%s]\n' % usr + rc
            return rc


    def disconnect_from_syslog_server(self):
        """ Disconnect from syslog server, if connection is not establised, it will do nothing
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


    def delete_bookmark(self, path, num):
        """ Check db log that email is analyzed
        @Param:
            path, num
        Return:
            None
        Example:
        | delete_bookmark('/opt/trend/ddi/bin', 1) |

        """
        cmd = 'rm -f %s/syslog_server%s_bookmark' % (path, num)
        ret = self.ssh_conn.execute_command(cmd)


    def check_syslog_header(self, path, file, logTag, field, expect_ret):
        """ Check db log that email is analyzed
        @Param:
            path, file
        Return:
            None
        Example:
        | check_syslog_header('/opt/trend/ddi/bin', 'syslog_via_udp.log') |

        """
        print "Start check syslog header fields..."
        print "Parameters: path=%s, file=%s, logTag=%s, field=%s, expect_ret=%s" % (path, file, logTag, field, expect_ret)

        self.is_ok('syslogs')
        if (field == 'logVer'):
            cmd = 'sed -n \'/%s/\'p %s/%s | awk -F"|" \'{print $1}\' | awk -F" " \'{print $5}\'' % (logTag, path, file)
        elif (field == 'vendor'):
            cmd = 'sed -n \'/%s/\'p %s/%s | awk -F"|" \'{print $2}\' ' % (logTag, path, file)
        elif (field =='pname'):
            cmd = 'sed -n \'/%s/\'p %s/%s | awk -F"|" \'{print $3}\' ' % (logTag, path, file)
        elif (field == 'pver'):
            cmd = 'sed -n \'/%s/\'p %s/%s | awk -F"|" \'{print $4}\' ' % (logTag, path, file)
        elif (field =='eventId'):
            cmd = 'sed -n \'/%s/\'p %s/%s | awk -F"|" \'{print $5}\' ' % (logTag, path, file)
        elif (field == 'eventName'):
            cmd = 'sed -n \'/%s/\'p %s/%s | awk -F"|" \'{print $6}\' ' % (logTag, path, file)
        elif (field =='severity'):
            cmd = 'sed -n \'/%s/\'p %s/%s | awk -F"|" \'{print $7}\' ' % (logTag, path, file)

        print 'Get field cmd: %s' % cmd
        ret = self.ssh_conn.execute_command(cmd)
        if (not ret.strip()):
            print 'Log header field: ', ret
            raise AssertionError('Log header parse not right on syslog server.')

        if (ret != expect_ret):
            print 'Log header field: ', ret
            raise AssertionError('Log header field not excepted.')

        print "Finished check syslog header fields: ", field


    def check_syslog_extention(self, path, file, logTag, field, expect_ret, status=0):
        """ Check db log that email is analyzed
        @Param:
            path, file
        Return:
            None
        Example:
        | check_logs_on_syslog_server('/opt/trend/ddi/bin', 'syslog_via_udp.log') |

        """
        print "Start check syslog extention fields..."
        print "Parameters : path=%s, file=%s, logTag=%s, field=%s, expect_ret=%s" %(path, file, logTag, field, expect_ret)
		
        self.is_ok('syslogs')	
        cmd = 'str=`sed -n \'/%s/\'p %s/%s`;str1=`echo ${str#*%s}`;str2=`echo ${str1%%%%=*}`; echo ${str2%% *}' % (logTag, path, file, field)
        ret = self.ssh_conn.execute_command(cmd)
        if (ret.lower() != expect_ret.lower()):
            print 'System log extention field: ', ret
            raise AssertionError('syslog extention field not excepted.')

        print "Finished check syslog extention fields: ", field

    def get_ddei_product_version(self):
        """ get ddei product version

        @Param:
            none
        Return:
            none
        Example:
            get_ddei_product_version
        """
        # get ddei product version
        cmd = 'str=`rpm -q ddei-core`; str1=`echo ${str%.*}`; echo $str1 | awk -F"-" \'{print $3}\''
        pre = self.ssh_conn.execute_command(cmd)
        cmd = 'str=`rpm -q ddei-core`; str1=`echo ${str%.*}`; echo $str1 | awk -F"-" \'{print $4}\''
        post = self.ssh_conn.execute_command(cmd)
        print "product pre: %s , post: %s" %(pre, post)
        ddei_product_version = pre + '.' + post
        print "DDEI product version: %s " % (ddei_product_version)
        return ddei_product_version

    def get_ddei_host_name(self):
        """ get ddei host name

        @Param:
            none
        Return:
            none
        Example:
            get_ddei_host_name
        """
        # get ddei product hostname
        cmd = 'hostname'
        ddei_host_name = self.ssh_conn.execute_command(cmd)
        print "DDEI product hosname: %s " % (ddei_host_name)
        return ddei_host_name

    def get_ddei_mac_address(self):
        """ get ddei mac address

        @Param:
            none
        Return:
            none
        Example:
            get_ddei_mac_address
        """
		
        # get ddei product MAC address
        cmd = 'sed -n /HWADDR/p /etc/sysconfig/network-scripts/ifcfg-eth0 | awk -F"=" \'{print $2}\''
        ddei_mac_address = self.ssh_conn.execute_command(cmd)
        print "DDEI product MAC address: %s " % (ddei_mac_address)
        return ddei_mac_address

    def get_ddei_product_guid(self):
        """ get ddei product guid

        @Param:
            none
        Return:
            none
        Example:
            get_ddei_product_guid
        """

        # get ddei prodcut GUID
        cmd = 'sed -n /guid/p /opt/trend/ddei/config/tmfbed_guid.conf | awk -F"\\"" \'{print $2}\''
        ddei_guid = self.ssh_conn.execute_command(cmd)
        print "DDEI product GUID: %s " % (ddei_guid)
        return ddei_guid

    def is_ok(self, part, table_name='tb_policy_event'):
        """ check the status for next step

        @Param:
            part
        Return:
            none
        Example:
            is_ok('process')
        """

        if(part=='conf'):
            for i in range(1,5):
                cmd = 'ls /opt/trend/ddei/config | grep syslog_server1_'
                ret = self.ssh_conn.execute_command(cmd)
                print "[Conf check] The results of remote cmd: %s" % ret.strip()
                if(ret.strip()):
                    print "The syslog conf uploaded success, conf file: [%s]." % ret.strip()
                    print "Change syslog config file name..."
                    cmd = 'cd /opt/trend/ddei/config; mv syslog_server1_* syslog_server1.conf; chmod 744 syslog_server1.conf; chown ddei:ddei syslog_server1.conf'
                    ret = self.ssh_conn.execute_command(cmd)
                    print "Finished changeing syslog config file name"
                    return
                time.sleep(1)
            raise AssertionError('Syslog conf uploaded fail.')
        elif(part=='process'):
            for i in range(1,10):
                cmd = 'ls /opt/trend/ddei/bin/syslog_server1_bookmark'
                ret = self.ssh_conn.execute_command(cmd)
                print "[Process check] The results of remote cmd: %s exist." % ret.strip()
                if(ret.strip()):
                    print "The syslog process is running, syslog book mark: [%s]." % ret.strip()
                    return
                time.sleep(1)
            raise AssertionError('Syslog process was not running.')
        elif(part=='data'):
            for i in range(1,10):
                cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "select * from %s;" | sed -n /row/p ' % (table_name)
                ret = self.ssh_conn.execute_command(cmd)
                print "[Data check] The results of remote cmd: %s" % ret.strip()
                if(ret.strip() != '(0 rows)'):
                    print "The data inserted into DB success, DB data: %s." % ret.strip()
                    return
                time.sleep(1)
            raise AssertionError('Insert data fail, there has no data in DB.')
        elif(part=='syslogs'):
            for i in range(1,60):
                cmd = 'cat /var/log/syslog_via_*'
                ret = self.ssh_conn.execute_command(cmd)
                print "[Syslogs check] The results of remote cmd: %s" % ret.strip()
                if(ret.strip()):
                   print "The logs were uploaded to syslog server success, syslog file: [%s]." % ret.strip()
                   return
                time.sleep(1)
            raise AssertionError('Logs uploaded to syslog server fail.')
        elif(part=='syslog_server_process'):
            for i in range(1,5):
                cmd = 'pidof /usr/local/syslog-ng/sbin/syslog-ng'
                ret = self.ssh_conn.execute_command(cmd)
                print "[Syslogs server process check] The results of remote cmd: %s" % ret.strip()
                if(ret.strip()):
                   print "The syslog server process is running, pid: [%s]." % ret.strip()
                   return
                time.sleep(1)
            raise AssertionError('Logs syslog server process is not running.')






