"""	Common configuration of TestDDEI
"""

import os,re
from subprocess import Popen, PIPE

#======================================
# Running automation machine IP(win7)
#======================================
LOCAL_IP=re.search('\d+\.\d+\.\d+\.\d+',Popen('ipconfig', stdout=PIPE).stdout.read()).group(0)

#======================================
# Path related settings
#======================================

AUTO_ROOT	= os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
TEST_CASES_DIR	= os.path.join(AUTO_ROOT, 'testcases\\')
TEST_LOG_DIR = os.path.join(AUTO_ROOT, 'testlogs\\')
REPORT_LOG_DIR = os.path.join(AUTO_ROOT, 'reports\\')
TEST_DATE_DIR = os.path.join(AUTO_ROOT, 'testdata\\')
TEST_TOOL_DIR = os.path.join(AUTO_ROOT, 'tools\\')
RUN_CASE_DIR = os.path.join(AUTO_ROOT, 'runcases\\')

CASE_ID	= ''

LATEST_RESULTS_DIR=os.path.join(AUTO_ROOT,'results\\latest\\')
RESULTS_DIR_TEMP=os.path.join(AUTO_ROOT,'results\\temp\\')
HISTORY_RESULT_DIR=os.path.join(AUTO_ROOT,'results\\history\\')
HISTORY_FAIL_DIR=os.path.join(HISTORY_RESULT_DIR,'fail\\')
FTP_SERVER_DIR=r'C:\BVT\usbx\Report result'
#======================================
# Email related settings
#======================================

TEMAIL_BIN	= os.path.join(AUTO_ROOT, 'tools', 'temail.exe')
if LOCAL_IP=='10.204.191.68':
    SMTP_SERVER='10.204.191.67'
elif LOCAL_IP=='10.204.253.120':
    SMTP_SERVER	= '10.204.253.126'
elif LOCAL_IP=='10.204.253.117':
    SMTP_SERVER='10.204.253.119'
else:
    pass
MAIL_TO		= 'test@ddei.com'
MAIL_FROM       = 'bvt@test.com'
EDGE_IP		= '7.3.3.1'
SENDER_IP 	= '1.2.3.4'
IP_FAKEMTA = ''
PORT_FAKEMTA = '11067'
FAKEMTA_PATH_DIR = os.path.join(AUTO_ROOT, 'fakeMTA\\')

#======================================
# Automation running host related settings
#======================================

LOCAL_HOST    = LOCAL_IP
LAB_SMTP_SERVER = '10.204.16.7'
REPORT_RCPT_LIST = 'report_rcpt_list.txt'
TEMAIL_CONFIG = os.path.join(AUTO_ROOT, 'temail.ini')
PARSE_FILE = os.path.join(AUTO_ROOT, "RobotXML2htmlResult.py")
REPORT = os.path.join(REPORT_LOG_DIR, 'out.html')
PARSE_REPORT_CMD = "python %s %s %s" %(PARSE_FILE, os.path.join(REPORT_LOG_DIR, "output.xml"), REPORT)
CMD_SEND_REPORT = "%s -INI=%s -TO=@%s -SUBJECT=DDEI_BVT_Test_Report_%s %s" % (TEMAIL_BIN, TEMAIL_CONFIG, REPORT_RCPT_LIST, "%s", REPORT)

LAB_PROXY_SERVER = "10.204.16.17"
LAB_PROXY_PORT = "8087"
LAB_PROXY_TYPE = "http"
LAB_PROXY_USER = ""
LAB_PROXY_PASS = ""

CUSTOM_DNS = "10.204.253.237"

# add some conf by eric
MAIL_LIST=['AllofTrendDDEIQA@dl.trendmicro.com','yanan_zhang@trendmicro.com.cn']
#MAIL_LIST=['eric_xu@trendmicro.com.cn']
SENDER='BVT@ddei.com'
MAIL_SERVER='10.204.16.7'
FTP_SERVER='10.204.191.68'
IMPORT_IMAGE_WIN7_MACHINE="10.204.191.68"
TIME_OUT=25200
FTP_28='10.204.16.28'
USER='trend\eric_xu'
PWD='Yhxu_seu1018'
AUTOMATION_CLINET_IP_LIST=["10.204.253.120","10.204.191.68","10.204.253.117"]
REMOTE_IP={
    '120':'10.204.253.120',
    '68':'10.204.191.68',
    '117':'10.204.253.117'
}
#======================================
# BUILD FTP related settings
#======================================
BUILD_FTP_SERVER = '10.204.16.2'
BUILD_FTP_USER = 'ddei'
BUILD_FTP_PWD = 'trend#100'
BUILD_FOLDER = 'Build/DDEI/2.0/centos6_3_x64/en/Rel/Latest/Release/Output/RPMS'
BUILD_RPM_FILE_LIST = ['ddei-core-*.i686.rpm', 'ddei-sys-*.i686.rpm', 'ddei-utility-*.i686.rpm']

#======================================
# DDEI server related settings
#======================================
if LOCAL_IP=='10.204.191.68':
    DDEI_IP='10.204.191.67'
    NEXT_MTA_ADDR='10.204.191.68'
elif LOCAL_IP=='10.204.253.120':
    DDEI_IP='10.204.253.126'
    NEXT_MTA_ADDR   = '10.204.253.129'
elif LOCAL_IP=='10.204.253.117':
    DDEI_IP='10.204.253.119'
    NEXT_MTA_ADDR='10.204.253.117'
else:
    pass  
SSH_USR		= 'root'
SSH_PWD		= 'ddei'
DB_USR		= 'sa'
DB_PWD		= '111111'
DB_NAME         = 'ddei'
POSTCONF        = '/opt/trend/ddei/postfix/usr/sbin/postconf -e'
PSQL_EXE    = '/opt/trend/ddei/PostgreSQL/bin/psql %s %s -t -c ' % (DB_NAME, DB_USR)
UI_USR = 'admin'
UI_PWD = 'ddei'

TABLE_POLICY_EVENT  = 'tb_policy_event_total'
TABLE_QUARANTINE    = 'tb_quarantine'
TABLE_OBJECT_FILE   = 'tb_object_file'
TABLE_OBJECT_URL    = 'tb_object_url'
TABLE_OBJECT_HOST   = 'tb_object_host'
TABLE_MSG_TRACING   = 'tb_msg_tracing'
TABLE_SYS_EVENT     = 'tb_system_event'
TABLE_ALERT_EVENT   = 'tb_alert_triger_event'

TABLE_SBX_TASK = 'tb_sandbox_tasks'
TABLE_SBX_TASK_HISTORY = 'tb_sandbox_tasks_history'
TABLE_SBX_TASK_DETAILS = 'tb_sandbox_task_details'
TABLE_SBX_REPORT_ACCESS_RECORDS = 'tb_sandbox_report_access_records'
TABLE_SBX_REPORT_ACCESS_URLS = 'tb_sandbox_report_access_urls'
TABLE_SBX_REPORT_DROPPED_FILES = 'tb_sandbox_report_dropped_files'
TABLE_SBX_REPORT_FILE_ANALYZE = 'tb_sandbox_report_file_analyze'
TABLE_SBX_REPORT_VULNERABILITIES = 'tb_sandbox_report_vulnerabilities'
TABLE_SBX_REPORT_IMAGES = 'tb_sandbox_report_images'
TABLE_SBX_REPORT_SYSTEM_BEHAVIORS = 'tb_sandbox_report_system_behaviors'
TABLE_SBX_REPORT_VIOLATED_EVENTS = 'tb_sandbox_report_violated_events'
TABLE_SBX_URLFILTER_CACHE = 'tb_sandbox_urlfilter_cache'
TABLE_BLACKLIST = 'tb_blacklist'

#======================================
# DDEI must processes
#======================================
DDEI_MUST_PROCESS_LIST = [
'/opt/trend/ddei/postfix/usr/libexec/postfix/master',
'/opt/trend/ddei/PostgreSQL/bin/postgres',
'/opt/trend/ddei/bin/imssmgrmon',
'/bin/sh /opt/trend/ddei/script/usandbox_watchdog.sh',
'/opt/trend/ddei/bin/wrsagent',
'/opt/trend/ddei/bin/imssmgr',
'/opt/trend/ddei/bin/scanner'
]
DDEI_INSTALL_LOG = '/opt/trend/ddei/installlog/DDEIInstall.log'
CMD_DDEI_UNINSTALL = '/opt/trend/ddei/installer/uninstall_ddei_app.sh'
CMD_DDEI_INSTALL_1 = 'rpm -ivh /root/*.rpm'
CMD_DDEI_INSTALL_2 = '/opt/trend/ddei/installer/install_ddei_app.sh'
CMD_DDEI_RESART_SERVICE = '/etc/init.d/rcDDEI restart'

CMD_ENABLE_SCANNER = "sed -i -e '/\[smtp\]/a smtp_virus_scan=yes' /opt/trend/ddei/config/imss.ini"
CMD_RESTART_SCANNER = "/opt/trend/ddei/script/S99IMSS restart"
CMD_START_SCANNER = "/opt/trend/ddei/script/S99IMSS start"
CMD_STOP_SCANNER = "/opt/trend/ddei/script/S99IMSS stop"
CMD_RESTART_MANAGER = "/opt/trend/ddei/script/S99MANAGER restart"
CMD_RESTART_WRSAGENT = "/opt/trend/ddei/script/S99WRSAGENT restart"
CMD_RESTART_SAAGENT = "/opt/trend/ddei/script/S99SAAGENT reload"
CMD_RESTART_TASKPROCESSOR = "/opt/trend/ddei/script/S99TASKMONITOR reload_scripts"

#======================================
# Email policy action related settings
#======================================

EMAIL_TAG       = ''
EMAIL_STRIP_FILE    = ''
EMAIL_STAMP    = ''

POLICY_SETTING_FILE = "/opt/trend/ddei/config/policy_setting.xml"
FILE_EXCEPTION_TYPE = "4"
URL_EXCEPTION_TYPE = "3"
ADD_EXCEPTION_CMD = "sed -i '/<hls>/a <item><itemid>%s</itemid><name>%s</name><type>%s</type><notes></notes><added>2013-09-12 15:43</added></item>' " + POLICY_SETTING_FILE
RELOAD_POLICY_CMD = "/opt/trend/ddei/script/policy_reload.sh"
EXCEPTION_COUNT = "grep -Eo '<item>' %s | wc -l" % POLICY_SETTING_FILE
CLEAR_URL_FILE_EXCPETION_CMD = "sed -i '/<item>/d' " + POLICY_SETTING_FILE

SENDER_EXCEPTION_TYPE = "sender"
RCPT_EXCEPTION_TYPE = "rcpt"
XHEADER_EXCEPTION_TYPE = "xheader"
ADD_RCPT_EXCEPTION_CMD = "sed -i -e '/<recipients>/d' -e '/<messages>/a <recipients><![CDATA[%s]]></recipients>' " + POLICY_SETTING_FILE
ADD_SENDER_EXCEPTION_CMD = "sed -i -e '/<senders>/d' -e '/<messages>/a <senders><![CDATA[%s]]></senders>' " + POLICY_SETTING_FILE
ADD_XHEADER_EXCEPTION_CMD = "sed -i -e '/<x_header>/d' -e '/<messages>/a <x_header><![CDATA[%s]]></x_header>' " + POLICY_SETTING_FILE


#======================================
# U-sandbox related settings
#======================================
USBX_IMAGE_FTP_SERVER = '10.204.191.68'
USBX_IMAGE_FOLDER = 'usbx'
USBX_IMAGE_XP = 'POC_xpsp3en_o2k3_o2k7_adXI_dn4.ova'
USBX_IMAGE_WIN7 = 'MAK_win7sp1en_offices_noab_x64_ID14.ova'

USBX_CLI_BIN = 'sudo python /opt/trend/ddei/u-sandbox/usandbox/cli/usbxcli.py'
USBX_MANAGE_BIN = 'sudo python /opt/trend/ddei/script/manage_sandbox.py'
USBX_VA_UTILS = 'sudo python /opt/trend/ddei/UI/adminUI/ROOT/usandbox/va_utils.py'

### Max cycle can be tolerated, one cycle means 10 mins ###
USBX_MAX_WAIT_CYCLE = 10
IMAGE_PATH = ''

### Command to control U-sandbox ###
CMD_USBX_IMPORT		= USBX_CLI_BIN + ' sbxgrp-create'
CMD_USBX_GET_STATE 	= USBX_CLI_BIN + ' sys-getstate'
CMD_USBX_INIT 		= USBX_CLI_BIN + ' sys-init'
CMD_USBX_START		= USBX_CLI_BIN + ' sys-start'
CMD_USBX_RESTART 	= USBX_CLI_BIN + ' sys-restart'
CMD_USBX_STOP		= USBX_CLI_BIN + ' sys-stop'
CMD_USBX_PURGE_CACHE    = USBX_CLI_BIN + ' op-purgecache --all'
CMD_USBX_PURGE_TASK     = USBX_CLI_BIN + ' op-purgeresult --all --force'
CMD_USBX_PURGE_ONE_TASK = USBX_CLI_BIN + ' op-purgeresult --id '
CMD_USBX_PURGE_BLACKLIST= USBX_CLI_BIN + ' op-purgeblacklist --all'
CMD_USBX_SET_GATEWAY    = USBX_CLI_BIN + ' set-gateway'
CMD_USBX_SET_PROXY      = USBX_CLI_BIN + ' set-proxy'
CMD_USBX_SET_PSWD       = USBX_CLI_BIN + ' set-passwddict'
CMD_USBX_CLEAR_PSWD       = CMD_USBX_SET_PSWD + ' --clear'
CMD_USBX_DEL_ALL_GROUP  = USBX_CLI_BIN + ' sbxgrp-delete --all'
CMD_USBX_SET_EXTSERVICES = USBX_CLI_BIN + ' set-extservices'
CMD_USBX_SUBMIT_SAMPLES = USBX_CLI_BIN + ' op-submitsample '
CMD_USBX_SUBMIT_URL = USBX_CLI_BIN + ' op-submiturl '
CMD_USBX_GET_TASK_STATUS = USBX_CLI_BIN + ' op-getstatus'
CMD_USBX_DISABLE_CACHE = USBX_CLI_BIN + ' set-cache --switch off'
CMD_USBX_ENABLE_CACHE = USBX_CLI_BIN + ' set-cache --switch on'
CMD_USBX_ENABLE_DEBUG = USBX_CLI_BIN + ' set-debug --level DEBUG'
CMD_USBX_DISABLE_DEBUG = USBX_CLI_BIN + ' set-debug --level ERROR'
CMD_USBX_RELOAD_PROXY = USBX_MANAGE_BIN + ' --loadproxy'

#### Config Custom File Type ####
VA_FILE_TYPE_BZIP2  = '<type name="BZIP2">121</type>'
VA_FILE_TYPE_CHM    = '<type name="CHM">4039</type>'
VA_FILE_TYPE_LNK    = '<type name="LNK">24|6019</type>'
VA_FILE_TYPE_OFFICE = '<type name="OFFICE">4045|1|2|4|4029|206|1003|1004|_mso</type>'
VA_FILE_TYPE_PDF    = '<type name="PDF">6015</type>'
VA_FILE_TYPE_RAR    = '<type name="RAR">25</type>'
VA_FILE_TYPE_SWF    = '<type name="SWF">4038</type>'
VA_FILE_TYPE_TAR    = '<type name="TAR">20</type>'
VA_FILE_TYPE_EXE    = '<type name="WIN_EXE">7</type>'
VA_FILE_TYPE_HTML   = '<type name="HTML">.htm|.html</type>'
VA_FILE_TYPE_ZIP    = '<type name="ZIP">2003|4003</type>'

SANDBOX_FILTER_FILE = "/opt/trend/ddei/config/sandbox_filter.xml"

CMD_RESET_ALL_FILE_TYPE = "sed -i -e '/selected_file_types/d' -e '/<type name=/d' %s" % SANDBOX_FILTER_FILE
CMD_ADD_FILE_TYPE = "sed -i '/<config>/a <selected_file_types>%s</selected_file_types>' %s" % ('%s', SANDBOX_FILTER_FILE)

#======================================
# DB in DDEI related settings
#======================================
PSQL_BIN = '/opt/trend/ddei/PostgreSQL/bin/psql'
DB_USER		= 'sa'
DB_PWD		= '111111'

#======================================
# Severity flag settings
#======================================
UNSCANNABLE = 5
UNSCANNABLE_ENABLE=4

HIGH   = 3
MEDIUM = 2
LOW    = 1
NO     = 0
YES = 1

#======================================
# Blacklist type
#======================================
IP     = 0
URL    = 1
FILE   = 2
DOMAIN = 3

#======================================
# Alert Function
#======================================
CMD_RESTART_ALERT = "/opt/trend/ddei/script/S99ALERT restart"
ALERT_RULES = {
    '1' : [1, 'System: Message Delivery Queue'],
    '2' : [2, 'System: CPU Usage'],
    '3' : [3, 'Security: Messages Detected'],
    '4' : [4, 'Security: Watchlist'],
    '5' : [5, 'System: Sandbox Stopped'],
    '6' : [6, 'System: Sandbox Queue'],
    '7' : [7, 'System: Average Sandbox Processing Time'],
    '8' : [8, 'System: Disk Space'],
    '9' : [9, 'System: Detection Surge'],
    '10': [10, 'System: Processing Surge'],
    '11': [11, 'System: Service Stopped'],
    '12': [12, 'System: Unreachable Relay MTAs'],
    '13': [13, 'System: Update Failed'],
    '14': [14, 'System: Update completed'],
    '15': [15, 'System: License Expiration']
    }

#======================================
# Product Licence Function
#======================================
AC_CODE = "DE-P2KU-UGUEC-BV4H9-3QF8Q-6CPVM-J2MSL"
AC_CODE_GOLDEN = "AP-V3NQ-PNKHN-LAVYX-7YWEU-9BHM3-MG6AH"     #12/31/2018
CMD_ACTIVATE_ATP_PR = "/opt/trend/ddei/script/pr_active.sh -registini 0 %s" % AC_CODE_GOLDEN
CMD_ACTIVATE_GM_PR = "/opt/trend/ddei/script/pr_active.sh -registini 1 %s" % AC_CODE_GOLDEN
PR_TEST_SCIPT_LOCAL_PATH = os.path.join(TEST_DATE_DIR, 'pr\\')
AC_CODE_ATD_FULL_OLD = "DE-EP36-MXYDQ-4VLJX-TXHEA-4L885-DLPQM"    #12/31/2017
AC_CODE_SEG_FULL_OLD = "DE-L42N-2NE2Q-EAQLF-H9FML-G4EYZ-ZDZ9H"    #12/31/2017
AC_CODE_ATD_FULL0 = "DE-DXGE-9CNU5-NMFG6-Z6KFC-TNBKX-CHMFF"   #12/31/2016
AC_CODE_ATD_FULL = "DE-URHN-VC8DF-VF84K-BPQ72-2EABH-QEG2G"    #12/31/2018(update)
AC_CODE_SEG_FULL = "DE-4LEA-M9MCD-VXDMW-SJN5V-JBXML-5SPLH"    #12/31/2018(update)
AC_CODE_ATD_TRIAL = "DE-4ACH-7TL7T-D4F5X-ZAMTS-XG85F-ZWDKC"   #12/31/2018(update)
AC_CODE_SEG_TRIAL = "DE-X86X-R6NRX-4SV3R-T84VC-8HEA6-S6TBH"   #12/31/2018(update)
AC_CODE_GOLDEN = "AP-V3NQ-PNKHN-LAVYX-7YWEU-9BHM3-MG6AH"     #12/31/2018
AC_CODE_ATD_FULL2 = "DE-SXMK-MVL4Y-YJ8JG-K5CT7-NVVCC-VRC4Q"  #6/1/2018
AC_CODE_SEG_TRIAL_NEW = "DE-N2D9-TPKF9-GTXDS-GNZBU-WM6FM-76A5B"  #12/31/2018(update)
AC_CODE_ATD_TRIAL_NEW = "DE-7UG8-JZLU7-43R5R-7SXUD-3NJK9-4Y6LL"  #12/31/2018(update)
AC_CODE_ATD_FULL_NEW = "DE-XDZX-54FPZ-ASD3T-4V3XA-YU8RS-S3GUM"   #12/31/2018(update)
AC_CODE_ATD_FULL_LAST = "DE-7MCN-GUK8U-7DLD9-PNCS4-C9HFE-YKUER"  #07/13/2028
AC_CODE_ATD_FULL_JAPAN = "DE-5QX5-GD4T9-32QDL-DFVNW-TJDZ6-EV6SR" #12/31/2018(update)
AC_CODE_ATD_FULL_INVALID = "DE-P2KU-UGUEC-BV4H9-3QF8Q-6CPVM-F88XX"   #12/31/2017
AC_CODE_EXPIRED_DATE = "2018-12-31" #(update)
AC_CODE_TRIAL_EXPIRED_DATE = "2018-12-31" #(update)
AC_CODE_GOLDEN_EXPIRED_DATE = "2018-12-31"

CMD_SET_EXPIRE_TIME = "2018-12-31 00:00:01" #(update)
CMD_SET_GRACE_EXPIRE_TIME = "date -s '2019-01-30 00:00:01'" #(update)
CMD_SET_BEFORE_EXPIRE_14_DAYS_TRAIL = "2018-12-17 00:00:01" #(update)
CMD_SET_BEFORE_EXPIRE_30_DAYS_TRAIL = "2018-12-1 00:00:01" #(update)
CMD_SET_BEFORE_EXPIRE_30_DAYS_FULL = "2018-12-01 00:00:01" #(update)
CMD_SET_EXPIRE_TIME_TRIAL = "2018-12-31 00:00:01" #(update)
FAKE_PR_SERVER_IP = "10.204.253.252"

#======================================
# DB Aggregation Function
#======================================
DO_AGGR_ACTION = "%s '%s'" % (PSQL_EXE, 'select tb_aggr_unified_refresh()')
EXE_DB_SQL_FILE = "/opt/trend/ddei/PostgreSQL/bin/psql %s %s -f %s" % (DB_NAME, DB_USR, '%s')

TABLE_AGGR_BY_ATTACH_NAME = "tb_aggr_by_attachmentname"
TABLE_AGGR_BY_ATTACH_TYPE = "tb_aggr_by_attachmenttype"
TABLE_AGGR_BY_IP = "tb_aggr_by_attacker_ip"
TABLE_AGGR_BY_HOST = "tb_aggr_by_host"
TABLE_AGGR_BY_RCPT = "tb_aggr_by_recipient"
TABLE_AGGR_BY_SENDER = "tb_aggr_by_sender"
TABLE_AGGR_BY_SUBJECT = "tb_aggr_by_subject"
TABLE_AGGR_BY_URL = "tb_aggr_by_url"
TABLE_AGGR_BY_MSG_CNT = "tb_aggr_msg_count"
TABLE_AGGR_BY_MSG_PROCESS = "tb_aggr_msg_processing"
TABLE_AGGR_BY_POLICY_RULE = "tb_aggr_by_policy_rule"
TABLE_AGGR_BY_QUARANTINE_REASON = "tb_aggr_by_quarantine_reason"
TABLE_AGGR_BY_THREAT_TYPE = "tb_aggr_by_threat_type"
TABLE_AGGR_BY_THREAT_CHARACTERISTIC = "tb_aggr_by_threat_characteristic"
TABLE_RCPT = 'tb_recipient'
TABLE_LAST_AGGR = "tb_lastaggr_time"

#======================================
# DB Threat Type
#======================================
CMD_APPEND_LOG = "cat %s >> `ls -t -r /opt/trend/ddei/log/polevt.imss.* | tail -1`"

THREAT_TYPE_TARGET_MALWARE = "1"
THREAT_TYPE_MALWARE = "2"
THREAT_TYPE_MAL_URL = "3"
THREAT_TYPE_POTEN_FILE = "4"
THREAT_TYPE_POTEN_URL = "5"

#======================================
# Components AU Update
#======================================
CMD_AU_UPDATE = "/opt/trend/ddei/UI/adminUI/ROOT/au_update/update.sh update"
CMD_AU_ROLLBACK = "/opt/trend/ddei/UI/adminUI/ROOT/au_update/update.sh rollback"
CMD_AU_GET_VERSION = "/opt/trend/ddei/UI/adminUI/ROOT/au_update/update.sh version"

CMD_UPDATE_ALL = "%s %s" % (CMD_AU_UPDATE, "1111111111")
CMD_UPDATE_SC = "%s %s" % (CMD_AU_UPDATE, "0000001000")

AU_SERVER_PRE_OPR = "http://ddei20-p.pre-opr-au.trendmicro.com/activeupdate/"
AU_SERVER_OPR = "http://ddei20-p.activeupdate.trendmicro.com/activeupdate/"

UPDATABLE_COMPONENTS_COMMANDS = {
    "1": ["10000000000000", "virus_pattern_version"],
    "2": ["01000000000000", "spyware_pattern_version"],
    "3": ["00100000000000", "intellitrap_pattern_version"],
    "4": ["00010000000000", "intellitrap_exception_version"],
    "5": ["00010000000000", "spam_engine_version"],
    "6": ["00010000000000", "spam_pattern_version"],
    "9": ["00001000000000", "atse_engine_version"],
    "11": ["00000100000000", "atse64_engine_version"],
    "12": ["00000010000000", "sandcastle_client_engine_version"],
    "13": ["00000001000000", "sal_pattern_version"],
    "14": ["00000000100000", "smv_pattern_version"],
    "15": ["00000000010000", "nccp_pattern_version"],
    "16": ["000000000010000", "sal_engine_version"],
    "17": ["000000000001000", "trustca_pattern_version"],
    "18": ["000000000000100", "ncip_pattern_version"],
    "19": ["000000000000010", "ncie_engine_version"],
    "20": ["000000000000001", "va_pattern_version"],
    "21": ["0000000000000001", "trxhandler_engine_version"],
    "22": ["00000000000000001", "trendx_pattern_version"],
    "23": ["000000000000000001", "trxhandler64_engine_version"],
    "all": ["111111111111111111", "all"]
}

#======================================
# Feedback related
#======================================
TMFBED_CONFIG = "/opt/trend/ddei/config/tmfbed.conf"
GUID_CONFIG = "/opt/trend/ddei/config/tmfbed_guid.conf"

FQDN_SERVER = "ddei200-en.fbs20.trendmicro.com"
PRODUCT_ID = '705'
PRODUCT_VERSION = '2.5.0'
PRODUCT_LANG = '1'
PRODUCT_PLATFORM = '9217'

GLCFG = "/opt/TrendMicro/GoldenGate/bin/glcfg"
S99TMFBED = "/opt/trend/ddei/script/S99TMFBED"
USBX_FEEDBACK = USBX_CLI_BIN + ' set-feedbackblacklist'

BLOB_FOLDER='/var/tmfbed_tmp/'
TMFBED_FOLDER='/root/tmfbed'

#======================================
# IPv6 related settings
#======================================
DDEI_IPV6_ADDRESS = '2620:101:4002:772::265'
DDEI_IPV6_PREFIX = '64'
DDEI_IPV6_DEFAULT_DNS = '2620:101:4002:772::263'
DDEI_IPV6_DEFAULT_GATEWAY = '2620:101:4002:772::1'
DDEI_IPV4_DEFAULT_DNS = '10.204.253.123'

UPSTREAM_MTA_IPV4 = '10.204.253.121'
UPSTREAM_MTA_IPV6 = '2620:101:4002:772::261'
UPSTREAM_MTA_IPV6_SUBNET = '2620:101:4002:772::'
UPSTREAM_MTA_IPV6_PREFIX = '64'

DOWNSTREAM_MTA_IPV4 = '10.204.253.122'
DOWNSTREAM_MTA_IPV6 = '2620:101:4002:772::262'
DOWNSTREAM_MTA_IPV6_SUBNET = '2620:101:4002:772::'
DOWNSTREAM_MTA_IPV6_PREFIX = '64'

MAIL_CLIENT = '10.204.253.123'
MAIL_CLIENT_USER = 'root'
MAIL_CLIENT_PW  = '111111'

EXTERNAL_SMTP_IPV4 = '10.204.253.123'
EXTERNAL_SMTP_IPV6 = '2620:101:4002:772::263'

SYSLOG_IPV6_ADDRESS = "2620:101:4002:772::263"
SYSLOG_IPV4_ADDRESS = "10.204.253.123"
SYSLOG_USR = "root"
SYSLOG_PWD = "111111"
SYSLOG_PORT_TCP = "611"
SYSLOG_PORT_UDP = "520"
SYSLOG_PORT_SSL = "60515"

#=====================================
# Postfix related settings
#=====================================
TABLE_POSTFIX_CONFIG = "tb_postfixconfig"
CMD_POSTFIX_RESTART = "/opt/trend/ddei/script/postfix restart"
CMD_POSTFIX_RELOAD = "/opt/trend/ddei/script/postfix reload"
POSTFIX_FOLDER = "/opt/trend/ddei/postfix/etc/postfix"
POSTGRESQL_BIN = "/opt/trend/ddei/PostgreSQL/bin/psql"

#======================================
# Syslog related settings
#======================================

LAG_SYSLOG_SERVER = '10.204.253.123'
LAB_SYSLOG_USER = "root"
LAB_SYSLOG_PASS = "111111"

#=====================================
# Smart Protection settings
#=====================================
RP_CERT_PATH = '/opt/trend/ddei/config/local_sps.pem'
RP_CRL_PATH = '/opt/trend/ddei/config/sps_crl'

#======================================
# system-setting-DDD
#======================================
DDD_LOGIN_PAGE = '/login.ddei'
DDD_REGISTER_PAGE = '/php/update_center.php'
DDD_UNREGISTER_PAGE = DDD_REGISTER_PAGE
DDD_TEST_CONNECTION_PAGE = DDD_REGISTER_PAGE
DDD_HOST = '10.204.253.128'
DDD_Domain = 'ddd.trendmicro.com'
DDD_API_KEY = 'cbdd086c-76b0-424b-b0fe-23c4c23675c7'
Global_Proxy_Setting_Page = '/saveProxySetting.ddei'

#======================================
# Hotfix/patch upgrade
#======================================
DIR_FILE_UPLOAD = "/var/app_data/ddei/temp/"
CMD_HOTFIX_UPGRADE="/usr/bin/python /opt/trend/ddei/at_upgrade/at_upgrade.py -t hotfix -f "
CMD_HOTFIX_ROLLBACK="/usr/bin/python /opt/trend/ddei/at_upgrade/at_upgrade.py -t rollback_hotfix apply"
LOCAL_FILE_PATH=TEST_DATE_DIR
PATCH_FILE="/usr/local/openva-update-tools/patchmgm.ini"
BACKUP_FILE="/var/app_data/ddei/patch/openva-update-tools/unpack/patchmgm.ini"
PACKAGE_CONFIG="/var/tmp/config.ini"
