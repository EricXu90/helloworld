# -*- coding: utf-8 -*-
# @Date    : 2015-03-27 10:17:11
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1
"""This document defines global variables which
   may be used to locate the web elements
"""

###################### Elements encapsulation ######################
#=================================
# Common use
#=================================
IFRAME_MIDDLE_PAGE = "middle_page"
IFRAME_LEFT_PAGE = "left_page"

#=================================
# Login page
#=================================
INPUT_USER_NAME = "userid"
INPUT_PASSWORD = "password"
BUTTON_LOG_ON = "li#login_btn span"

#=================================
# Main page
#=================================
# By ID
MENU_ADMIN = "Admin"
SUB_MENU_MAIL_SETTINGS = "Navigation__SMTPRouting"
SUB_MENU_SYSTEM_SETTINGS = "Network_Setting"
SUB_MENU_VA_SETTINGS = "Virtual_Analyzer"

MENU_DETECTIONS = "Detections"
SUB_MENU_THREAT = "Threat"

#=================================
# Detections page
#=================================
# By ID
DIV_QUERY_TABLE = "query_pager"
TABLE_QUERY_RESULT = "logs"

#=================================
# Mail settings page
#=================================
# By ID
TAB_CONNECTIONS = "a_tab_connection"
TAB_MESSAGE_DELIVERY = "a_tab_delivery"
TAB_LIMITS_EXCEPTIONS = "a_tab_rule"

#=================================
# System settings page
#=================================
# System settings > Network
# By ID
TAB_NETWORK = "tab1_link"
RADIO_MTA_MODE = "mta"
RADIO_BCC_MODE = "bcc"
RADIO_TAP_MODE = "TAP"
SPAN_NETWORK_INLINE_MESSAGE = "flag"
# By CSS
BTN_NETWORK_SAVE = "li#tab_network_save span"
BTN_NETWORK_CANCEL = "li#tab_network_cancel span"

# System settings > Notification SMTP
# By ID
TAB_NOTIFICATION_SMTP = "tab2_link"
RADIO_BTN_INTERNAL = "internal"
RADIO_BTN_EXTERNAL = "external"
INPUT_SERVER_NAME = "smtp_server"
INPUT_SERVER_PORT = "smtp_port"
SPAN_SMTP_INLINE_MESSAGE = "flag1"
# By CSS
BTN_SMTP_SAVE = "li#tab_smtp_save span"
BTN_SMTP_CANCEL = "li#tab_smtp_cancel span"

#==================================
# Scanning / analysis page
#==================================
# Archive password
# Entry
# By ID
LEFT_MENU_ARCHIVE_PASSWORDS = "Navigation__ARCHIVE_PWD"

# Add password
# By ID
SPAN_ADD_PASSWORD = "add"
SPAN_PASSWORD_INLINE_MESSAGE = "flag"
# By XPATH
INPUT_PASSWORD_LIST = "//input[@type='text']"
# By CSS
SPAN_REMOVE_PASSWORD = "span.remove"
BTN_SAVE = "li#btnSave span"
BTN_CANCEL = "li#btnCancel span"
#BTN_CLOSE = "span.button_content"
#BTN_IMPORT = "span.button_content"

# Import password
# By XPATH
BTN_IMPORT = "//ul/li[2]/span"
BTN_CLOSE = "//ul/li[1]/span"
#BTN_IMPORT = "/html/body/div[3]/div[3]/ul/li[2]/span"
#BTN_CLOSE = "/html/body/div[3]/div[3]/ul/li[1]/span"
INPUT_UPLOAD_PASSWORD = "//input[@type='file']"
A_DOWNLOAD_SAMPLE_PASSWORD = "/html/body/div/div[2]/a"

# By ID
BTN_BROWSE_FILE = "import_csv"
SPAN_IMPORT_PASSWORD = "import"
IFRAME_IMPORT_PASSWORD = "ui-tmPopup-Content-Iframe-ui-dialog-title-import"
SPAN_TOP_ERROR_MSG = "widget_sandbox_queue_top_msg"
SELECT_PASSWORD_FILTER = "filter_select"

# By CSS
TABLE_FILTER_RESULT = "table#import_result tr"
