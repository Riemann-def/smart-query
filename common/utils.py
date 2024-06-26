# common/utils.py

import time
import pika

def get_rabbitmq_connection(host, max_retries=10, retry_delay=10):
    connection = None
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host))
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Unable to connect to RabbitMQ. Attempt {attempt + 1}/{max_retries}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    if connection is None:
        raise pika.exceptions.AMQPConnectionError(f"Failed to connect to RabbitMQ after {max_retries} attempts.")
    return connection
