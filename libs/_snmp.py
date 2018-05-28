__author__ = 'anne_zhao'

from _baselib import KeywordBase
import time
import os
import conf

class SnmpKeywords(KeywordBase):
    """
    This library contain all related keywords about snmp function
    """

    def restart_snmp_process(self, snmp_conf, snmpd_conf):
        """ Star SNMP process
        @Param:
            num=2
        Return:
            None
        Example:
        | Start snmp Process (snmp_settings.conf, snmpd.conf) |

        """
        print "Start snmp process..."
        self.snmp_is_ok('conf')
        cmd = '/opt/trend/ddei/script/S99SNMPTRAP restart'
        self.exec_command_on_DDEI(cmd)

        cmd = 'service snmpd restart'
        self.exec_command_on_DDEI(cmd)

        self.snmp_is_ok('process')
        print "Start snmp process success."

    def insert_snmp_data_into_db(self, table_name, data_file):
        """ Check db log that email is analyzed
        @Param:
            table_name, data_file
        Return:
            None
        Example:
        | insert_data_into_db('tb_policy_event', 'snmp_data') |
        """
        print "Start insert data into db..."
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "delete from %s where id=1;' % (table_name)
        self.exec_command_on_DDEI(cmd)

        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "\\copy %s from \'%s\' delimiter\',\' csv header;"' % (table_name, data_file)
        self.exec_command_on_DDEI(cmd)

        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "update %s set id=((select max(id) from %s) +1) where id=1;"' % (table_name, table_name)
        self.exec_command_on_DDEI(cmd)

        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "update %s set date=\'now()\' where id=(select max(id) from %s);"' % (table_name, table_name)
        self.exec_command_on_DDEI(cmd)

        self.snmp_is_ok('data', table_name)
        print "Finished insert data into db."

    def restore_ddei_snmp_env(self, local_conf1, remote_conf1, local_conf2, remote_conf2):
        """ Restore ddei snmp environment
        @Param:
            path
        Return:
            None
        Example:
        | restore_ddei_snmp_process (snmp_settings.conf, snmpd.conf)|
        """
        print "Start clean ddei snmp env..."

        """stop db_maintain"""
        cmd = '/bin/sh /opt/trend/ddei/script/db_maintain.sh stop'
        self.exec_command_on_DDEI(cmd)

        """stop snmp process"""
        cmd = 'tmp=`ps -ef|grep snmp | sed -n \'/python/\'p | awk -F\' \' \'{print $2}\'`; kill -9 $tmp'
        self.exec_command_on_DDEI(cmd)

        """delete data /root/tb_snmp_data.csv """
        cmd = 'rm -f /root/*.csv'
        self.exec_command_on_DDEI(cmd)
      
        """delete snmp alert data in DB"""
        cmd = 'psql ddei sa -c "delete from tb_alert_triger_event ;"'
        self.exec_command_on_DDEI(cmd)

        """upload default snmp conf"""
        self.upload_file_to_DDEI(local_conf1, remote_conf1)
        self.upload_file_to_DDEI(local_conf2, remote_conf2)

        """delete snmp debug log"""
        cmd = 'echo > /opt/trend/ddei/log/snmp_trap.log'
        self.exec_command_on_DDEI(cmd)

        """restart snmp process"""
        self.restart_snmp_process(remote_conf1, remote_conf2)

        time.sleep(1)

        print "Finished restore ddei snmp env."

    def connect_to_snmp_server(self, host, prompt = '#'):
        """ Perform connection to snmp server
        @Param:
            host:   ip of snmp server
            prompt: default is '#'
        Return:
            If no error occur, it will return connection ID
        Example:
        | Connect To snmp Server | 10.64.80.234 | |

        """
        self.conn_id = self.ssh_conn.open_connection(host, prompt)
        time.sleep(2)
        print "Connection id: ", self.conn_id 
        return self.conn_id

    def login_snmp_server(self, usr = 'root', pwd = '111111'):
        """ Login snmp server via ssh connection
        @Param:
            usr:    snmp server user name, default value is root
            pwd:    password of the user, default value is 111111
        Return:
            If no error occur, login information will be returned
        Example:
        | Login snmp server | root | 111111 |
        | Login snmp server |

        """
        if not self.conn_id:
            raise AssertionError('Connection is not establised yet!')
        else:
            ## Set user name and password as case specified
            conf.SSH_USR = usr
            conf.SSH_PWD = pwd
            rc = self.ssh_conn.login(usr, pwd)
            #time.sleep(2)
            test_log = 'Login snmp server as [%s]\n' % usr + rc
            return rc

    def disconnect_from_snmp_server(self):
        """ Disconnect from snmp server, if connection is not establised, it will do nothing
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

    def get_snmp_expect_result(self, file='/proc/meminfo', part='SwapTotal'):
        """ get snmp expect results
        @Param:
            part
        Return:
            info
        Example:
        | get_snmp_expect_result('SwapTotal') 

        """
        print "Start get snmp expect resutls..."
        print "Parameters: part=%s" % (part)

        """ Get the expect result """
        cmd='cat %s |grep %s | awk -F" " \'{print $2}\' | sed -n 1p;' % (file, part)
        ret=self.exec_command_on_DDEI(cmd)
        if (not ret.strip()):
            print 'SNMP expect result: %s ' % ret
            raise AssertionError('Get snmp expect result error.')

        print "Finished get snmp expect result: ", ret
        return ret

    def get_snmp_query_result(self, snmp_version, community_name, agent_ip, mib_oid, type='0',snmp_mode='authPriv',user_name='ddei',passwd='11111111', snmp_passphrase='22222222'):
        """ get snmp query results
        @Param:
            path, file
        Return:
            value
        Example:
        | check_snmp_query_result('2c','public','10.204.253.164', 'SwapTotal', '.1.3.6.1.4.1.2021.4.3.0','INTEGER: 2097148 kB') 

        """
        print "Start get snmp query resutls..."
        print "Parameters: snmp_version=%s, community_name=%s, agent_ip=%s, mib_oid=%s, type=%s" % (snmp_version, community_name, agent_ip, mib_oid, type)

        """ snmpget the info """
        if (snmp_version == '3'):
            cmd_prefix = "snmpwalk -r 0 -v 3 -u %s -n "" -l %s -a MD5 -A %s -x DES -X %s %s %s" % (user_name, snmp_mode, passwd, snmp_passphrase,agent_ip, mib_oid)
        else:
            cmd_prefix = "snmpwalk -v %s -c %s %s %s" % (snmp_version, community_name, agent_ip, mib_oid)
        if (type == '1'):
            cmd="%s | awk -F\"\\\"\" '{print $2}'" % (cmd_prefix)
        else:
            cmd="%s | awk -F\" \" '{print $4}'" % (cmd_prefix)
        ret=self.exec_command_on_DDEI(cmd)
        print 'SNMP Query result: %s' % ret
        """
        if (not ret):
            print 'SNMP query result: %s ' % ret
            raise AssertionError('Get snmp query result error.')
        """
        
        print "Finished get snmp query result: ", ret
        return ret

    def get_ddei_product_info(self, part):
        """ get ddei product version

        @Param:
            none
        Return:
            none
        Example:
            get_ddei_product_version
        """
        # get ddei product version
        """
        cmd = 'str=`rpm -q ddei-core`; str1=`echo ${str%.*}`; echo $str1 | awk -F"-" \'{print $3}\''
        pre = self.exec_command_on_DDEI(cmd)
        cmd = 'str=`rpm -q ddei-core`; str1=`echo ${str%.*}`; echo $str1 | awk -F"-" \'{print $4}\''
        post = self.exec_command_on_DDEI(cmd)
        print "product pre: %s , post: %s" %(pre, post)
        ddei_product_version = pre + '.' + post
        """

        cmd = 'env | grep %s | awk -F"=" \'{print $2}\'' % part
        product_info = self.exec_command_on_DDEI(cmd)
        print "DDEI product info: %s = %s " % (part, product_info)
        return product_info


    def get_ddei_component_info(self, component_name):
        """ get ddei component info

        @Param:
            none
        Return:
            ddei_guid
        Example:
            get_ddei_component_info
        """

        # get ddei component info
        cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "select * from tb_global_setting;" |grep %s|awk -F"|" \'{print $3}\'' % component_name
        ret = self.exec_command_on_DDEI(cmd)
        print "DDEI component version: %s = %s " % (component_name, ret)
        return ret

    def snmp_is_ok(self, part, table_name='tb_alert_trigger_event'):
        """ check the status for next step

        @Param:
            part
        Return:
            none
        Example:
            snmp_is_ok('process')
        """
        print "Input parameters: part = %s, table_name = %s" % (part, table_name)
        if(part=='conf'):
            for i in range(1,5):
                cmd = 'ls /opt/trend/ddei/config | grep snmp_settings.conf'
                ret = self.exec_command_on_DDEI(cmd)

                print "[Conf check] The results of cmd: %s" % ret.strip()
                if(ret.strip()):
                    print "DDEI snmp conf uploaded success, conf file: [%s]." % ret.strip()
                    return
                cmd = 'ls /etc/snmp | grep snmpd.conf'
                ret = self.exec_command_on_DDEI(cmd)
                print "[Conf check] The results of cmd: %s" % ret.strip()
                if(ret.strip()):
                    print "SNMPd conf uploaded success, conf file: [%s]." % ret.strip()
                    return
                time.sleep(1)
            raise AssertionError('snmp conf uploaded fail.')
        elif(part=='process'):
            for i in range(1,10):
                cmd = 'pidof /usr/sbin/snmpd'
                ret = self.exec_command_on_DDEI(cmd)
                print "[Process check] Process: %s." % ret.strip()
                if(not ret.strip()):
                    print "[Process check] Process: %s not exist." % ret.strip()
                    return
                cmd = 'ps -ef|grep snmp_trap | sed -n \'/script/p\''
                ret = self.exec_command_on_DDEI(cmd)
                print "[Process check] Process: %s." % ret.strip()
                if(ret.strip()):
                    print "[Process check] Process: %s exist." % ret.strip()
                    return
                time.sleep(1)
            raise AssertionError('snmp processes were not running.')
        elif(part=='data'):
            for i in range(1,10):
                cmd = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -c "select * from %s;" | sed -n /row/p ' % (table_name)
                ret = self.exec_command_on_DDEI(cmd)
                print "[Data check] The results of remote cmd: %s" % ret.strip()
                if(ret.strip() != '(0 rows)'):
                    print "The data inserted into DB success, DB data: %s." % ret.strip()
                    return
                time.sleep(1)
            raise AssertionError('Insert data fail, there has no data in DB.')
        elif(part=='snmp'):
            for i in range(1,60):
                cmd = 'cat /var/log/snmp_*'
                ret = self.exec_command_on_DDEI(cmd)
                print "[snmp check] The results of remote cmd: %s" % ret.strip()
                if(ret.strip()):
                   print "The logs were uploaded to snmp server success, snmp file: [%s]." % ret.strip()
                   return
                time.sleep(1)
            raise AssertionError('Logs uploaded to snmp server fail.')
        elif(part=='snmp_server_process'):
            for i in range(1,5):
                cmd = 'pidof /usr/sbin/snmpd'
                ret = self.exec_command_on_DDEI(cmd)
                print "[snmp server process check] The results of remote cmd: %s" % ret.strip()
                if(ret.strip()):
                   print "The snmp server process is running, pid: [%s]." % ret.strip()
                   return
                time.sleep(1)
            raise AssertionError('Logs snmp server process is not running.')

    def get_ddei_mem_swap_total(self):
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
        ddei_guid = self.exec_command_on_DDEI(cmd)
        print "DDEI product GUID: %s " % (ddei_guid)
        return ddei_guid

    def start_dump_snmp_trap(self, ip):
        """ 
        @Param:
            path, file
        Return:
            None
        Example:
        | prepare_dump_snmp_trap('10.204.253.131') |

        """
        print "Start prepare dump snmp trap..."
        print "Parameters : ip=%s" %(ip)

        cmd = 'pkill tcpdump; pidof tcpdump'
        ret = self.exec_command_on_DDEI(cmd)
        if (ret != ''):
            print "kill tcpdump fail..."
            raise AssertionError('Prepare snmp server env fail: kill old tcpdump process error.')

        cmd = 'nohup /root/traptest/test.sh %s > /dev/null 2>&1 &' % (ip)
        self.exec_command_on_DDEI(cmd)

        time.sleep(1)
        cmd = 'pidof tcpdump'
        ret = self.exec_command_on_DDEI(cmd)
        print "tcpdump pid: %s" %(ret)
        if (ret == ''):
            print "Start a new tcpdump fail..."
            raise AssertionError('Prepare snmp server env fail: start tcpdump error.')

        print "Finished prapare dump snmp trap."


    def stop_dump_snmp_trap(self, ip):
        """ 
        @Param:
            path, file
        Return:
            None
        Example:
        | stop_dump_snmp_trap('10.204.253.131') |

        """
        print "Start stop dump snmp trap..."
        print "Parameters : ip=%s" %(ip)

        cmd = 'pkill tcpdump; pidof tcpdump'
        ret = self.exec_command_on_DDEI(cmd)
        if (ret != ''):
            print "kill tcpdump fail..., kill again"
            time.sleep (2)
            cmd = 'pkill tcpdump; pidof tcpdump'
            ret = self.exec_command_on_DDEI(cmd)
            if (ret != ''):
                print "kill tcpdump again fail..."
                raise AssertionError('Prepare snmp server env fail: kill old tcpdump process error.')
        print "Finished prapare dump snmp trap."


    def check_snmp_trap_msg(self, path, file, logTag, field, expect_ret, status=0):
        """ Check db log that email is analyzed
        @Param:
            path, file
        Return:
            None
        Example:
        | check_snmp_trap_msg('/opt/trend/ddi/bin', 'snmp_via_udp.log') |

        """
        print "Start check snmp trap message on snmp server..."
        print "Parameters : path=%s, file=%s, logTag=%s, field=%s, expect_ret=%s" %(path, file, logTag, field, expect_ret)

        cmd='pkill tcpdump'
        self.exec_command_on_DDEI(cmd)
        cmd = 'pidof tcpdump'
        ret = self.exec_command_on_DDEI(cmd)
        if (ret != ''):
            print 'Process tcpdump was still running on SNMP server.'
            raise AssertionError('SNMP server tcpdump error')

        cmd = 'str=`sed -n \'/%s/\'p %s/%s`;str1=`echo ${str#*%s}`;str2=`echo ${str1%%%%=*}`; echo ${str2%% *}' % (logTag, path, file, field)
        ret = self.exec_command_on_DDEI(cmd)
        if (ret != expect_ret):
            print 'System log extention field: ', ret
            raise AssertionError('System log extention field not excepted.')

        print "Finished check system log extention fields: ", field

    def get_snmp_trap_result(self, snmp_trap_result):
        """ get snmp query results
        @Param:
            path, file
        Return:
            value
        Example:
        | check_snmp_query_result('2c','public','10.204.253.164', 'SwapTotal', '.1.3.6.1.4.1.2021.4.3.0','INTEGER: 2097148 kB') 

        """
        print "Start get snmp trap resutls..."
        print "Parameters: snmp_trap_result=%s" % (snmp_trap_result)

        """ kill tcpdump """
        cmd = 'pkill tcpdump'
        self.exec_command_on_DDEI(cmd)

        """ snmptrap info """
        cmd = 'cat %s' % (snmp_trap_result)
        ret=self.exec_command_on_DDEI(cmd)
        if (ret == ''):
            print 'SNMP trap result is null'
            raise AssertionError('Snmp trap msg was not sent to snmp server.')
                
        print "Finished get snmp trap result: %s" % ret
        return ret


    def check_snmp_trap_sent_out(self, log_file, key):
        """ get snmp query results
        @Param:
            path, file
        Return:
            value
        Example:
        | check_snmp_trap_sent_out('snmp_trap.log','CPU') 
        """

        print "Start check snmp trap msg sent out..."
        print "Parameters:  log_file=%s, key=%s" % (log_file, key)

        x =  0
        ret = ''
        while x <60:
            cmd = 'cat %s | grep  %s' % (log_file, key)
            ret=self.exec_command_on_DDEI(cmd)
            if (ret != ''):
                print 'SNMP trap msg already sent out. '
                break
            time.sleep(1)
            x += 1
    
        if (ret == ''):
            print "Finished check snmp trap msg sent"        
            raise AssertionError('Snmp trap msg was not sent out.')
        print "Finished check snmp trap msg sent"




