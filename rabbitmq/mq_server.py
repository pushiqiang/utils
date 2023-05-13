
"""
pip install kombu==4.6.11

Usages:
# step1: define routing_key
TEST_ACTION_ROUTING_KEY = 'order.test'

# step2: define message handler func
# consumer: handle_test_action 位于 test.handler.test
# queue: test.handler.test.handle_test_action
def handle_test_action(message):
    body = message.body
    pass

# step3: register message handle
# bind queue to exchange by routing_key
class MessageHandler(object):
    def __init__(self):
        self.handle_map = {
            TEST_ACTION_ROUTING_KEY: handle_test_action,
        }

# step4: run consumer server
mq_server = MQServer(rabbitmq_conn, MessageHandler())
t = Thread(target=mq_server.run, args=[])
t.setDaemon(True)
t.start()

# optional run producer
mq_producer = MQProducer(rabbitmq_conn, RABBITMQ_EXCHANGE)

# step5: publish message
mq_producer.publish(TEST_ACTION_ROUTING_KEY, message)
or
mq_server.publish(TEST_ACTION_ROUTING_KEY, message)
"""

import logging
import signal
import time
import Queue as queue
from json import dumps as json_dump
from functools import partial, wraps
from threading import Thread

from kombu import Exchange, Queue
from kombu.messaging import Consumer
from kombu.mixins import ConsumerProducerMixin

logger = logging.getLogger(__name__)


class Message(object):
    def __init__(self, sender, timestamp, body, delay=None, **context):
        self.sender = sender
        self.timestamp = timestamp
        self.body = body
        self.context = context
        self.delay = delay


def retry(count=1):
    """
    Retry decorator for consumer
    Usage:
    @retry(3)
    def handle(message):
        pass
    """
    assert 0 < count and isinstance(count, int), \
        'retry count must be a positive integer greater than 0'

    def retry_decorator(func):
        setattr(func, '_retry', count)

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped_func

    return retry_decorator


def after_ack(func):
    """

    Consume after ack, consume at most once
    Usage:
    @after_ack
    def handle(message):
        pass
    """
    setattr(func, '_after_ack', True)

    @wraps(func)
    def wrapped_func(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapped_func


class MQProducer(object):
    def __init__(self, connection, exchange='default', exchange_type='direct'):
        self.connection = connection
        self.should_stop = False
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._thread = None
        self._wait_publish_queue = queue.Queue()
        self._register_signal()
        self.run_in_thread()

    def handle_exit(self, sig, frame):
        self.should_stop = True

    def _register_signal(self):
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def publish(self, routing_key, message, exchange=None, sender=None, delay=None, **context):
        try:
            data = {
                'sender': sender,
                'timestamp': int(time.time()),
                'body': message,
                'context': context,
                'delay': delay
            }
            self._wait_publish_queue.put((routing_key, exchange, data))
        except Exception:
            logger.error('Send message to queue error.', exc_info=True)

    def _thread_publish_executor(self):
        producer = self.connection.Producer()
        while True:
            try:
                routing_key, exchange, data = self._wait_publish_queue.get_nowait()
            except Exception:
                if self.should_stop:
                    return
                time.sleep(2)
                self.connection.connection.send_heartbeat()
            else:
                try:
                    producer.publish(json_dump(data),
                                     routing_key=routing_key,
                                     content_type='application/json',
                                     exchange=exchange or self._exchange,
                                     retry=True)
                except Exception:
                    logger.error('Send message to rabbitmq error.', exc_info=True)
                finally:
                    self._wait_publish_queue.task_done()

    def run_in_thread(self):
        self._thread = Thread(target=self._thread_publish_executor, args=[])
        self._thread.start()
        return self._thread


class MQServer(ConsumerProducerMixin):
    """
    Rabbitmq consumer server, stateless, can start multiple servers
    Usage:
         rabbitmq_conn= get_rabbitmq()
         server = MQServer(rabbitmq_conn, MQHandler())
         t = Thread(target=server.run, args=[])
         t.setDaemon(True)
         t.start()
    """
    def __init__(self, connection, handler, exchange='default', exchange_type='direct', worker_num=5):
        assert hasattr(handler, 'handle_map') and isinstance(handler.handle_map, dict)
        self.connection = connection
        self.handler = handler
        self.should_stop = False
        self._wait_publish_queue = queue.Queue()
        self._wait_ack_queue = queue.Queue()
        self._channels = {}
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._default_channel = None
        self._producer_connection = None
        self._register_signal()
        self._worker_num = worker_num
        self._worker_pool = None
        self._create_workers()

    def _create_workers(self):
        from utils.pool import WorkerThreadPool
        self._worker_pool = WorkerThreadPool(self._worker_num)

    def handle_exit(self, sig, frame):
        self.should_stop = True
        self._worker_pool.close()

    def _register_signal(self):
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def get_consumers(self, _, default_channel):
        self._default_channel = default_channel
        consumers = []
        exchange = Exchange(self._exchange, type=self._exchange_type, durable=True, auto_delete=False)
        for _routing_key, handles in self.handler.handle_map.items():
            if not isinstance(handles, list):
                handles = [handles]
            for handle in handles:
                channel = default_channel.connection.channel()
                self._channels[id(channel)] = channel
                _queue = '{}.{}'.format(handle.__module__, handle.__name__)
                consumers.append(Consumer(channel=channel,
                                          queues=[Queue(_queue, exchange, routing_key=_routing_key,
                                                        durable=True, auto_delete=False)],
                                          callbacks=[partial(self.on_message, handle)],
                                          on_decode_error=self.on_decode_error))

        return consumers

    def _thread_publish_executor(self):
        producer = self.producer
        while True:
            try:
                routing_key, exchange, data, retry_count = self._wait_publish_queue.get_nowait()
            except Exception:
                if self.should_stop:
                    return
                time.sleep(2)
            else:
                try:
                    producer.publish(json_dump(data),
                                     routing_key=routing_key,
                                     content_type='application/json',
                                     exchange=exchange or self._exchange,
                                     headers={'x-retry-count': retry_count} if retry_count is not None else None,
                                     retry=True)
                except Exception:
                    logger.error('Send message to rabbitmq error.', exc_info=True)
                finally:
                    self._wait_publish_queue.task_done()

    def _retry_publish(self, handle, body, message):
        """
        Retry
        """
        retry_count = message.headers.get('x-retry-count', getattr(handle, '_retry', 0)) - 1
        if 0 <= retry_count:
            # Send back to the queue to retry
            self._wait_publish_queue.put(
                (message.delivery_info['routing_key'], message.delivery_info['exchange'], body, retry_count))

    def publish(self, routing_key, message, exchange=None, sender=None, delay=None, **context):
        try:
            data = {
                'sender': sender,
                'timestamp': int(time.time()),
                'body': message,
                'context': context,
                'delay': delay
            }
            self._wait_publish_queue.put((routing_key, exchange, data, None), timeout=3)
        except Exception:
            logger.error('Send message to queue error.', exc_info=True)

    def _thread_executor(self, handle, body, message):
        try:
            m = Message(**body)
            if m.delay:
                gap = m.timestamp + m.delay - int(time.time())
                if 0 < gap:
                    time.sleep(gap)
            handle(m)
        except Exception:
            logger.error('Handle message error. handle:[{}], message:[{}]'.format(
                '.'.join([handle.__module__, handle.__name__]), body), exc_info=True)
            self._retry_publish(handle, body, message)

        if not getattr(handle, '_after_ack', False):
            # non thread-safe, send to main thread queue to ack
            self._wait_ack_queue.put((id(message.channel), message.delivery_tag))

    def on_message(self, handle, body, message):
        _after_ack = getattr(handle, '_after_ack', False)
        if _after_ack:
            # ack at the first time
            message.ack()

        self._worker_pool.run(self._thread_executor, args=[handle, body, message])
        self.on_iteration()

    def on_iteration(self):
        try:
            channel_id, delivery_tag = self._wait_ack_queue.get(block=False)
        except Exception:
            pass
        else:
            channel = self._channels.get(channel_id)
            if not channel:
                self._wait_ack_queue.task_done()
                return

            try:
                channel.basic_ack(delivery_tag)
            except Exception:
                pass
            finally:
                self._wait_ack_queue.task_done()

    def on_consume_end(self, connection, default_channel):
        if self._producer_connection is not None:
            self._producer_connection.close()
            self._producer_connection = None

        for _channel in self._channels.values():
            _channel.close()

    def on_decode_error(self, message, exc):
        logger.error(
            "Can't decode message body(type:{!r} encoding:{!r} raw:{!r})".format(
                message.content_type, message.content_encoding, message.body),
            exc_info=exc)

    def run(self, _tokens=1, **kwargs):
        thr = Thread(target=self._thread_publish_executor, args=[])
        thr.start()
        super(MQServer, self).run(_tokens, **kwargs)
