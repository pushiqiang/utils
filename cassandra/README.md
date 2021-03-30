## Using ORM:
```
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
```



## Using CQL:
```
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
```

## Paging query
```
import base64

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import SimpleStatement, conn


class User(Model):
    __table_name__ = 'user'
    user_id = columns.UUID(partition_key=True)

    @classmethod
    def paging_query(cls, user_id=None, paging_state=None, page_size=10):
        """分页查询
        """
        cql = 'SELECT * FROM user'
        if user_id:
            cql = f'{cql} where user_id={user_id}'
        statement = SimpleStatement(cql, fetch_size=page_size)
        connection = conn.get_connection()

        if paging_state is not None:
            paging_state = base64.b64decode(bytes(paging_state, encoding='utf-8'), '-_')

        # 查询数据库
        result_set = connection.session.execute(statement,
                                                paging_state=paging_state)
        results = [cls(**result) for result in result_set.current_rows]

        paging_state = None
        if result_set.paging_state:
            paging_state = str(base64.b64encode(result_set.paging_state, b'-_'),
                               encoding='utf-8')

        return results, paging_state


```
