# -*- coding: utf-8 -*-
# @Date    : 2015-04-10 16:30:51
# @Author  : Todd Tong (todd_tong@trendmicro.com.cn)
# @Link    : http://www.trendmicro.com
# @Version : 0.1

import os
import sys

#=============================
# Constants variables
#=============================
# Unit: second
IMPLICIT_WAIT_TIME = 10
EXPLICIT_WAIT_TIME = 100

# Directory where auto download the file to when click <a href='...' /> link on web console.
DOWNLOAD_DIR = os.path.abspath(os.path.join(os.path.basename(sys.argv[0]), '../../testdata/'))

#=============================
# Constants Strings
#=============================
SAVE_SUCCESS = "Saved successfully."
SELECT_OPTION_OF_INVALID_PASSWORD = "Invalid or duplicate"
SELECT_OPTION_OF_TO_BE_IMPORTED = "To be Imported"
SELECT_OPTION_OF_ALL = "All items"
ERROR_MESSAGE = ""