# -*- coding: utf-8 -*-
from django.utils import six
from django.core.exceptions import ImproperlyConfigured
from django.db.backends.mysql.base import DatabaseWrapper as _DatabaseWrapper
from django.utils.safestring import SafeBytes, SafeText

try:
    import MySQLdb as Database
except ImportError as err:
    try:
        import pymysql as Database
    except ImportError:
        raise ImproperlyConfigured("Error loading MySQLdb or pymsql module.\n Did you install mysqlclient or pymysql")

from db_utils.db.pool import DBPoolWrapper


Database = DBPoolWrapper(Database)


class DatabaseWrapper(_DatabaseWrapper):

    Database = Database

    def get_connection_params(self):
        params = super(DatabaseWrapper, self).get_connection_params()
        pool_config = self.settings_dict.get('POOL', {})
        minsize = pool_config.pop("mincached", 0)
        maxsize = pool_config.pop("maxcached", 0)
        params["mincached"] = int(minsize)
        params["maxcached"] = int(maxsize)
        params.update(pool_config)

        return params

    def get_new_connection(self, conn_params):
        conn = Database.connect(**conn_params)
        conn.encoders[SafeText] = conn.encoders[six.text_type]
        conn.encoders[SafeBytes] = conn.encoders[bytes]
        return conn
