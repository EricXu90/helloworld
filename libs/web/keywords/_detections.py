# -*- coding: utf-8 -*-
# @Date    : 2015-04-02 15:40:53
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : www.trendmicro.com
# @Version : 0.1

import os
from web.pageobjects.detectionspage import Detections

class DetectionsKeywords(object):
    """This class encapsulates possible operations on Detections page
       and explore the keywords to RF.
    """
    def __init__(self):
        super(DetectionsKeywords, self).__init__()
        self.detection_page = Detections()

    def result_should_have_value(self, msg):
        """ Verify if the page have the specific message
        @Params:
            msg: message which needs to be found
        @Return:
            None
        @Exception:
            AssertionError
        Example:
        | Result Should Have Value | test@trend.com |
        """
        ret = self.detection_page.result_should_have_value(msg)
        # not exist
        if not ret:
            raise AssertionError("Detections page doesn't have the string [%s]" % msg)

