__author__ = 'jone_zhang'

from _baselib import KeywordBase
import conf
import subprocess
import os
import shutil
import time

class MTAKeyword(KeywordBase):
    """
    This library contain all related keywords about MTA setting function
    """

    def set_next_deliver_mta(self, mta_addr=conf.LOCAL_HOST, domain='*'):
        """ Set static next delivering MTA. Default is to deliver all emails

        @Param:

            mta_addr:    the next MTA address

            domain:     the email address domain

        Return:

            None

        Example:

        | Set Next Deliver MTA | 192.168.1.1 | test.com |

        """
        transport_file = "/opt/trend/ddei/postfix/etc/postfix/transportList"
        relay_setting = "%s smtp:[%s]:25" % (domain, mta_addr)

        cmd_write_setting = "echo '%s' > %s" % (relay_setting, transport_file)
        cmd_postmap = "/opt/trend/ddei/postfix/usr/sbin/postmap %s" % transport_file
        cmd_add_postconf = "/opt/trend/ddei/postfix/usr/sbin/postconf -e 'transport_maps = hash:%s'" % transport_file

        self.exec_command_on_DDEI("postsuper -d ALL")
        self.exec_command_on_DDEI(cmd_write_setting)
        self.exec_command_on_DDEI(cmd_postmap)
        self.exec_command_on_DDEI(cmd_add_postconf)
        self.exec_command_on_DDEI("/opt/trend/ddei/postfix/usr/sbin/postfix reload")
        time.sleep(5)

    def set_empty_mta(self):
        """ Set next deliver MTA to empty

        @Param:

            None

        Return:

            None

        Example:

        | Set Empty MTA |

        """
        cmd_add_postconf = "/opt/trend/ddei/postfix/usr/sbin/postconf -e 'transport_maps ='"
        self.exec_command_on_DDEI(cmd_add_postconf)

    def start_up_local_mta(self, mta_path):
        """ Start up local fake MTA

        @Param:

            mta_path:   the path name of local MTA

        Return:

            None

        Example:

        | Start Up Local MTA | c:\fakeMTA.exe |

        """
        current_dir = os.path.abspath(os.curdir)

        for f in os.listdir(current_dir):
            f1 = os.path.join(current_dir,f)
            if os.path.isdir(f1) and f.isdigit():
                shutil.rmtree(os.path.join(current_dir, f))
                
        time.sleep(5)

        cmd_start = "%s -P 25 -S" % mta_path
        print cmd_start
        self.mta_process = subprocess.Popen(cmd_start)

    def shut_down_local_mta(self):
        """ Shut down local MTA process and also delete old received emails

        @Param:

            None

        Return:

            None

        Example:

        | Shut Down Local MTA |

        """
        if hasattr(self, 'mta_process'):
            #self.mta_process.terminate()
            self.mta_process.kill()

    def get_email_from_local_mta(self):
        """ Return the path of received email by local MTA

        @Param:

            None

        Return:

            The email path name; if no emails, return None

        Example:

        | ${email_path}= | Get Email From Local MTA |

        """
        
        
        current_dir = os.path.abspath(os.curdir)

        for f in os.listdir(current_dir):
            f1 = os.path.join(current_dir,f)
            if os.path.isdir(f1) and f.isdigit():
                for (p, d, fn) in os.walk(os.path.join(current_dir, f)):
                    for file in fn:
                        if file.find('.eml') > 0:
                            return os.path.join(p, file)

        return None

    def get_email_list_from_local_mta(self):
        """ Return the path of received email by local MTA

        @Param:

            None

        Return:

            The email path name; if no emails, return None

        Example:

        | ${email_path}= | Get Email From Local MTA |

        """
        current_dir = os.path.abspath(os.curdir)
        print "current dir is: ", current_dir
        mail_list=[]

        for f in os.listdir(current_dir):
            if os.path.isdir(f) and f.isdigit():
                for (p, d, fn) in os.walk(os.path.join(current_dir, f)):
                    for file in fn:
                        if file.find('.eml') > 0:
                            mail_list.append(os.path.join(p, file))
        
        return mail_list
