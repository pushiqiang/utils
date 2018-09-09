# -*- coding: utf8 -*-

import os
import logging
from logging.handlers import TimedRotatingFileHandler

# 日志打印格式
# eg: '2018-09-09 11:04:43 - your_logger_name - [main.py:7] INFO : Log info'
LOG_FORMAT = '%(asctime)s - %(name)s - [%(filename)s:%(lineno)s] %(levelname)s : %(message)s'

# 默认每周一分表
LOG_TIME_ROTATING_CONFIG = {
    'filename': 'logs/system',
    'when': 'W0',
    'interval': 1,
    'backupCount': 8
}

# filename 是输出日志文件名的前缀，比如log/myapp
# when 是一个字符串的定义如下：
#   “S”: Seconds;
#   “M”: Minutes;
#   “H”: Hours;
#   “D”: Days;
#   “W”: Week day (0=Monday); 'W0'-'W6' ， 周一至周日
#   “midnight”: 每天的凌晨
# interval : 指等待多少个单位when的时间后，Logger会自动重建文件
# backupCount : 保留日志个数。默认的0是不会自动删除掉日志
# 日志文件后缀，切分后日志文件名的时间格式 默认 filename + "." + suffix
# suffxi默认情况
# ‘S’:  suffix=”%Y-%m-%d_%H-%M-%S”,
# ‘M’:  suffix=”%Y-%m-%d_%H-%M”
# ‘H’:  suffix=”%Y-%m-%d_%H”
# ‘D’:  suffxi=”%Y-%m-%d”
# ‘MIDNIGHT’:”%Y-%m-%d”
# ‘W’:”%Y-%m-%d”


log_parent_dir = os.path.dirname(os.path.abspath(LOG_TIME_ROTATING_CONFIG['filename']))
if not os.path.exists(log_parent_dir):
    # 若上级目录不存在，创建
    os.makedirs(log_parent_dir)

formatter = logging.Formatter(LOG_FORMAT)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

# 创建TimedRotatingFileHandler对象
file_handler = TimedRotatingFileHandler(
    filename=LOG_TIME_ROTATING_CONFIG['filename'],
    when=LOG_TIME_ROTATING_CONFIG['when'],
    interval=LOG_TIME_ROTATING_CONFIG['interval'],
    backupCount=LOG_TIME_ROTATING_CONFIG['backupCount']
)
file_handler.suffix = file_handler.suffix + '.log'
file_handler.setFormatter(formatter)


def get_logger(name, use_rotating=False):
    """
    获取logger对象
    如果多次以同一个name获取logger，那么返回的都是同一个logger。
    :param name:
    :param use_file_storage: 是否使用文件存储
    :return:
    """
    my_logger = logging.getLogger(name)

    if use_rotating:
        my_logger.addHandler(file_handler)

    return my_logger
