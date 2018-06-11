## django + celery

django和celery的低耦合使用

基于类的celery任务定义


## 使用

1. 在`task_worker/tasks.py`文件中定义任务，可自定义文件名，只需要在__init__.py文件中引入定义的task

2. task_worker作为django项目下的一个包，启动run_worker.sh

3. 在django中应用中直接调用执行
```
from task_worker import PostNoticeFollowerTask

PostNoticeFollowerTask.delay(**kwargs)
```
