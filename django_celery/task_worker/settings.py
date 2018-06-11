
import os
import socket

from kombu import Exchange, Queue


# Redis
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_HOST = 'redis'

# celery config
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Asia/Shanghai'

RABBIT_HOSTNAME = socket.gethostbyname('rabbitmq')


BROKER_URL = 'amqp://{user}:{password}@{hostname}/{vhost}'.format(
    user='root',
    password='devpassword',
    hostname=RABBIT_HOSTNAME,
    vhost='rabbitmq_vhost')

# We don't want to have dead connections stored on rabbitmq, so we have to negotiate using heartbeats
BROKER_HEARTBEAT = '?heartbeat=30'
if not BROKER_URL.endswith(BROKER_HEARTBEAT):
    BROKER_URL += BROKER_HEARTBEAT

# Celery configuration
# configure queues
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('post_notcie', Exchange('post_notcie'), routing_key='post.notcie.follower'),
    Queue('comment_notcie', Exchange('comment_notcie'), routing_key='post.comment.notcie.owner'),
    Queue('es_update', Exchange('es_update'), routing_key='es.index.update'),
    Queue('es_delete', Exchange('es_delete'), routing_key='es.index.delete'),
)

# 路由（哪个任务放入哪个队列）
CELERY_ROUTES = {
    'task_worker.tasks.PostNoticeFollowerTask': {'queue': 'post_notcie', 'routing_key': 'post.notcie.follower'},
    'task_worker.tasks.CommentNoticeOwnerTask': {'queue': 'comment_notcie', 'routing_key': 'post.comment.notcie.owner'},
    'task_worker.tasks.EsIndexUpdateTask': {'queue': 'es_update', 'routing_key': 'es.index.update'},
    'task_worker.tasks.EsIndexDeleteTask': {'queue': 'es_delete', 'routing_key': 'es.index.delete'},
}

# Sensible settings for celery
CELERY_TASK_PUBLISH_RETRY = True
CELERY_DISABLE_RATE_LIMITS = False

CELERY_TASK_RESULT_EXPIRES = 600

# Set redis as celery result backend
CELERY_RESULT_BACKEND = 'redis://%s:%d/%d' % (REDIS_HOST, REDIS_PORT, REDIS_DB)
CELERY_REDIS_MAX_CONNECTIONS = 1

# Don't use pickle as serializer, json is much safer
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['application/json']

CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_MAX_TASKS_PER_CHILD = 1000

