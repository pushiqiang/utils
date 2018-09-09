# -*- encoding: utf-8 -*-

import time
from logger import get_logger

logger = get_logger(name='sanic')

def test():
    logger.info('enter test')
    time.sleep(2)
    logger.info('exit test')

if __name__ == '__main__':
    while(True):
        test()
