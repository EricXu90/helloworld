from ftplib import FTP, error_perm
import time
import subprocess
import os
import sys
import shutil
import SSHLibrary
import logging
import ParseCaseResult
# from pit_test import PITTest
import smtplib
from email.mime.text import MIMEText
import re
from subprocess import Popen, PIPE
import json
from libs import conf,suite_list
from libs.logger import loginfo,logwarning,logerror,init

#initial log module
init()

#==========================================================
# Modify setting here
#==========================================================
AUTO_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(os.path.dirname(AUTO_ROOT), 'usbx')
GM_BUILD_FOLDER = os.path.join(AUTO_ROOT, 'GM_BUILD')
LOCAL_TOOLS_FOLDER = os.path.join(AUTO_ROOT, 'tools')
AUTO_LOG_FILE = "BVT.log"

MONITOR_INTERVAL = 0.5*60
RETRY_INTERVAL = MONITOR_INTERVAL

GM_BUILD = "1223"
IGNOR_INSTALL = False
IGNOR_BVT = False

IP=re.search('\d+\.\d+\.\d+\.\d+',Popen('ipconfig', stdout=PIPE).stdout.read()).group(0)
BVT_RUNNING_CASE_TAG = ['BVT_IPv6_SP2','BVT', 'BVT_SP1', 'BVT_UI_SP1', 'BVT_SP2', 'BVT_UI_SP2', 'BVT_2.1', 'BVT_UI_2.1', 'BVT_2.5']

BVT_BUILD = {
    "en": {
        "test_ver": "1119",
        "path": "build/DDEI-US/3.1/centos7x64/en/int/"
    }
}

# make ssh connection fast
CMD_Config_SSHD = "sed -i -e '/UseDNS/d' -e '/GSSAPIAuthentication/d' /etc/ssh/sshd_config; echo 'UseDNS no' >> /etc/ssh/sshd_config; echo 'GSSAPIAuthentication no' >> /etc/ssh/sshd_config; service sshd restart"
SQL_Enable_ATSE_Aggresive_Mode = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -t -c "%s"' % "UPDATE tb_global_setting set value=4 where name='VSIDetectMode'"
SQL_Disable_SO_Detection = '/opt/trend/ddei/PostgreSQL/bin/psql ddei sa -t -c "%s"' % "update tb_global_setting set value =0 where section = 'so_detection' and name = 'so_detection_enable'"



class DDEITest:
    def __init__(self):
        self.ssh_conn = SSHLibrary.SSHLibrary()
        self.ssh_conn.open_connection(conf.DDEI_IP, '#')
        self.ssh_conn.login(conf.SSH_USR, conf.SSH_PWD)
        self.usbx_image = ""

    def make_connetion(self):
        """ Init SSH connection to DDEI

        """
        self.ssh_conn = SSHLibrary.SSHLibrary()
        self.ssh_conn.open_connection(conf.DDEI_IP, '#')
        self.ssh_conn.login(conf.SSH_USR, conf.SSH_PWD)

    def exec_command(self, cmd):
        """ Execute remote command and return the result

        """
        try:
            result = self.ssh_conn.execute_command(cmd).strip()
        except:
            self.ssh_conn.open_connection(conf.DDEI_IP, '#')
            self.ssh_conn.login(conf.SSH_USR, conf.SSH_PWD)
            result = self.ssh_conn.execute_command(cmd).strip()
        return result

    def reboot_and_wait_ddei(self):
        """ Reboot DDEI and wait for its completion

        """
        write_cmd = 'echo "sleep 2;ifconfig eth0 down;reboot" > reboot.sh'
        reboot_cmd = 'nohup sh reboot.sh > /dev/null 2>&1 &'

        loginfo('Rebooting DDEI...')
        #enable ssh and disable token
        loginfo('Begin to enable ssh and remove ssh token...')
        self.exec_command("systemctl enable sshd")
        self.download_script_to_disable_token()
        loginfo('Finish to enable ssh and remove ssh token...')
        self.exec_command(CMD_Config_SSHD)
        self.exec_command(write_cmd)
        self.exec_command(reboot_cmd)
        self.ssh_conn.close_connection()
        time.sleep(6)

        loginfo('Waiting DDEI starting...')
        ping_cmd = 'ping %s -n 1' % conf.DDEI_IP
        while True:
            time.sleep(5)
            print '.',
            process = subprocess.Popen(ping_cmd, shell=True, stdout=subprocess.PIPE)
            test_result = process.stdout.read()
            if test_result.find('Packets: Sent = 1, Received = 1, Lost = 0 (0% loss)') != -1:
                print ''
                break
        loginfo('DDEI is running again')

    def clean_environment(self):
        """ Clean u-sandbox and uninstall old DDEI

        """
        loginfo('Stop U-Sandbox Function...')
        self.exec_command(conf.CMD_USBX_STOP)

        loginfo('Delete All Existing U-Sandbox Group...')
        self.exec_command(conf.CMD_USBX_DEL_ALL_GROUP)

        loginfo('Begin to uninstall Old DDEI')
        self.exec_command(conf.CMD_DDEI_UNINSTALL)

        uninstall_confirm_cmd="rpm -qa|grep ddei"
        if "ddei" in self.exec_command(uninstall_confirm_cmd):
            self.exec_command("rpm -e ddei-core; rpm -e ddei-system")
            self.exec_command("rpm -e clish_cmd")
            self.exec_command('rpm -e update-center')
            # self.exec_command('rpm -e at_library')
            # self.exec_command('rpm -e at_lock')
            # self.exec_command('rpm -e data_migration')
            # self.exec_command('rpm -e hashcat')
            # self.exec_command('rpm -e health_monitor')
            # self.exec_command('rpm -e hw-model-custom')           
            loginfo('uninstall all rpm again')
            
        if "ddei" in self.exec_command(uninstall_confirm_cmd):
            logerror('uninstall failed')
            sys.exit(0)
        else:
            loginfo('Finish Uninstall')
            time.sleep(60)      

    def get_install_package(self, build_num, is_pit = False, build_lan='en'):
        """ Get specific installation package

        """
        folder = '%s%s/output/RPMS' % (BVT_BUILD[build_lan]['path'], build_num)
        loginfo('Getting DDEI RPM packages path=%s' % folder)
        ftp_cmd = '''ftp -n %s << EOF
        user %s %s
        cd %s
        bin
        prompt off
        mget *
        bye
        EOF
        ''' % (conf.BUILD_FTP_SERVER,
               conf.BUILD_FTP_USER,
               conf.BUILD_FTP_PWD,
               folder)

        loginfo('Getting DDEI build (RPM packages)...')
        self.exec_command('rm -rf /root/*.rpm')
        if not is_pit:
            print self.exec_command(ftp_cmd)
        else:
            build_files = os.path.join(GM_BUILD_FOLDER, build_num, '*')
            self.ssh_conn.put_file(build_files, '/root/')
        time.sleep(30)
        loginfo('Getting DDEI build (RPM packages) successfully')

    #test upload uninstall.sh
    def upload_uninstall_script(self,uninstall_script='uninstall_ddei_app.sh'):
        loginfo('start uplod uninstall_ddei_app.sh')
        rc=self.exec_command('ls /opt/trend/ddei/installer/')
        if rc.find(uninstall_script)==-1:
            loginfo('uninstall_script not exist....')
        else:
            loginfo('delete uninstall_ddei_app.sh in 67')
            self.exec_command('rm -f /opt/trend/ddei/installer/uninstall_ddei_app.sh')
        self.ssh_conn.put_file(os.path.join(LOCAL_TOOLS_FOLDER, uninstall_script),"/opt/trend/ddei/installer/%s" %uninstall_script)
        self.exec_command('cd /opt/trend/ddei/installer/; chmod 755 uninstall_ddei_app.sh;chown ddei:ddei uninstall_ddei_app.sh')

    def download_script_to_disable_token(self, disable_token_script = 'disable-token.zip'):
        """ Upload disable token script file from local to DDEI and disable token

        """
        #at_config file
        loginfo('Starting upload at_config file ...')
        rc = self.exec_command('ls /usr/bin/')
        if rc.find('at_config') == -1:
            loginfo('at_config file not exist...')
            self.ssh_conn.put_file(os.path.join(LOCAL_TOOLS_FOLDER, 'at_config'), "/usr/bin/at_config")
        else:
            loginfo('at_config file alrealy exist')
            self.exec_command('cd /usr/bin/; chmod 755 at_config; chown root:root at_config')
        loginfo('End upload at_config file .')

        #time.sleep(5)
        self.exec_command("cd /usr/bin/; chmod 755 at_config;")

        # token
        loginfo('Starting disable token ...')
        rc = self.exec_command('ls /root/disable-token/')
        if rc.find('disable-token.sh') == -1:
            loginfo('Disable token script not exist...')
            rc = self.exec_command('ls /root/')
            if rc.find(disable_token_script) == -1:
                loginfo('Disable token zip not exist...')
                self.ssh_conn.put_file(os.path.join(LOCAL_TOOLS_FOLDER, disable_token_script), "/root/%s" % disable_token_script)
        else:
            loginfo('Disable token script alrealy exist')
        self.exec_command('unzip -o /root/' + disable_token_script)
        self.exec_command('cd /root/disable-token/; sh -x ./disable-token.sh')
        loginfo('End disable token.')

        #pwd file
        loginfo('Starting upload pwd file ...')
        rc = self.exec_command('ls /opt/trend/ddei/config/')
        if rc.find('os_credential.xml') == -1:
            loginfo('pwd file not exist...')
            self.ssh_conn.put_file(os.path.join(LOCAL_TOOLS_FOLDER, 'os_credential.xml'), "/root/os_credential.xml")
        else:
            loginfo('pwd file alrealy exist')
            self.exec_command('cp -f /root/os_credential.xml /opt/trend/ddei/config/; cd /opt/trend/ddei/config/; chmod 750 os_credential.xml; chown ddei:ddei os_credential.xml')
        loginfo('End upload pwd file .')

        # pub key
        loginfo('Starting upload pub key ...')
        rc = self.exec_command('ls -a /root/.ssh/')
        if rc.find('pam_ddei_es256.pub') == -1:
            loginfo('pub key not exist...')
            self.ssh_conn.put_file(os.path.join(LOCAL_TOOLS_FOLDER, 'pam_ddei_es256.pub'), "/root/.ssh/pam_ddei_es256.pub")
        else:
            loginfo('pub key alrealy exist')
            self.exec_command('cd /root/.ssh/; chmod 444 pam_ddei_es256.pub; chown root:root pam_ddei_es256.pub')
        loginfo('End upload pub key.')

    def install_ddei(self):
        """ Install DDEI and activate it

        """
        loginfo('Begin to Install RPM packages ...')
        self.exec_command("rm -f $(ls *.rpm | xargs -n 1 | grep -v 'ddei-core' | grep -v 'ddei-system' | grep -v clish | grep -v 'update-center')")
        self.exec_command(conf.CMD_DDEI_INSTALL_1)
        loginfo('Finish Installing RPMs')

        loginfo('Begin to create file [pg_log] ...')
        self.exec_command("mkdir -p /var/app_data/ddei/db; touch /var/app_data/ddei/db/pglog; chown -R ddei:ddei /var/app_data/ddei/db/pglog")
        loginfo('Finish to create file [pg_log] ...')

        loginfo('Begin to remove ssh key request and restart sshd ...')
        self.exec_command("sed -i -e '/Match User root/d' -e '/publickey/d' /etc/ssh/sshd_config; systemctl enable sshd")
        loginfo('Finish to remove ssh key request and restart sshd ...')

        loginfo('Begin to modify install shell prepare_for_first_boot.sh ...')
        self.exec_command("sed -i '82s/ !//' /opt/trend/ddei/installer/prepare_for_first_boot.sh")
        loginfo('Finish to modify install shell prepare_for_first_boot.sh ...')

        loginfo('Begin to Install DDEI ...')
        self.exec_command("sed -i '/pg_hba/ s:0/0:10.204.0.0/16:' /opt/trend/ddei/installer/installdb.sh; sed -i 's/password/trust/' /opt/trend/ddei/installer/installdb.sh")
        self.exec_command(conf.CMD_DDEI_INSTALL_2)
        time.sleep(120)
        #set msgtracing log level:debug
        loginfo('set msgtracing log level:debug')
        self.exec_command(r"sed -i -e '220,$s/ERROR/DEBUG/g' /opt/trend/ddei/config/MsgTracing.conf")
        loginfo('Begin to reboot DDEI ...')
        self.reboot_and_wait_ddei()
        time.sleep(600)
        loginfo('Finish Installing DDEI')
        self.make_connetion()

        loginfo('Deleting old DDEI RPM packages...')
        self.exec_command("rm -f *.rpm")

    def config_ddei(self):
        """ Prepare configuration for running BVT

        """
        # Active ATP license
        loginfo('Begin activate DDEI With ATP AC Code ...')
        self.exec_command(conf.CMD_ACTIVATE_ATP_PR)
        loginfo('Write AC code into accode_atd ')
        cmd = 'echo ' + conf.AC_CODE_GOLDEN + ' > /opt/trend/ddei/config/accode_atd'
        self.exec_command(cmd)
        cmd = 'chown ddei:ddei /opt/trend/ddei/config/accode_atd'
        self.exec_command(cmd)
        loginfo('Finish activate DDEI With ATP AC Code ...')

        #Active GM license
        loginfo('Begin activate DDEI with GM code...')
        self.exec_command(conf.CMD_ACTIVATE_GM_PR)
        loginfo('Write GM code into accode_seg')
        cmd='echo '+conf.AC_CODE_GOLDEN+' > /opt/trend/ddei/config/accode_seg'
        self.exec_command(cmd)
        cmd='chown ddei:ddei /opt/trend/ddei/config/accode_seg'
        self.exec_command(cmd)
        loginfo('Finish active DDEI with GM code...')

        loginfo('create link from /opt/trend/ddei/log to /var/app_data/ddei/log')
        self.exec_command("rm -rf /opt/trend/ddei/log;ln -s  /var/app_data/ddei/log /opt/trend/ddei/log")
        loginfo('finish create link')

        # Close all widgets for UI testing, because GeoMap widget need flash plugin which pop up window will affect UI automation
        widget_db = "/opt/trend/ddei/UI/adminUI/ROOT/dashboard/widget/repository/db/sqlite/tmwf.db"
        hide_geomap_widget = 'sqlite3 %s "update users set udata=%s, cdata=%s, pdata=%s"' % (widget_db, "'[]'", "'[]'", "'[]'")
        self.exec_command(hide_geomap_widget)
        loginfo('finished close all widgets.')

        add_custom_dns = "echo 'nameserver 10.204.253.237' > /etc/resolv.conf"
        self.exec_command(add_custom_dns)
        loginfo('finished add custom dns.')

        # config proxy 
        conf_file = "/opt/trend/ddei/config/imss.ini"
        enable_proxy = '%s "%s"' % (conf.PSQL_EXE,  "update tb_global_setting set value='yes' where section='Update' and name='UseProxySetting'")
        sql_set_proxy_ip = '%s "%s"' % (conf.PSQL_EXE, "update tb_global_setting set value='%s' where section='Update' and name='HTTPProxy'" % conf.LAB_PROXY_SERVER)
        sql_set_proxy_port = '%s "%s"' % (conf.PSQL_EXE,  "update tb_global_setting set value='%s' where section='Update' and name='HTTPPort'" % conf.LAB_PROXY_PORT)
        sql_set_proxy_type = '%s "%s"' % (conf.PSQL_EXE, "update tb_global_setting set value='%s' where section='Update' and name='ProxyType'" % conf.LAB_PROXY_TYPE)
        sql_set_au_status='%s "%s"' % (conf.PSQL_EXE,  "update tb_global_setting set value='no' where section='Update' and name='EnableUpdateSchedule'")
        self.exec_command(enable_proxy)
        self.exec_command(sql_set_proxy_ip)
        self.exec_command(sql_set_proxy_port)
        self.exec_command(sql_set_proxy_type)
        self.exec_command(sql_set_au_status)

        # enable ATSE to aggresive mode for 2.5 feature change
        self.exec_command(SQL_Enable_ATSE_Aggresive_Mode)
        self.exec_command(SQL_Disable_SO_Detection)
        loginfo('finished enable ATSE to aggresive mode.')
        # Change default debug level
        cmd = "sed -i -e '/#log_level=normal/d' -e '/\[general\]/a log_level=debug' %s" % conf_file
        self.ssh_conn.execute_command(cmd)

        #modify scanner process number
        cmd=r"sed -i -e 's/#proc_min_init_num = 30/proc_min_init_num = 5/g' /opt/trend/ddei/config/imss.ini"
        self.exec_command(cmd)
        self.ssh_conn.execute_command("/opt/trend/ddei/script/S99IMSS restart")
        loginfo('finished config proxy and change default debug level.')

    def is_all_process_start(self):
        """ Check whether all process have started

        """
        rc = self.exec_command('ps -ef')
        for ddei_process in conf.DDEI_MUST_PROCESS_LIST:
            if rc.find(ddei_process) == -1:
                logerror('Launching DDEI failed')
                return False
        return True

    def download_image_from_local(self, image_type = 'win7'):
        """ Upload image file from local to DDEI

        """
        if image_type == 'xp':
            self.usbx_image = conf.USBX_IMAGE_XP
        elif image_type == 'win7':
            self.usbx_image = conf.USBX_IMAGE_WIN7

        rc = self.exec_command('ls /var/app_data/')

        if rc.find(self.usbx_image) == -1:
            loginfo('Getting U-Sandbox OS image...')
            self.ssh_conn.put_file(os.path.join(IMAGE_FOLDER, self.usbx_image), "/var/app_data/%s" % self.usbx_image)
        else:
            loginfo('U-sandbox image alrealy exist')

    def import_image(self, image_type = 'win7'):
        """ Import U-sandbox image

        """
        while True:
            rc = self.exec_command(conf.CMD_USBX_GET_STATE)
            if rc.find('noimage') != -1:
                loginfo('Init U-Sandbox successfully')
                break
            print '.',
            time.sleep(5)
        loginfo('Finish to init U-sandbox')

        loginfo('Enable u-sandbox debug log')
        rc = self.exec_command(conf.CMD_USBX_ENABLE_DEBUG)
        loginfo('Importing OS image to U-Sandbox..')
        rc = self.exec_command(conf.CMD_USBX_IMPORT + ' --num 1 --name "%s" --type win --clonedtype link --imagepath %s'\
                                      % (image_type, '/var/app_data/' + self.usbx_image))
        if rc.find('id') == -1:
            logerror('Fail To Import Image')
            print rc
            return False

        while True:
            rc = self.exec_command(conf.CMD_USBX_GET_STATE)
            if rc.find('maintenance') != -1:
                loginfo('OS image to U-Sandbox successfully')
                break
            print '.',
            time.sleep(5)
        loginfo('Finish Importing OS image')

    def config_sandbox(self):
        """ Pre-config the u-sandbox

        """
        loginfo('Setting U-Sandbox gateway..')
        self.exec_command(conf.CMD_USBX_SET_GATEWAY + ' --type nat')
        time.sleep(5)
        rc = self.exec_command(conf.CMD_USBX_SET_GATEWAY)
        if rc.find('Type: nat') == -1:
            logerror('Fail To set U-sandbox to nat type')
        else:
            loginfo('Finish setting U-sandbox to nat type')

        #set U-sandbox proxy
        loginfo('Setting U-Sandbox proxy..')
        self.exec_command(conf.CMD_USBX_SET_PROXY + ' --switch ON --host 10.204.16.17 --port 8087 --proto http --user \'\' --passwd \'\'')
        time.sleep(5)
        rc = self.exec_command(conf.CMD_USBX_SET_PROXY)
        if rc.find('Host: 10.204.16.17') == -1:
            logerror('Fail To set proxy for U-sandbox')
        else:
            loginfo('Finish setting U-sandbox proxy')

    def start_sandbox(self):
        """ Start u-sandbox function

        """
        loginfo('Starting U-Sandbox...')
        rc = self.exec_command(conf.CMD_USBX_START)

        if rc.find('Error') != -1:
            logerror('Fail To Start u-sandbox')
            print rc
            return False

        while True:
            rc = self.exec_command(conf.CMD_USBX_GET_STATE)
            if rc.find('running') != -1:
                loginfo('Start U-Sandbox succcessfully')
                break
            print '.',
            time.sleep(5)
        loginfo('Finish Starting U-Sandbox')

        loginfo('Purge image file for release disk space')
        # self.exec_command("rm -f /var/app_data/%s" % self.usbx_image)

    def switch_to_internalVA(self):
        """ switch to u-sandbox function

        """
        loginfo('Begin to switch to interval VA...')
        self.exec_command('psql ddei sa -c "update tb_global_setting set value=0 where name =\'Mode\';"')
        self.exec_command('rm -rf /opt/trend/ddei/bin/dtasProduct.pid')
        loginfo('finished to modify global setting VA mode')
        self.exec_command('nohup /opt/trend/ddei/script/S99TASKMONITOR restart > /dev/null 2>&1 &')
        time.sleep(300)
        loginfo('finished to restart TASKMONITOR to start internal VA')
        loginfo('End to switch to interval VA...')
       
    def deploy_ddei_test_env(self, build_num, is_pit = False, build_lan='en'):
        """ Deploy DDEI test environment

        """

        self.change_system_time()
        self.upload_uninstall_script()

        #rpm install
        count = 0
        while (count < 5):
            loginfo('Get RPMs count = %s' % count)

            self.get_install_package(build_num, is_pit, build_lan)
            rc = self.exec_command('ls /root/')
            coreRPM= 'ddei-core-3.1.0-' + build_num + '.i686.rpm'
            systemRPM = 'ddei-system-3.1.0-' + build_num + '.i686.rpm' 
            loginfo('Get RPMs: %s, %s' % (coreRPM, systemRPM))
            if rc.find(coreRPM) != -1 and rc.find(systemRPM) != -1:
                self.clean_environment()
                self.install_ddei()

                #config: active, 
                self.make_connetion()
                self.config_ddei()
                self.ssh_conn.close_connection()

                #--------------------------
                #need to modify in future
                #--------------------------
                if IP==conf.IMPORT_IMAGE_WIN7_MACHINE:
                    self.download_image_from_local()
                    self.import_image()
                    self.config_sandbox()
                    self.start_sandbox()
                    self.switch_to_internalVA()
                else:
                    pass

                #backup ddei config
                loginfo('backup ddei config')
                self.exec_command('/opt/trend/ddei/script/imp_exp.sh ui -e /opt/ddei_test.dat')

                loginfo('deploy_ddei_test_env success.')
                break;
            
            loginfo('RPM packages not complete, ftp get again...')
            count = count + 1
        if count==5:
            logerror('deploy_ddei_test_env failed.....')

    # change system time
    def change_system_time(self):
        """ Change DDEI system time

        """
        loginfo('Change system time begin...')
        localtime = time.asctime(time.localtime(time.time()))
        loginfo('localtime=%s' % localtime)
        cmd = "date -s \'%s\'" % localtime
        loginfo(cmd)
        self.exec_command(cmd)
        loginfo('Change system time finished.')

    # check rpm install success or not		
    def check_RPM_install(self, build_num):
        rc = self.exec_command("rpm -q ddei-core | awk -F'-' '{print $4}' | awk -F'.' '{print $1}'")
        if rc != build_num:
            logerror('RPM install fail, not run cases this circle...')
            return False
        loginfo('RPM install success, run cases this circle...')
        return True


def check_install_ret(build_num, is_pit=False, build_lan='en'):
    ddei_test = DDEITest()
    ret = ddei_test.check_RPM_install(build_num)
    return ret

def clean_old_logs():
    if os.access(AUTO_LOG_FILE, os.F_OK):
        os.unlink(AUTO_LOG_FILE)

    if os.access(conf.TEST_LOG_DIR, os.F_OK):
        shutil.rmtree(conf.TEST_LOG_DIR, True)
        print '>> Delete %s' % conf.TEST_LOG_DIR

    if os.access(conf.REPORT_LOG_DIR, os.F_OK):
        shutil.rmtree(conf.REPORT_LOG_DIR, True)
        print '>> Delete %s' % conf.REPORT_LOG_DIR
    print '>> Test environment is clean'

def backup_reports():
    """ Move robotframework log and report to ./reports
    """
    if not os.access(conf.REPORT_LOG_DIR, os.F_OK):
        os.mkdir(conf.REPORT_LOG_DIR)
    
    if os.access('output.xml', os.F_OK):
        # shutil.move('output.xml', conf.REPORT_LOG_DIR + 'output.xml')
        os.system('copy /y output.xml %s' % conf.REPORT_LOG_DIR)
        os.system('del output.xml')
    if os.access('report.html', os.F_OK):
        # shutil.move('report.html', conf.REPORT_LOG_DIR + 'report.html')
        os.system('move /y report.html %s' % conf.REPORT_LOG_DIR)
    if os.access('log.html', os.F_OK):
        # shutil.move('log.html', conf.REPORT_LOG_DIR + 'log.html')
        os.system('move /y log.html %s' % conf.REPORT_LOG_DIR)


def deploy_DDEI_test_env(build_num, is_pit=False, build_lan='en'):
    ddei_test = DDEITest()
    ddei_test.deploy_ddei_test_env(build_num, is_pit, build_lan)
    return True

def begin_pit_test():
    pit = PITTest()

    if pit.is_new_pit_ready():
        loginfo("=== Trigger a PIT test ===")
        loginfo("### Finding new PIT component is ready and begin PIT Test ###")

        if not IGNOR_INSTALL:
            deploy_DDEI_test_env(GM_BUILD, is_pit=True)
        if pit.can_update_new_components():
            pit.run_ddei_pit()
            loginfo("=== Current PIT test is Done ===")
            loginfo("### PIT test is completed ###")
        loginfo("### All components are already up-to-date ###")

    loginfo("### No newer PIT component found ###")

def is_new_build_ready(build_lan='en'):
    global BVT_BUILD
    build_server = FTP()
    loginfo("Enter check build ready or not function")

    try:
        rc = build_server.connect(conf.BUILD_FTP_SERVER)
        if rc.find('220 Microsoft FTP Service') == -1:
            logerror("Fail to connect FTP Build server!")
            return False

        rc = build_server.login(conf.BUILD_FTP_USER, conf.BUILD_FTP_PWD)
        if rc.find('230 User logged in') == -1:
            logerror("Fail to Logon FTP Build server!")
            return False

        rc = build_server.cwd(BVT_BUILD[build_lan]['path'])
        build_list = build_server.nlst()
        build_list = filter(lambda x:x.isdigit(), build_list)
        build_list.sort()
        build_number = build_list[-1]
        loginfo("The latest build number is '%s'" % build_number)
        try:
            rpm_list = build_server.nlst('%s/output/RPMS' % build_number)
        except error_perm:
            logerror("Fail to find the latest version '%s' RPM file path on build server. It could build fail!" % build_number)
            return False

        build_server.close()

        loginfo("The rpm list on build server: '%s'" % (rpm_list))
        coreRPM= build_number + '/output/RPMS/ddei-core-3.1.0-' + build_number + '.i686.rpm'
        loginfo("The latest build number is '%s', coreRPM is '%s'" % (build_number, coreRPM))
        if build_number.isdigit() and build_number > BVT_BUILD[build_lan]['test_ver'] and len(rpm_list) >= 9:
            for i in range(0, len(rpm_list)):
                if rpm_list[i] == coreRPM:
                    BVT_BUILD[build_lan]['test_ver'] = build_number
                    return True

        loginfo("The latest build '%s' number is NOT newer than last build '%s'" % (build_number, BVT_BUILD[build_lan]['test_ver']))
        return False
    except:
        return False

#sender mail
def send_email_report(html_path,build_lan):
    try:
        if len(conf.MAIL_LIST) == 0:
            raise Exception, "Mail list is empty, report is not sent!"
        f = open(html_path, 'r')
        content = ''
        for item in f.readlines():
            content += str(item)
        f.close()
        msg = MIMEText(content, 'html', 'utf-8')
        msg["Accept-Language"]="zh-CN"
        msg["Accept-Charset"]="ISO-8859-1,utf-8"
        smtp = smtplib.SMTP()
        smtp.connect(conf.MAIL_SERVER)
        print 'mailserver:',conf.MAIL_SERVER        
        sender=conf.SENDER
        receiver = conf.MAIL_LIST
        print sender,receiver
        msg['Subject'] = 'DDEI_BVT_Test_Report_%s' %(BVT_BUILD[build_lan]['test_ver'] + build_lan)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()

        print "send mail success"
    except Exception, e:
        logerror("[Exception] send_email_report() get exception: %s", sys.exc_info()[:2])

# Only auto - install DDEI
def only_install_main():
    """ The BVT trigger entry

    """
    if len(sys.argv) != 2:
        print 'Wrong parameter!'
        print 'Usage:'
        print ' python Auto_trigger.py BVT'
        print '     [OR]'
        print ' python Auto_trigger.py Staging'
        return
    elif sys.argv[1] == 'BVT':
        Auto_cmd=auto_cmd()
    else:
        print 'No "%s" cases' % sys.argv[1]
        return
    clean_old_logs()

    print 'Start monitoring ...'
  
    deploy_DDEI_test_env('1159')
    loginfo("finish deploying DDEI build")

# run one time
def run_special_build_main():
    """ The BVT trigger entry
    """
    if len(sys.argv) != 2:
        print 'Wrong parameter!'
        print 'Usage:'
        print ' python Auto_trigger.py BVT'
        print '     [OR]'
        print ' python Auto_trigger.py Staging'
        return
    elif sys.argv[1] == 'BVT':
        Auto_cmd=auto_cmd()
    else:
        print 'No "%s" cases' % sys.argv[1]
        return
    clean_old_logs()

    print 'Start monitoring ...'

    for build_lan in BVT_BUILD.keys():
        #deploy_DDEI_test_env('1131')
        loginfo("finish deploying DDEI build")

        loginfo("Begin to trigger a new BVT test: %s" % Auto_cmd)
        os.system(Auto_cmd)

        clean_old_logs()
        time.sleep(30)
        try:
            backup_reports()
        except Exception as e:
            logerror(e)
            time.sleep(60)
            backup_reports()  
        time.sleep(30)

        loginfo('Begin to Parse Test Summary Report')
        loginfo('The sending report command is: %s' % conf.PARSE_REPORT_CMD)
        os.system(conf.PARSE_REPORT_CMD)

        loginfo('Begin to Send Test Report')
        loginfo('The sending report command is: %s' % conf.CMD_SEND_REPORT)
        subprocess.Popen(conf.CMD_SEND_REPORT % (BVT_BUILD[build_lan]['test_ver'] + build_lan), shell=True, stdout=subprocess.PIPE)
           
        os.system('move selenium-screenshot-*.* ./reports')

        try:
            ParseCaseResult.parse_file("./reports/output.xml")
        except:
            pass

        cmd_trigger_sctm_execution = "Trigger_SCTM_Execution.bat"
        os.system(cmd_trigger_sctm_execution)

#parse robot command
def auto_cmd():
    copy_casefile()
    #case_tag = ' '.join(["--include " + tag for tag in BVT_RUNNING_CASE_TAG])
    #Auto_cmd='pybot %s %s' % (case_tag, conf.RUN_CASE_DIR)
    Auto_cmd='pybot %s' % (conf.RUN_CASE_DIR)
    return Auto_cmd

#rerun failed case
def run_failed_cases():
    

#copy suite_list file into runcase
def copy_casefile():
    if not os.path.exists(conf.RUN_CASE_DIR):
        os.mkdir(conf.RUN_CASE_DIR)
    else:
        shutil.rmtree(conf.RUN_CASE_DIR)
        os.mkdir(conf.RUN_CASE_DIR)
    library_list=['BVT_Variables.txt','BVT_UI_Element_Mapping.txt','BVT_Resource.txt']
    need_to_copy_files=library_list+suite_list.SUITE_LIST
    loginfo(need_to_copy_files)
    for file in need_to_copy_files:
        src_file=os.path.join(conf.TEST_CASES_DIR,file)
        dst_file=os.path.join(conf.RUN_CASE_DIR,file)
        shutil.copyfile(src_file,dst_file)
    loginfo('finish copy running suites')      

def main():
    """ The BVT trigger entry

    """
    if len(sys.argv) != 2:
        print 'Wrong parameter!'
        print 'Usage:'
        print ' python Auto_trigger.py BVT'
        print '     [OR]'
        print ' python Auto_trigger.py Staging'
        return
    elif sys.argv[1] == 'BVT':
        Auto_cmd=auto_cmd()
        pass
    else:
        print 'No "%s" cases' % sys.argv[1]
        return

    clean_old_logs()
    print 'Start monitoring ...'

    run_flag=False
    while True:
        # Check if need pit test
        # begin_pit_test()

        for build_lan in BVT_BUILD.keys():
            if not is_new_build_ready(build_lan):
                logwarning("No build newer than %s found for Language %s" % (BVT_BUILD[build_lan]['test_ver'], build_lan))
                break

            loginfo("Find a new build: %s" % BVT_BUILD[build_lan]['test_ver'])
            loginfo("Begin to deploy new build: %s" % BVT_BUILD[build_lan]['test_ver'])

            if not IGNOR_INSTALL and not deploy_DDEI_test_env(BVT_BUILD[build_lan]['test_ver']):
                logerror("Fail to deploy build or Skip to deploy build (%s)." % IGNOR_INSTALL)

            loginfo("finish deploying DDEI build")

            if IGNOR_BVT:
                loginfo("Skip BVT test for current build %s for Language %s" % (BVT_BUILD[build_lan]['test_ver'], build_lan))
                break
            
            if not check_install_ret(BVT_BUILD[build_lan]['test_ver']):
                logerror("Skip BVT test for current circle: install rpm fail")
                break
            loginfo("Begin to trigger a new BVT test: %s" % Auto_cmd)
            os.system(Auto_cmd)
            run_flag=True
            #process = subprocess.Popen(Auto_cmd, shell=True, stdout=subprocess.PIPE)
            #test_result = process.stdout.read()
            #loginfo(test_result)
            clean_old_logs()
            time.sleep(30)
            try:
                backup_reports()
            except Exception as e:
                logerror(e)
                time.sleep(60)
                backup_reports()  
            time.sleep(30)
            try:
                loginfo('move screenshot')
                os.system('move selenium-screenshot-*.* ./reports')
            except Exception as e:
                logerror('move screenshot is failed!')
                pass

            loginfo('Begin to Parse Test Summary Report')
            loginfo('The sending report command is: %s' % conf.PARSE_REPORT_CMD)
            os.system(conf.PARSE_REPORT_CMD)

            loginfo('Begin to Send Test Report')

            #ftp server merge result and send report
            if IP==conf.FTP_SERVER:
                send_email_report(conf.REPORT,build_lan)
            #os.system('move selenium-screenshot-*.* ./reports')

            try:
                ParseCaseResult.parse_file("./reports/output.xml")
            except:
                pass

            cmd_trigger_sctm_execution = "Trigger_SCTM_Execution.bat"
            os.system(cmd_trigger_sctm_execution)
        if run_flag:
            break
        time.sleep(MONITOR_INTERVAL)

    
if __name__ == '__main__':
    # only_install_main()
    #run_special_build_main();
    main()

