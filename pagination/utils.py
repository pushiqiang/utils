from functools import my_custom_sql


class QueryWrapper:
    """查询集包装器。实现django Paginator需要的必要方法，实现和query一样使用Paginator分页"""

    def __init__(self, sql, model_class=None):
        """
        :param sql: sql语句
        """
        self.sql = sql.replace(';', '')
        self.model_class = model_class

    def count(self):
        """
        计算总页数
        """
        sql = """select count(*) as count from (%s) _count""" % self.sql
        data = my_custom_sql(sql)
        if data:
            return data[0]['count']
        return 0

    def __getitem__(self, k):
        """
        分页只使用到了切片，此处的k为slice对象
        """
        x, y = k.start, k.stop
        sql = self.sql + ' LIMIT {start}, {num}'.format(start=x, num=y - x)
        result = my_custom_sql(sql)
        if self.model_class:
            result = [self.model_class(**item) for item in result]
        return result

    def all(self):
        return my_custom_sql(self.sql)
