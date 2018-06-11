# 默认情况下，所有配置的队列都已启用
# 注意: 启动的时候并不推荐在一个worker进程中启动多个队列(celery worker -A work.app -l info),强烈建议分开进程跑(celery worker -A work.app -c 2 -Q email_queue -l info;celery worker -A work.app -c 4 -Q wixin_queue -l info),分开独立工作进程跑,进程之间不会互相影响~
celery worker -A task_worker.app -l info

