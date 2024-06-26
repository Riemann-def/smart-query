import json
import os
import psycopg2
from common.utils import get_rabbitmq_connection
import pika
import logging
from decimal import Decimal
from datetime import date

# Configurar el registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def execute_query(sql_query):
    conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
    cur = conn.cursor()
    cur.execute(sql_query)
    results = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    
    # Convertir los objetos Decimal y date a tipos compatibles con JSON
    converted_results = []
    for row in results:
        converted_row = []
        for value in row:
            if isinstance(value, Decimal):
                converted_row.append(float(value))
            elif isinstance(value, date):
                converted_row.append(value.isoformat())
            else:
                converted_row.append(value)
        converted_results.append(converted_row)
    
    return converted_results, colnames

def callback(ch, method, properties, body):
    data = json.loads(body)
    sql_query = data.get("sql_query")
    logger.info(f"Executing SQL Query: {sql_query}")

    try:
        results, colnames = execute_query(sql_query)
        logger.info(f"Query executed successfully: {results} -- {colnames}")

        connection = get_rabbitmq_connection(RABBITMQ_HOST)
        channel = connection.channel()
        channel.queue_declare(queue='formatting_queue')
        channel.basic_publish(exchange='', routing_key='formatting_queue', body=json.dumps({"results": results, "columns": colnames}))
        logger.info("Data sent to Formatting Service")
        connection.close()
    except Exception as e:
        logger.error(f"Error executing query: {e}")

def main():
    connection = get_rabbitmq_connection(RABBITMQ_HOST)
    channel = connection.channel()
    channel.queue_declare(queue='execution_queue')
    channel.basic_consume(queue='execution_queue', on_message_callback=callback, auto_ack=True)
    logger.info("Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
