都知道django每次请求都会连接数据库和释放数据库连接。Django为每个请求使用新的数据库连接。一开始这个方法行得通。然而随着服务器上的负载的增加,创建/销毁连接数据库开始花大量的时间。要避免这个，你可以使用数据库连接池，这里使用SQLAlchemy的连接池。使Django持久化数据库连接。

###但这种方法会改变django的代码。对框架有侵入


#### 方法 1
实现方法如下：
　　把django/db/backends/mysql文件夹全部拷贝出来，放在项目的一个libs/mysql下面，然后修改base.py文件。
　　或者把django/db/backends/mysql文件夹在django/db/backends/下面复制为mysql_pool文件夹，将base.py中所以import中的mysql替换为mysql_pool，这样可以直接在settings.py中设置'ENGINE':'django.db.backends.mysql_pool'
找到
```
try:    
    import MySQLdb as Database
except ImportError as e:    
    from django.core.exceptions import ImproperlyConfigured    
    raise ImproperlyConfigured("Error loading MySQLdb module: %s" % e)
```
这段代码，在下面添加：
```
from sqlalchemy import pool
Database = pool.manage(Database[,recycle=DATABASE_WAIT_TIMEOUT-1])
#其中DATABASE_WAIT_TIMEOUT为你定义的连接超时时间，必须小于等于mysql里面的wait_timeout（）
```
结果如下
```
try:    
    import MySQLdb as Database
except ImportError as e:    
    from django.core.exceptions import ImproperlyConfigured    
    raise ImproperlyConfigured("Error loading MySQLdb module: %s" % e)
from sqlalchemy import pool
Database = pool.manage(Database)
```
然后找到get_connection_params(self)函数代码：
```
def get_connection_params(self):
    kwargs = {
        'conv':django_conversions,
        'charset':utf8
        }
        ...
```
修改为：
```
def get_connection_params(self):
    kwargs = {
        'charset':utf8
        }
        ...
```
注意：如果不改变此处的kwargs，将会出现：TypeError:unhashable type:'dict' 的错误。
原样用kwargs传的话，sqlalchemy的pool会报unhashable错误，那是因为kwargs中有个key（conv）对应的value（django_conversions）是个字典，在pool中会把（key,value）组成元组作为新的key保存在pool中，但是因为value（django_conversions）是dict，不允许作为key的

在mysql里使用 show status 或 show processlist查看连接情况

#### 方法 2
直接在settings.py同级目录下的__init__.py文件中添加如下代码
```
from django.conf import settings
from django.db.utils import load_backend
import sqlalchemy.pool as pool
import logging
pool_initialized=False

def init_pool():
     if not globals().get('pool_initialized', False):
         global pool_initialized
         pool_initialized = True
         try:
             backendname = settings.DATABASES['default']['ENGINE']
             backend = load_backend(backendname)

             #replace the database object with a proxy.
             backend.Database = pool.manage(backend.Database)

             backend.DatabaseError = backend.Database.DatabaseError
             backend.IntegrityError = backend.Database.IntegrityError
             logging.info("Connection Pool initialized")
         except:
             logging.exception("Connection Pool initialization error")

init_pool()
```
然后修改django/db/backends/mysql/base.py文件
找到get_connection_params(self)函数代码：
修改为：
```
def get_connection_params(self):
    kwargs = {
        'charset':utf8
        }
        ...
```
同理，不修改kwargs将会出现：TypeError:unhashable type:'dict' 的错误。

以上两种方法都要改变django的代码，有一定入侵性，第二种方法改变要小一点


django 1.7
python 2.7
sqlalchemy 1.0


