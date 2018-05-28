__author__ = 'jone_zhang'

from _baselib import KeywordBase
import time
import os
import conf

class ScannerKeywords(KeywordBase):
    """
    This library contain all related keywords about Scanner function
    """

    def email_should_be_quarantined(self):
        """ Check db log that email is quarantined

        @Param:

            None

        Return:

            None

        Example:

        | Email Should Be Quarantined |

        """
        time.sleep(5)
        cmd = "%s 'select %s from %s limit 1'" % (conf.PSQL_EXE, 'act_quarantined', 'tb_policy_event_total')
        value = self.ssh_conn.execute_command(cmd)
        print "Action: %s" % value
        if (not value.strip()) or (int(value.strip()) != 1):
            raise AssertionError("No emails found to be quarantined.")

    def email_should_be_analyzed(self):
        """ Check db log that email is analyzed

        @Param:

            None

        Return:

            None

        Example:

        | Email Should Be Analyzed |

        """
        time.sleep(5)
        cmd = "%s 'select %s from %s limit 1'" % (conf.PSQL_EXE, 'act_analyzed', 'tb_policy_event_total')
        value = self.ssh_conn.execute_command(cmd)
        print "Action: %s" % value
        if (not value.strip()) or (int(value.strip()) != 1):
            task_cnt_cmd = "%s 'select %s from %s'" % (conf.PSQL_EXE, 'count(*)', 'tb_sandbox_tasks_history')
            cnt = self.ssh_conn.execute_command(task_cnt_cmd)
            print "Analysis Task History Count: %s" % cnt
            if int(cnt) == 0:
                raise AssertionError("No emails found to be analyzed.")
				
    def email_should_be_deleted(self):
        """ Check db log that email is deleted

        @Param:

            None

        Return:

            None

        Example:

        | Email Should Be Deleted |

        """
        time.sleep(5)
        cmd = "%s 'select %s from %s limit 1'" % (conf.PSQL_EXE, 'act_deleted', 'tb_policy_event_total')
        value = self.ssh_conn.execute_command(cmd)
        if (not value.strip()) or (int(value.strip()) != 1):
            raise AssertionError("No emails found to be deleted.")

    def email_should_be_delivered(self):
        """ Check db log that email is delivered

        @Param:

            None

        Return:

            None

        Example:

        | Email Should Be Delivered |

        """
        time.sleep(5)
        cmd = "%s 'select %s from %s limit 1'" % (conf.PSQL_EXE, 'act_delivered', 'tb_policy_event_total')
        value = self.ssh_conn.execute_command(cmd)
        if (not value.strip()) or (int(value.strip()) != 1):
            raise AssertionError("No emails found to be delivered.")

    def add_policy_exception(self, exp_type, item):
        """ Add File or URL Exception List in Policy Setting

        @Param:

            exp_type:    the policy exception type - only support file and url

            item:        the added exception item value

        Return:

            None

        Example:

        | Add Policy Exception | 3 | www.baidu.com |

        """
        total_cnt = self.ssh_conn.execute_command(conf.EXCEPTION_COUNT).strip()
        add_cmd = ""

        if exp_type.strip() == conf.FILE_EXCEPTION_TYPE:
            add_cmd = conf.ADD_EXCEPTION_CMD % (str(int(total_cnt) + 1), item, conf.FILE_EXCEPTION_TYPE)
        elif exp_type.strip() == conf.URL_EXCEPTION_TYPE:
            add_cmd = conf.ADD_EXCEPTION_CMD % (str(int(total_cnt) + 1), item, conf.URL_EXCEPTION_TYPE)
        elif exp_type.strip() == conf.SENDER_EXCEPTION_TYPE:
            add_cmd = conf.ADD_SENDER_EXCEPTION_CMD % item
        elif exp_type.strip() == conf.RCPT_EXCEPTION_TYPE:
            add_cmd = conf.ADD_RCPT_EXCEPTION_CMD % item
        elif exp_type.strip() == conf.XHEADER_EXCEPTION_TYPE:
            add_cmd = conf.ADD_XHEADER_EXCEPTION_CMD % item
        else:
            print "The Added Exception Item Is Invalid"
            return

        self.ssh_conn.execute_command(add_cmd)
        self.ssh_conn.execute_command(conf.RELOAD_POLICY_CMD)

    def restore_policy_exception(self):
        """ Restore policy exception setting to default

        @Param:

            None

        Return:

            None

        Example:

        | Restore Policy Exception |

        """
        self.ssh_conn.execute_command(conf.CLEAR_URL_FILE_EXCPETION_CMD)
        self.ssh_conn.execute_command(conf.ADD_RCPT_EXCEPTION_CMD % '')
        self.ssh_conn.execute_command(conf.ADD_SENDER_EXCEPTION_CMD % '')
        self.ssh_conn.execute_command(conf.ADD_XHEADER_EXCEPTION_CMD % '')
        self.ssh_conn.execute_command(conf.RELOAD_POLICY_CMD)

    def set_policy_action(self, severity, action):
        """ Set policy action for different severity

        @Param:

            None

        Return:

            None

        Example:

        | Set Policy Action | ${HIGH} | ${Action_Pass} |

        """
        severity_xml_map = {
            conf.HIGH: "action_high_risk",
            conf.MEDIUM: "action_medium_risk",
            conf.LOW: "action_low_risk",
            conf.UNSCANNABLE_ENABLE: "custom_action_unscannable_archive",
            conf.UNSCANNABLE: "action_unscannable_archive"
        }
        xml_item = severity_xml_map[int(severity)]

        cmd_set_action = "sed -i -e '/<%s>/d' -e '/<policy>/a <%s>%s</%s>' %s" % (xml_item, xml_item, action, xml_item, conf.POLICY_SETTING_FILE)

        self.exec_command_on_DDEI(cmd_set_action)
        self.exec_command_on_DDEI(conf.RELOAD_POLICY_CMD)

    def add_predefined_password(self, password):
        """ Set predefined password for scanner and u-sandbox usage

        @Param:

            password:   the predefined password

        Return:

            None

        Example:

        | Add Predefined Password | 11111 |

        """
        cmd_add_for_scanner = "sed -i -e '/<passwords/d' -e '/<config>/a <passwords><password><![CDATA[%s]]></password></passwords>' %s" % (password, conf.SANDBOX_FILTER_FILE)
        cmd_add_for_va = '%s "%s"' % (conf.CMD_USBX_SET_PSWD, password)
        cmd_notify_pwd_analyzer = "sudo kill -SIGHUP $(ps -ef | grep -v grep | grep passwordAnalyzer.pyc | awk '{ print $2 }')"

        self.exec_command_on_DDEI(cmd_add_for_scanner)
        self.exec_command_on_DDEI(conf.RELOAD_POLICY_CMD)
        self.exec_command_on_DDEI(cmd_notify_pwd_analyzer)
        self.exec_command_on_DDEI(cmd_add_for_va)

    def clear_predefined_password(self):
        """ Clear predefined password for scanner and u-sandbox usage

        @Param:

            None

        Return:

            None

        Example:

        | Clear Predefined Password |

        """
        self.add_predefined_password('')
        self.exec_command_on_DDEI(conf.CMD_USBX_CLEAR_PSWD)

    def add_regx_password(self, password, pre="", post="", ignore_case=0):
        """ Add reg password

        @Param:

            pre:    pre_condition

            password:   password_condition

            post:   post_condition

            ignore_case:    ignore case

        Return:

            None

        Example:

        | Add Regx Password | 111 | password: | aa | 0 |

        """
        password_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
                                    <custom_regex>
                                     <rule>
                                      <rule_name>rule name1</rule_name>
                                      <pattern>
                                       <pre_condition><![CDATA[%s]]></pre_condition>
                                       <password_condition><![CDATA[%s]]></password_condition>
                                       <post_condition><![CDATA[%s]]></post_condition>
                                      </pattern>
                                      <flags>
                                       <IGNORECASE>%s</IGNORECASE>
                                      </flags>
                                     </rule>
                                    </custom_regex>""" % (pre, password, post, ignore_case)

        generate_xml_cmd = "echo '%s' > /opt/trend/ddei/config/password_analyse.xml" % password_xml_content
        cmd_notify_pwd_analyzer = "sudo kill -SIGHUP $(ps -ef | grep -v grep | grep passwordAnalyzer.pyc | awk '{ print $2 }')"

        self.exec_command_on_DDEI(generate_xml_cmd)
        self.exec_command_on_DDEI(cmd_notify_pwd_analyzer)

    def set_custom_subject_tag(self, severity, tag):
        """ Set custom subject tag string for policy action setting

        @Param:

            severity:   the email severity type ( Include: high, medium, low )

            tag:    the custom specified tag string

        Return:

            None

        Example:

        | Set Custom Subject Tag | high | test subject tag |

        """
        if cmp(severity, "unscannable")==0:
            cmd_add_tag = "sed -i -e '/subject_%s_archive/d' -e '/<message_tags>/a <subject_%s_archive>\[%s\]<\/subject_%s_archive>' %s" % (severity, severity, tag, severity, conf.POLICY_SETTING_FILE)
        else:
            cmd_add_tag = "sed -i -e '/subject_%s_risk/d' -e '/<message_tags>/a <subject_%s_risk>\[%s\]<\/subject_%s_risk>' %s" % (severity, severity, tag, severity, conf.POLICY_SETTING_FILE)

        self.exec_command_on_DDEI(cmd_add_tag)
        self.exec_command_on_DDEI(conf.RELOAD_POLICY_CMD)

    def set_custom_end_stamp(self, end_stamp):
        """ Set custom end stamp added in scanned email body

        @Param:

            end_stamp:    the custom specified end stamp in email body

        Return:

            None

        Example:

        | Set Custom End Stamp | test end stamp |

        """
        cmd_add_stamp = "sed -i -e '/end_stamp/d' -e '/<message_tags>/a <end_stamp>%s<\/end_stamp>' %s" % (end_stamp, conf.POLICY_SETTING_FILE)

        self.exec_command_on_DDEI(cmd_add_stamp)
        self.exec_command_on_DDEI(conf.RELOAD_POLICY_CMD)

    def set_custom_file_replacement(self, replacement):
        """ Set custom file replacement for stripped file

        @Param:

            replacement:    the file path in local machine

        Return:

            None

        Example:

        | Set Custom File Replacement | c:\123.txt |

        """
        if not os.path.exists(replacement):
            raise AssertionError("Can NOT find replacement file: %s" % replacement)

        filename = os.path.basename(replacement)
        self.upload_file_to_DDEI(replacement, '/opt/trend/ddei/config/file_replacement/%s' % filename)
        cmd_change_folder_params= "chown ddei:ddei /opt/trend/ddei/config/file_replacement"
        self.exec_command_on_DDEI(cmd_change_folder_params)
        cmd_change_params = "chown ddei:ddei /opt/trend/ddei/config/file_replacement/%s" % filename
        self.exec_command_on_DDEI(cmd_change_params)
        cmd_add_replacement = "sed -i -e '/file_replacement/d' -e '/<message_tags>/a <file_replacement>/opt/trend/ddei/config/file_replacement/%s<\/file_replacement>' %s" % (filename, conf.POLICY_SETTING_FILE)
        self.exec_command_on_DDEI(cmd_add_replacement)
        self.exec_command_on_DDEI(conf.RELOAD_POLICY_CMD)

    def set_notify_setting(self, severity, is_notify):
        """ Set notify setting for policy action setting

        @Param:

            severity:   the email severity type ( Include: high, medium, low, unscannable )

            is_notify:    is this kind of severity should set notification (Include: 1, 0; 1 means notify, 0 means not to notify)

        Return:

            None

        Example:

        | Set notify setting | high | yes |

        """
        if cmp(severity, "unscannable")==0:
            cmd_notify_setting = "sed -i -e '/notify_recipients_%s_archive/d' -e '/<policy>/a <notify_recipients_%s_archive>%s<\/notify_recipients_%s_archive>' %s" % (severity, severity, is_notify, severity, conf.POLICY_SETTING_FILE)
        else:
            cmd_notify_setting = "sed -i -e '/notify_recipients_%s_risk/d' -e '/<policy>/a <notify_recipients_%s_risk>%s<\/notify_recipients_%s_risk>' %s" % (severity, severity, is_notify, severity, conf.POLICY_SETTING_FILE)

        self.exec_command_on_DDEI(cmd_notify_setting)
        self.exec_command_on_DDEI(conf.RELOAD_POLICY_CMD)

    def update_tmase_pattern(self, rule_path):
        try:
            self.exec_command_on_DDEI('cd /opt/trend/ddei/lib/pattern/tmase; zip -r backup_pattern.zip tm*; rm -rf tm*')
        except:
            raise AssertionError("can't backup tmase pattern")
        
        pattern_files = os.listdir(rule_path)
        for file in pattern_files:
            print os.path.join(rule_path, file)
            self.ssh_conn.put_file(os.path.join(rule_path, file), '/opt/trend/ddei/lib/pattern/tmase')
        original_process_id = self.get_process_pid_on_ddei('scanner')
        print 'original_process_id:',original_process_id
        print type(original_process_id)
        time.sleep(1)
        self.exec_command_on_DDEI('/opt/trend/ddei/script/S99IMSS restart')
        self.wait_until_process_restart('scanner', original_process_id)

    def restore_tmase_pattern(self):
        try:
            self.exec_command_on_DDEI('cd /opt/trend/ddei/lib/pattern/tmase; rm -rf tm*; unzip backup_pattern.zip; rm -rf backup_pattern.zip')
        except:
            raise AssertionError("can't restore tmase pattern")
            
        original_process_id = self.get_process_pid_on_ddei('scanner')
        self.exec_command_on_DDEI('/opt/trend/ddei/script/S99IMSS restart')
        self.wait_until_process_restart('scanner', original_process_id) 




