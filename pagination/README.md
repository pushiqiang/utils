
## 全表id倒序分页

根据id倒序（即创建时间倒叙）分页，适用简单场景

使用max获取最大id，从最后一条数据向前分页
通过id倒序向前推进使用 `<=` 和 `limit` 结合的方式优化分页加载
eg: select * from yourtable where id <= seek_id order by id desc limit 20;

### Using

```
from pagination.pagination import WholeTableIdReversePagination

queryset = YourModel.objects.all()
pagination = WholeTableIdReversePagination()
result = list(pagination.paginate_queryset(queryset, request))
```

#### DRF Using

```
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'pagination.pagination.WholeTableIdReversePagination',
}
```

#### Request:
```
GET https://api.example.org/accounts/?page_seek_id=100
or
GET https://api.example.org/accounts/
```

#### Response:
```
HTTP 200 OK
{
    "count": 20
    "next": "https://api.example.org/accounts/?page_seek_id=80",
    "previous": none,
    "results": [
       …
    ]
}
```
