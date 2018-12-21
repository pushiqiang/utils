

class QueryWrapper(object):
    """查询集包装器。实现django Paginator需要的必要方法，实现和query一样使用Paginator分页"""

    def __init__(self, sql, params=None, db="default"):
        """
        :param sql: sql语句
        """
        self.sql = sql
        self.params = params
        self.db = db

    def count(self):
        """计算总数据条数"""
        sql = """select count(*) as count from (%s) _count""" % self.sql
        data = exec_sql(sql)
        if data:
            return data[0]['count'] # 返回总数据条数
        return 0

    def __getitem__(self, k):
        """分页只使用到了切片，此处的k为slice对象"""
        x, y = k.start, k.stop
        sql = self.sql + ' LIMIT {start}, {num}'.format(start=x, num=y - x)
        result = exec_sql(sql) # 字典列表形式返回
        return result

    def all(self):
        """查询所有数据"""
        return exec_sql(self.sql) # 字典列表形式返回
