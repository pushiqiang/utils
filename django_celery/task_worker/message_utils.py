import os

import pika
import json


credentials = pika.PlainCredentials(
    os.environ.get('RABBIT_ENV_USER', 'admin'),
    os.environ.get('RABBIT_ENV_RABBITMQ_PASS', 'mypass'),
)
parameters = pika.ConnectionParameters(
    host=os.environ.get('RABBIT_PORT_5672_TCP_ADDR'),
    port=int(os.environ.get('RABBIT_PORT_5672_TCP_PORT')),
    credentials=credentials,
)

connection = pika.BlockingConnection(parameters)

channel = connection.channel()

def send_msg(body, headers=None):
    # channel.queue_delete(queue='ws_msg')
    channel.exchange_declare(exchange='ws_msg.exchange',type='direct')
    channel.queue_declare(queue='ws_msg')
    channel.queue_bind(exchange='ws_msg.exchange', queue='ws_msg')

    properties = pika.BasicProperties(
        app_id='job-publisher',
        content_type='application/json',
    )

    if headers:
        properties.headers = headers

    channel.basic_publish(
        exchange='ws_msg.exchange',
        routing_key='ws_msg',
        body=json.dumps(body),
        properties=properties
)