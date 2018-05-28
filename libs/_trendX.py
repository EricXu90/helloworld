__author__ = 'anne_zhao'

from _baselib import KeywordBase
import conf
import time
import os
import SSHLibrary
import urllib
import urllib2
import ssl

class TrendXKeywords(KeywordBase):
    """
    This library contain all related keywords about Syslog function
    """

    def clean_ddei_TrendX_env(self):
        """ Clean TrendX environment
        @Param:
            path
        Return:
            None
        Example:
        | clean_ddei_TrendX_env |

        """
        print "Start clean TrendX env..."
        cmd = 'cd /var/app_data/ddei/postfix/incoming/; rm -f *'
        self.exec_command_on_DDEI(cmd)
        cmd = 'cd /var/app_data/ddei/postfix/active/; rm -f *'
        self.exec_command_on_DDEI(cmd)
        cmd = 'cd /var/app_data/ddei/postfix/deferred/; rm -rf *'
        self.exec_command_on_DDEI(cmd)
        time.sleep(1)
        print "Finished clean TrendX env."

    def detection_found_as(self):
        """ detected by TrendX
        @Param:
            path
        Return:
            None
        Example:
        | detected_by_trendX |

        """
        print "Start query DB to check log was detected by TrendX ..."
        cmd = 'select found_as from tb_object_file b left join tb_policy_event a on a.msg_id = b.msg_id;'
        ret = self.exec_sql_command_on_DDEI(cmd)
        print "Finished cquery DB to check log was detected by TrendX."
        return ret

