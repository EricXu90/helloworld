__author__ = 'jone_zhang'

from _baselib import KeywordBase
import time

class MsgTraceKeyword(KeywordBase):
    """
    This library contain all related keywords about update function: Message Tracing
    """

    def wait_until_exist_msg_tracing_log(self):
        """ Wait until there is message tracing log in db

        @Param:

            None

        Return:

            None

        Example:

        | Wait Until Exist Msg Tracing Log |

        """
        retry = 1
        sql_query_cnt = "select count(*) from tb_msg_tracing"

        while retry <= 300:
            cnt = self.exec_sql_command_on_DDEI(sql_query_cnt)
            if int(cnt) != 0:
                return
            time.sleep(1)
            retry += 1

        raise AssertionError("There is NO message tracing log generated.")