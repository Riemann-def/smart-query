# validation-service/validation_service.py

import json
import os
from common.utils import get_rabbitmq_connection
import pika
import logging
import re

# Configurar el registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")

def callback(ch, method, properties, body):
    data = json.loads(body)
    sql_query = data.get("sql_query")["sql_query"]

    # Aquí podrías agregar validaciones específicas de SQL
    valid_sql_query = clean_sql_query(sql_query)

    try:
        connection = get_rabbitmq_connection(RABBITMQ_HOST)
        channel = connection.channel()
        channel.queue_declare(queue='execution_queue')
        channel.basic_publish(exchange='', routing_key='execution_queue', body=json.dumps({"sql_query": valid_sql_query}))
        logger.info("Query sent to Execution Service: %s", valid_sql_query)
    except Exception as e:
        logger.error(f"Error publishing to RabbitMQ: {e}")
    finally:
        connection.close()

def clean_sql_query(sql_query):
    # Eliminar los bloques de código (```sql y ```)
    cleaned_query = re.sub(r'```sql|```', '', sql_query).strip()
    return cleaned_query

def main():
    connection = get_rabbitmq_connection(RABBITMQ_HOST)
    channel = connection.channel()
    channel.queue_declare(queue='validation_queue')
    channel.basic_consume(queue='validation_queue', on_message_callback=callback, auto_ack=True)
    logger.info("Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
