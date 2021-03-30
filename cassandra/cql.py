"""
Usages:
    # configs.py
    class Config:
        CASSANDRA_NODES = ['cassandra']
        CASSANDRA_USER = 'cassandra'
        CASSANDRA_KEYSPACE = 'test'
        CASSANDRA_REPLICATION_FACTOR = 1

    # app.py
    from utils.cassandra.cql import CassandraCqlClient
    from configs import Config

    CassandraCqlClient().register_cassandra_cql(Config)

    # views.py
    from cassandra.query import BatchStatement, BatchType
    from utils.cassandra import cql

    result = cql.session.execute(cql.session.prepare("SELECT * FROM user WHERE user_id=? limit 1"), [user_id]).one()

    query = await cql.session.prepare_future("SELECT * FROM user WHERE user_id=? limit 1")
    result2 = await cql.session.execute_future(query, [user_id]).one()

    batch = BatchStatement(batch_type=BatchType.UNLOGGED)
    insert_statement = cql.session.prepare("INSERT INTO user (user_id, name, age, email) VALUES (?, ?, ?, ?)")
    for user in users:
        batch.add(insert_statement, *user)

    cql.session.execute(batch)

"""

import logging

# https://github.com/aio-libs/aiocassandra
from aiocassandra import aiosession
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

logger = logging.getLogger(__name__)

# cassandra session 初始化为全局单例
session = None


class AttrDict(dict):
    """字典类变成属性类， 通过config.attr方式访问
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class CassandraCqlClient:
    def __init__(self, config):
        self.config = AttrDict(config) if isinstance(config, dict) else config
        # 密码认证
        # auth = PlainTextAuthProvider(username=self.config.CASSANDRA_USER,
        #                              password=self.config.CASSANDRA_PASSWORD)
        # cluster = Cluster(self.config.CASSANDRA_NODES, auth_provider=auth)
        self.cluster = Cluster(self.config.CASSANDRA_NODES)

    def setup_cql(self):
        global session
        session = cluster.connect(self.config.CASSANDRA_KEYSPACE,
                                  wait_for_all_pools=True)
        aiosession(session)
        logger.info('CQL session prepared')

    def register_cassandra_cql(self):
        """启动 Cassandra cql
        """
        self.setup_cql()


def shutdown():
    """关闭cassandra session
    """
    session.shutdown()
    session.cluster.shutdown()
    session = None


def drop_keyspace(keyspace):
    """删除keyspace, 单元测试时使用
    """
    session.execute('DROP KEYSPACE IF EXISTS %s' % keyspace, timeout=60)
