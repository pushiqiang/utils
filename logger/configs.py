# logger config
LOGGER_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    },
    'loggers': {
        # 默认配置, 通过logging.getLogger(__name__)拿到的logger配置
        '': {
            'handlers': [
                'console',
            ],
            'level': 'DEBUG',
            'propagate': True,
        },
        # 自定义, 通过logging.getLogger('flask')拿到的logger配置
        # propagate设置为False，关闭向上级logger传递，否则会出现重复输出
        'flask': {
            'handlers': [
                'console',
            ],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic',
            'stream': 'ext://sys.stdout'
        },
    },
    'formatters': {
        'generic': {
            'format':
            '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
            'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
            'class': 'logging.Formatter'
        }
    }
}
