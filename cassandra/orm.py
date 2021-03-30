"""
Usages:
    # configs.py
    class Config:
        CASSANDRA_NODES = ['cassandra']
        CASSANDRA_USER = 'cassandra'
        CASSANDRA_KEYSPACE = 'test'
        CASSANDRA_REPLICATION_FACTOR = 1

    # models.py
    from cassandra.cqlengine import columns
    from cassandra.cqlengine.models import Model

    class Example(Model):
        # Fixme: 删掉 example
        __table_name__ = 'example'

        id = columns.UUID(primary_key=True)
        created_at = columns.DateTime(default=datetime.utcnow)
        example_field = columns.Text()

    # sync_db.py
    import models

    db_management = CassandraManagement(config)
    db_management.sync_db(models)

    # main.py
    from cassandra.cqlengine.query import conn
    from utils.cassandra.orm import CassandraManagement

    db_management = CassandraManagement(config)
    db_management.connect()

    session = conn.get_session()
    cql = 'SELECT * FROM example WHERE id=%s'

    result = await session.execute_future(cql, [uuid.UUID(u_id)])
    result2 = session.execute(cql, [uuid.uuid4()])

    obj = models.Example.create(id=uuid.uuid4(), example_field='xxx')
    results = models.Example.filter(id=obj.id)

"""
import logging

import inspect

# https://github.com/aio-libs/aiocassandra
from aiocassandra import aiosession
from cassandra import AlreadyExists, ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster, NoHostAvailable
from cassandra.cqlengine import connection
from cassandra.cqlengine import management
from cassandra.cqlengine.models import Model
from cassandra.cqltypes import UserType
from cassandra.query import dict_factory


logger = logging.getLogger(__name__)


class AttrDict(dict):
    """字典类变成属性类， 通过config.attr方式访问
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


def get_models(app_module, keyspace):
    """获取某个模块下所有的 cqlengine model
    """
    table_models, user_type_models = list(), list()
    for name, model in inspect.getmembers(app_module):
        # 判断是否 table
        is_table_class = (inspect.isclass(model) and issubclass(model, Model)
                          and not model.__abstract__)

        if is_table_class:
            # 判断 model 是否有 keyspace
            if model.__keyspace__ is None \
                    or model.__keyspace__ == keyspace:
                table_models.append(model)

        # 判断是否 user type
        is_user_type_class = (inspect.isclass(model)
                              and issubclass(model, UserType))
        if is_user_type_class:
            user_type_models.append(model)

    return table_models, user_type_models


class Singleton(type):
    """单例元类, 用于创建单例对象
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CassandraManagement(metaclass=Singleton):
    """Cassandra会话管理器类, 单例: 使用 DatabaseManagement() 得到的永远是一个对象
    """
    def __init__(self, config, timeout=10):
        self.timeout = timeout
        self._keyspace = None
        self.db_session = None
        self._is_connected = False
        self.config = AttrDict(config) if isinstance(config, dict) else config
        self.replication_factor = self.config.CASSANDRA_REPLICATION_FACTOR

    @property
    def keyspace(self):
        if self._keyspace is None:
            self._keyspace = self.config.CASSANDRA_KEYSPACE
        return self._keyspace

    @keyspace.setter
    def keyspace(self, new_keyspace):
        self._keyspace = new_keyspace

    def connect(self):
        """连接数据库
        """
        if self._is_connected:
            return

        # 密码认证
        # auth = PlainTextAuthProvider(username=self.config.CASSANDRA_USER,
        #                              password=self.config.CASSANDRA_PASSWORD)
        # cluster = Cluster(self.config.CASSANDRA_NODES, auth_provider=auth)

        cluster = Cluster(self.config.CASSANDRA_NODES)
        try:
            self.db_session = cluster.connect()
        except NoHostAvailable:
            # 再尝试连接一次
            self.db_session = cluster.connect()
        self.db_session.set_keyspace(self.keyspace)
        self.db_session.row_factory = dict_factory
        self.db_session.default_timeout = self.timeout
        self.db_session.default_consistency_level = \
            ConsistencyLevel.LOCAL_QUORUM

        connection.set_session(self.db_session)

        aiosession(self.db_session)

        self._is_connected = True

    def disconnect(self):
        """断开连接
        """
        if not self._is_connected:
            return
        self.db_session.cluster.shutdown()
        self.db_session = None
        self._is_connected = False

    def create_keyspace_if_not_exist(self):
        """
        创建 Cassandra 的 keyspace
        :return:
        """
        # 单机房的复制策略, 用于开发和测试环境
        create_keyspace_cql = (
            'CREATE KEYSPACE %s WITH replication = '
            "{'class': 'SimpleStrategy', 'replication_factor': '%s'} "
            'AND durable_writes = true;' %
            (self.keyspace, self.replication_factor))

        # auth = PlainTextAuthProvider(username=self.config.CASSANDRA_USER,
        #                              password=self.config.CASSANDRA_PASSWORD)
        # cluster = Cluster(self.config.CASSANDRA_NODES, auth_provider=auth)
        cluster = Cluster(self.config.CASSANDRA_NODES)
        try:
            db_session = cluster.connect()
        except NoHostAvailable:
            # 再尝试连接一次
            db_session = cluster.connect()

        try:
            db_session.execute(create_keyspace_cql)
        except AlreadyExists:
            return False
        return True

    def sync_db(self, *model_modules):
        """同步数据库
        eg: sync_db(module_1, module_2)
        """
        self.create_keyspace_if_not_exist()

        if not self._is_connected:
            self.connect()

        # 同步所有 table model 和 usertype model
        table_models, user_type_models = [], []
        for model_module in model_modules:
            _table_models, _user_type_models = get_models(
                model_module, self.keyspace)
            table_models.extend(_table_models)
            user_type_models.extend(_user_type_models)

        for model in user_type_models:
            management.sync_type(ks_name=self.keyspace, type_model=model)
        for model in table_models:
            management.sync_table(model)

    def drop_db(self):
        """删除数据表, 单元测试时使用
        """
        if not self._is_connected:
            self.connect()

        management.drop_keyspace(self.keyspace)

        # 清除数据表后断开连接
        self.disconnect()
