# -*- coding: utf-8 -*-
from DBUtils.PooledDB import PooledDB
from DBUtils.SteadyDB import SteadyDBConnection


class DBPoolWrapper(object):
    def __init__(self, db_module):
        self._connection = None
        self._db_module = db_module
        self._pool = {}

    def __getattr__(self, item):
        return getattr(self._db_module, item)

    def connect(self, **kwargs):
        db = kwargs.get("db", "")
        if db not in self._pool:
            self._pool[db] = PooledDB(creator=self._db_module, **kwargs)
        self._connection = self._pool[db].connection()
        return self._connection


def autocommit(self, *args, **kwargs):
    self._con.autocommit(*args, **kwargs)


def get_server_info(self):
    return self._con.get_server_info()


@property
def encoders(self):
    return self._con.encoders


setattr(SteadyDBConnection, "autocommit", autocommit)
setattr(SteadyDBConnection, "get_server_info", get_server_info)
setattr(SteadyDBConnection, "encoders", encoders)
