#encoding=utf-8
import logging
import datetime
import os


def init():
    log_dir = './log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s | %(message)s',
                        datefmt='%Y-%m-%d %A %H:%M:%S',
                        filename="%s/auto_%s.log"%(log_dir, gettime()['date']),    
                        filemode='a')
    console = logging.StreamHandler()                  # 定义console handler  
    console.setLevel(logging.INFO)                     # 定义该handler级别  
    formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s | %(message)s')  #定义该handler格式  
    console.setFormatter(formatter)  
    # Create an instance  
    logging.getLogger().addHandler(console)

def loginfo(msg):
    logging.info(msg)

def logerror(msg):
    logging.error(msg)

def logwarning(msg):
    logging.warning(msg)

def gettime():
    now = datetime.datetime.now()
    return {'date':now.strftime('%Y%m%d'), 'time':now.strftime('%H:%M:%S')}

