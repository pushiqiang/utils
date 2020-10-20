import redis
from settings import REDIS_CONFIG


def get_redis_db():
    if REDIS_CONFIG['password']:
        return redis.StrictRedis(host=REDIS_CONFIG['host'], port=REDIS_CONFIG['port'],
                                 password=REDIS_CONFIG['password'])
    else:
        return redis.StrictRedis(host=REDIS_CONFIG['host'], port=REDIS_CONFIG['port'])


redis_db = get_redis_db()


class RedisLock(object):
    """利用 redis 实现的锁
    Usages:
        with RedisLock('your_lock_key'):
            do_something()
    """

    def __init__(self, key, value=None, ttl=None):
        """
        :param key: string
        :param value:
        :param ttl: int
        """
        self.key = key
        self.value = value
        self.ttl = ttl
        self.is_acquired = False

    def acquire(self):
        """设置锁"""
        exec_result = redis_db.set(self.key, self.value, ex=self.ttl, nx=True)
        if exec_result is None:
            self.is_acquired = False
        elif exec_result is True:
            self.is_acquired = True
        else:
            # 不应出现的返回值, 抛出错误
            raise Exception('Not expected result value of '
                            'redis_db.set(): {!s}'.format(exec_result))

    def release(self):
        """释放锁"""
        redis_db.delete(self.key)

    def __enter__(self):
        """使用 context manager"""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时判断如果设置锁成功, 才释放锁"""
        if self.is_acquired:
            self.release()
