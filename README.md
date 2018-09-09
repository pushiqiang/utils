# 1.django-rest-swagger==0.3.10

Django==1.11

djangorestframework==3.7.3

支持YAML docstrings

支持python3


# 2.docker/dynamic_mount_docker_volume
 
给正在运行的Docker容器动态绑定卷组（动态添加Volume）


# 3. django + celery低耦合使用

django和celery的低耦合使用

基于类的celery任务定义


# 4. 使用Nginx代理s3，动态生成缩略图并缓存

通过 {domain}/{uri}?s={size}实现获取指定大小缩略图

原图：`localhost/u/1523562/avatar`

缩略图：`localhost/u/1523562/avatar?s=200`

缩略图：`localhost/u/1523562/avatar?s=100`


# 5. zerorpc 使用

打印调用日志：打出所有的调用请求、参数和返回值，或写入日志

检测文件改变自动重启： autoreload, 更新代码不用重启服务，使用werkzeug的run_with_reloader函数实现


# 6. logger 日志切分周期输出文件

```
from logger import get_logger


# 普通控制台输出日志
logger = get_logger(name='console')

# 普通控制台和按日期周期文件输出日志
logger = get_logger(name='sanic', use_rotating=True)


```
output:   `2018-09-09 11:04:43 - your_logger_name - [main.py:7] INFO : Log info`

