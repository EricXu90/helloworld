__author__ = 'jone_zhang'

from _baselib import KeywordBase
import time
import os
import conf

class AlertKeywords(KeywordBase):
    """
    This library contain all related keywords about Alert function
    """

    def _config_alert_rule_enable(self, rule_id, enable_value):
        """ Set the enable/disable status for specific alert rule

        """
        self.purge_DB('ddei', 'tb_alert_triger_event')
        update_db_cmd = '%s "update %s set rule_enable=%s, rule_check_interval=1, rule_event_type=1, rule_recipents=\'bvt@test.com\', rule_threshold=1, rule_watchlist=\'%s\' where rule_id=%s and is_default=0"' % (conf.PSQL_EXE, 'tb_alert_rule_setting', enable_value, conf.MAIL_TO, rule_id)
        self.ssh_conn.execute_command(update_db_cmd)
        self.ssh_conn.execute_command(conf.CMD_RESTART_ALERT)
        time.sleep(5)

    def enable_alert_rule(self, rule_id):
        """ Enable specific alert rule

        @Param:

            rule_id:    The alert rule id

        Return:

            None

        Example:

        | Enable Alert Rule | 1 |

        """
        self._config_alert_rule_enable(rule_id, '1')

    def disable_alert_rule(self, rule_id):
        """ Disable specific alert rule

        @Param:

            rule_id:    The alert rule id

        Return:

            None

        Example:

        | Disable Alert Rule | 1 |

        """
        self._config_alert_rule_enable(rule_id, '0')

    def disable_all_alert_rules(self):
        """ Disable all alert rules


        @Param:

            None

        Return:

            None

        Example:

        | Disable All Alert Rules |

        """
        sql_disable_all_alert_rules = "update tb_alert_rule_setting set rule_enable=0 where is_default=0"
        self.exec_sql_command_on_DDEI(sql_disable_all_alert_rules)

    def can_trigger_alert_rule(self, rule_id):
        """ Check if the alert rule is triggered by querying alert event logs

        @Param:

            rule_id:    The alert rule id

        Return:

            None

        Example:

        | Can Trigger Alert Rule | 1 |

        """
        query_db_cmd = "%s 'SELECT count(*) from %s where rule_id=%s'" % (conf.PSQL_EXE, 'tb_alert_triger_event', rule_id)
        cnt = self.ssh_conn.execute_command(query_db_cmd)
        if int(cnt) == 0:
            raise AssertionError("The alert trigger event count is: 0")

    def _wait_alert_to_be_monitored(self, sleep_time=90):
        """ Wait for some time to make the alert rule event to be monitored

        """
        time.sleep(sleep_time)

    def _trigger_alert_event_rule_1(self):
        """ System: Message Delivery Queue

        """

        pass

    def _trigger_alert_event_rule_2(self):
        """ System: CPU Usage

        """
        self._wait_alert_to_be_monitored()

    def _trigger_alert_event_rule_3(self):
        """ Security: Messages Detected

        """
        self.send_one_email(mail_path=os.path.join(conf.TEST_DATE_DIR,'medium_URL.eml'))
        self._wait_alert_to_be_monitored()

    def _trigger_alert_event_rule_4(self):
        """ Security: Watchlist

        """
        self._trigger_alert_event_rule_3()

    def _trigger_alert_event_rule_5(self):
        """ System: Sandbox Stopped

        """
        self.ssh_conn.execute_command(conf.CMD_USBX_STOP)
        self._wait_alert_to_be_monitored()
        time.sleep(60)
        self.ssh_conn.execute_command(conf.CMD_USBX_START)

    def _trigger_alert_event_rule_6(self):
        """ System: Sandbox Queue

        """
        self.ssh_conn.execute_command(conf.CMD_USBX_STOP)
        self.send_one_email(mail_path=os.path.join(conf.TEST_DATE_DIR,'attach_suspicious.eml'))
        self._wait_alert_to_be_monitored()
        self.ssh_conn.execute_command(conf.CMD_USBX_START)


    def _trigger_alert_event_rule_7(self):
        """ System: Average Sandbox Processing Time

        """
        self._trigger_alert_event_rule_6()

    def _trigger_alert_event_rule_8(self):
        """ System: Disk Space

        """
        update_disk_limit_cmd = "%s 'update %s set rule_threshold=9999 where rule_id=8 and is_default=0'" % (conf.PSQL_EXE, 'tb_alert_rule_setting')
        self.ssh_conn.execute_command(update_disk_limit_cmd)
        self.ssh_conn.execute_command(conf.CMD_RESTART_ALERT)
        self._wait_alert_to_be_monitored()

    def _trigger_alert_event_rule_9(self):
        """ System: Detection Surge

        """
        self._trigger_alert_event_rule_3()

    def _trigger_alert_event_rule_10(self):
        """ System: Processing Surge

        """
        self._trigger_alert_event_rule_3()

    def _trigger_alert_event_rule_11(self):
        """ System: Service Stopped

        """
        update_manager_monitor = '''%s "UPDATE tb_global_setting set value=0.1 where name ='ScannerSvcMin'"''' % conf.PSQL_BIN
        self.ssh_conn.execute_command(update_manager_monitor)
        self.ssh_conn.execute_command(conf.CMD_RESTART_MANAGER)

        hide_config = "mv /opt/trend/ddei/config/sandbox_filter.xml /opt/trend/ddei/config/sandbox_filter.xml.bak"
        self.ssh_conn.execute_command(hide_config)
        self.ssh_conn.execute_command(conf.CMD_RESTART_SCANNER)

        self._wait_alert_to_be_monitored()

        restore_config = "mv /opt/trend/ddei/config/sandbox_filter.xml.bak /opt/trend/ddei/config/sandbox_filter.xml"
        self.ssh_conn.execute_command(restore_config)
        self.ssh_conn.execute_command(conf.CMD_RESTART_SCANNER)

    def _trigger_alert_event_rule_12(self):
        """ System: Unreachable Relay MTAs

        """
        limit_cnt = 15
        for i in range(limit_cnt):
            self.send_one_email(mail_path=os.path.join(conf.TEST_DATE_DIR,'normal.eml'))

        self._wait_alert_to_be_monitored()

    def _trigger_alert_event_rule_13(self):
        """ System: Update Failed

        """
        pass

    def _trigger_alert_event_rule_14(self):
        """ System: Update completed

        """
        pass

    def _trigger_alert_event_rule_15(self):
        """ System: License Expiration

        """
        self._wait_alert_to_be_monitored()

    def trigger_alert_event_of_rule(self, rule_id):
        """ Trigger a alert event for specific rule

        @Param:

            rule_id:    The alert rule id

        Return:

            None

        Example:

        | Trigger Alert Event Of Rule | 1 |

        """
        trigger_event_rule_func = getattr(self, "_trigger_alert_event_rule_%s" % rule_id, None)

        if callable(trigger_event_rule_func):
            trigger_event_rule_func()
