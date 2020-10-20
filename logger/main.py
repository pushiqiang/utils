# -*- encoding: utf-8 -*-
import logging
import logging.config

import configs

# 应用初始化时加载logger配置
logging.config.dictConfig(configs.LOGGER_CONFIG)

# 各文件使用
logger = logging.getLogger(__name__)

logger.info('teste')
try:
    do_something()
except Exception as e:
    logger.error('error', exc_info=True)
    process_error()
