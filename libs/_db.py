__author__ = 'jone_zhang'

from _baselib import KeywordBase
import time
import os
import conf

class DatabaseKeywords(KeywordBase):
    """
    This library contain all related keywords about Database/Log function
    """

    def import_test_db_data(self, data_file):
        """ Import Test Aggr DB Data

        @Param:

            data_file:    the data file name by sql file format

        Return:

            None

        Example:

        | Import Test DB Data | aggr_ip.sql |

        """
        local_db_data_dir = os.path.join(conf.TEST_DATE_DIR, 'db')
        self.upload_file_to_DDEI(os.path.join(local_db_data_dir, data_file), '/root/%s' % data_file)

        cmd_import_data = conf.EXE_DB_SQL_FILE % data_file
        self.ssh_conn.execute_command(cmd_import_data)

    def do_db_log_aggregation(self):
        """ Trigger DB Log Aggregation

        @Param:

            None

        Return:

            None

        Example:

        | Do DB Log Aggregation |

        """
        self.ssh_conn.execute_command(conf.DO_AGGR_ACTION)

    def generate_threat_type_log_from(self, log_file):
        """ Generate Test Log Data

        @Param:

            log_file:   the local test log file name

        Return:

            None

        Example:

        | Generate Threat Type Log From | threattype_2.log |

        """
        local_db_data_dir = os.path.join(conf.TEST_DATE_DIR, 'db')
        self.upload_file_to_DDEI(os.path.join(local_db_data_dir, log_file), '/root/%s' % log_file)

        cmd_append_log = conf.CMD_APPEND_LOG % log_file
        self.ssh_conn.execute_command(cmd_append_log)

        self.ssh_conn.execute_command(conf.CMD_RESTART_MANAGER)
        time.sleep(20)

    def threat_type_should_be_correct(self, threat_type):
        """ Check DB Log Threat Type Value Should Be Correct

        @Param:

            threat_type:   the threat type value

        Return:

            None

        Example:

        | Threat Type Should Be Correct |

        """
        sql_type_condition = "threat_type=%s" % threat_type
        cnt = self.get_log_count_on_DDEI(conf.TABLE_POLICY_EVENT, sql_type_condition)

        if int(cnt) == 0:
            raise AssertionError("The specified threat type log count is: 0")

    def wait_until_table_exist_log(self, table_name, wait_sec=300):
        """ Wait until there is logs in specified table

        @Param:

            table_name:   the specified db table name

            wait_sec:   the waiting timeout seconds

        Return:

            None

        Example:

        | Wait Until Table Exist Log | tb_policy_event |

        """
        retry_cnt = 0

        while retry_cnt <= int(wait_sec):
            log_cnt = self.get_log_count_on_DDEI(table_name)
            if int(log_cnt) > 0:
                return
            retry_cnt += 1
            time.sleep(1)

        raise AssertionError("There is NO logs found in table '%s'" % table_name)
    def wait_until_table_exist_log_with_condition(self, table_name, condition, wait_sec=300):
        """ Wait until there is logs in specified table
        @Param:
            table_name:   the specified db table name
            wait_sec:   the waiting timeout seconds
        Return:
            None
        Example:
        | Wait Until Table Exist Log With Condition| tb_policy_event | condition
        """
        retry_cnt = 0
        while retry_cnt <= int(wait_sec):
            log_cnt = self.get_log_count_on_DDEI(table_name, condition)
            if int(log_cnt) > 0:
                return
            retry_cnt += 1
            time.sleep(1)
        raise AssertionError("There is NO logs found in table '%s'" % table_name)
