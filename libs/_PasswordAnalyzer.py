__author__ = 'Administrator'

import os
import re
import subprocess
import time
import email
import ConfigParser
import SSHLibrary

import conf


class PA_Keywords:
    """
    This library is only for password analyzer feature.

    """
    def __init__(self):
        """ Init
        """
        self.ssh_conn = SSHLibrary.SSHLibrary()
        self.conn_id = None
        self.test_log_file = ''

    def get_default_value(self, section, option_name):
        """ get DDEI default setting on file /opt/trend/dde/config/imss.ini

        @Param:

            section:    the section name

            option_name:    the option setting name in system config file

        Return:

            default value

        Example:

        |Get Default Value | password_analyzer | time_out_second |

        """
        imss = "/opt/trend/ddei/config/imss.ini"
        imss_local = os.path.join(conf.AUTO_ROOT, 'imss.ini')
        config = ConfigParser.ConfigParser()

        self.get_file_from_DDEI(imss, imss_local)
        config.read(imss_local)
        value = config.get(section,option_name)
        return value.strip()

    def inform_pa_use_new_config(self, host = conf.DDEI_IP, prompt = '#',usr = conf.SSH_USR, pwd = conf.SSH_PWD):
        """ inform password analyzer process to use new configuration /opt/trend/dde/config/imss.ini

        @Param:

            none

        Return:

            none

        Example:

        |inform_pa_use_new_config |

        """
        self.conn_id = self.ssh_conn.open_connection(host, prompt)
        conf.SSH_USR = usr
        conf.SSH_PWD = pwd
        sc = self.ssh_conn.login(usr, pwd)
        return sc
        self.ssh_conn.execute_command("sudo kill -SIGHUP $(ps -ef | grep -v grep | grep passwordAnalyzer.pyc | awk '{ print $2 }')")

    def clear_password_bank(self):
        """ get DDEI default setting on file /opt/trend/dde/config/imss.ini

        @Param:

            section:    the section name

            option_name:    the option setting name in system config file

        Return:

            default value

        Example:

        |Get Default Value | password_analyzer | time_out_second |

        """
        self.ssh_conn.execute_command(">/opt/trend/ddei/config/password_bank_file.conf")
        self.ssh_conn.execute_command("/opt/trend/ddei/script/S99PASSWORDANALYZER restart")

