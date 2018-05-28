__author__ = 'anne_zhao'

from _baselib import KeywordBase
import conf
import time
import os
import SSHLibrary
import urllib
import urllib2
import ssl

class MsgQKeywords(KeywordBase):
    """
    This library contain all related keywords about Syslog function
    """

    def insert_msgQ_data(self, type):
        """ insert mail into msg queue path
        @Param:
            type
        Return:
            None
        Example:
        | insert_msgQ_data |

        """
        print "Start insert mail into msg queue path..."
        if type == 'incoming': 
            cmd = 'cp /root/3* /var/app_data/ddei/postfix/incoming/;'
            self.exec_command_on_DDEI(cmd)
        elif type == 'active':
            cmd = 'cp /root/9* /var/app_data/ddei/postfix/active/;'
            self.exec_command_on_DDEI(cmd)
        elif type == 'deferred':
            cmd = 'mkdir /var/app_data/ddei/postfix/deferred/7;'
            self.exec_command_on_DDEI(cmd)
            cmd = 'cp /root/7* /var/app_data/ddei/postfix/deferred/7/;'
            self.exec_command_on_DDEI(cmd)
        elif type == 'condition':
            cmd = 'mkdir /var/app_data/ddei/postfix/deferred/6;'
            self.exec_command_on_DDEI(cmd)
            cmd = 'cp /root/6* /var/app_data/ddei/postfix/deferred/6/;'
            self.exec_command_on_DDEI(cmd)
        elif type == 'DBCS':
            cmd = 'cp /root/A3* /var/app_data/ddei/postfix/incoming/;'
            self.exec_command_on_DDEI(cmd)
            cmd = 'cp /root/A7* /var/app_data/ddei/postfix/active/;'
            self.exec_command_on_DDEI(cmd)
            cmd = 'mkdir /var/app_data/ddei/postfix/deferred/A;'
            self.exec_command_on_DDEI(cmd)
            cmd = 'cp /root/A2* /var/app_data/ddei/postfix/deferred/A/;'
            self.exec_command_on_DDEI(cmd)
        print "Finished insert mail into msg queue path."

    def clean_msgQ_incoming_data(self):
        """ clean mail into msg queue path
        @Param:
            path
        Return:
            None
        Example:
        | clean_msgQ_incoming_data |

        """
        print "Start clean mail into msg queue incoming path..."
        cmd = 'rm -rf /var/app_data/ddei/postfix/incoming/*;'
        self.exec_command_on_DDEI(cmd)
        print "Finished clean mail into msg queue incoming path."

    def clean_msgQ_active_data(self):
        """ clean mail into msg queue path
        @Param:
            path
        Return:
            None
        Example:
        | clean_msgQ_active_data |

        """
        print "Start clean mail into msg queue active path..."
        cmd = 'rm -rf /var/app_data/ddei/postfix/active/*;'
        self.exec_command_on_DDEI(cmd)
        print "Finished clean mail into msg queue active path."

    def clean_msgQ_deferred_data(self):
        """ clean mail into msg queue path
        @Param:
            path
        Return:
            None
        Example:
        | clean_msgQ_active_data |

        """
        print "Start clean mail into msg queue deferred path..."
        cmd = 'rm -rf /var/app_data/ddei/postfix/deferred/*;'
        self.exec_command_on_DDEI(cmd)
        print "Finished clean mail into msg queue deferred path."

    def clean_ddei_msgQ_env(self):
        """ Clean msgQ environment
        @Param:
            path
        Return:
            None
        Example:
        | clean_ddei_msgQ_env |

        """
        print "Start clean msgQ env..."
        cmd = 'cd /var/app_data/ddei/postfix/incoming/; rm -rf *'
        self.exec_command_on_DDEI(cmd)
        cmd = 'cd /var/app_data/ddei/postfix/active/; rm -rf *'
        self.exec_command_on_DDEI(cmd)
        cmd = 'cd /var/app_data/ddei/postfix/deferred/; rm -rf *'
        self.exec_command_on_DDEI(cmd)
        time.sleep(1)
        print "Finished clean msgQ env."



