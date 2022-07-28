# Lightweight use of rabbitmq in web services
## requirements
pip install kombu==4.6.11

## Usages:
### step1: define routing_key
```python
TEST_ACTION_ROUTING_KEY = 'order.test'
```

### step2: define message handler func
> consumer: handle_test_action 位于 test.handler.test
>
> queue: test.handler.test.handle_test_action
```python
def handle_test_action(message):
    body = message.body
    pass
```


### step3: register message handle
```python
# bind queue to exchange by routing_key
class MessageHandler(object):
    def __init__(self):
        self.handle_map = {
            TEST_ACTION_ROUTING_KEY: handle_test_action,
        }
```

### step4: run consumer server
```python
mq_server = MQServer(rabbitmq_conn, MessageHandler())
t = Thread(target=mq_server.run, args=[])
t.setDaemon(True)
t.start()

# optional run producer
mq_producer = MQProducer(rabbitmq_conn, RABBITMQ_EXCHANGE)
```

### step5: publish message
```python
mq_producer.publish(TEST_ACTION_ROUTING_KEY, message)
# or
mq_server.publish(TEST_ACTION_ROUTING_KEY, message)
```
