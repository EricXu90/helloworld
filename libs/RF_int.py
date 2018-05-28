__author__ = 'Marks Shen'

import os
import conf

class RF_Int_Keywords():

    def RF_run(self, tag):
        workdir=os.path.join(conf.AUTO_ROOT,r'BDD\DDEI')
        cmd = '%s\%s %s' % (workdir, 'run.bat', tag)
        outfile = '%s\output.txt' % workdir
        ret = os.system(cmd)
        if ret != 0:
            out = open(outfile, 'r')
            raise AssertionError('Case: %s execution fail!! Err=%s' % (tag, out.read()))

