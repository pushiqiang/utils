全表id倒序分页

原生sql使用Paginator分页


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


## Django原生sql使用Paginator分页
```
from utils import QueryWrapper

class User(models.Model):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)


sql = 'select id, username, first_name from auth_user'
queryset = QueryWrapper(sql, User)

count = queryset.count() 
data = queryset.all()

# 在Django中使用
from django.core.paginator import Paginator
pages = Paginator(queryset, per_page=10)
page = pages.page(page_no) # 获取某页数据


# 在django rest framework中使用
page = self.paginate_queryset(queryset)
results = self.get_paginated_response(page).data
print(results)

>>>
{
	"count": 25,
	"next": "http://127.0.0.1:8888/test/?page=2",
	"previous": null,
	"results": [{
		"id": 11349230,
		"username": "张三",
		"phone": "1440182340944",
	
	}, {
		"id": 11344204,
		"username": "李四",
		"phone": "1440182333431",
	},..
}


```