# -*- coding: utf-8 -*-
# @Date    : 2015-03-26 19:14:07
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : $Id$

import os
from web.pageobjects.mailsettingspage import MailSettings

class MailSettingsKeywords(object):
    """ """
    def __init__(self):
        super(MailSettingsKeywords, self).__init__()
        self.mail_settings = MailSettings()