import json
import os
import pandas as pd
from common.utils import get_rabbitmq_connection
import pika
import logging

# Configurar el registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        results = data.get("results")
        columns = data.get("columns")

        logger.info(f"Received data: {results} -- {columns}")

        if isinstance(results, list) and isinstance(columns, list):
            df = pd.DataFrame(results, columns=columns)
            # Convertir los tipos de datos del DataFrame a tipos nativos de Python
            df = df.astype(object).where(pd.notnull(df), None)
            
            if len(df.columns) == 1 and "count" in df.columns[0].lower():
                count = df.iloc[0, 0]
                formatted_data = {"type": "counter", "data": count}
            else:
                table_data = df.to_dict(orient='records')
                formatted_data = {"type": "table", "data": table_data}
        else:
            logger.error("Invalid data format received")
            formatted_data = {"type": "error", "data": "Invalid data format received"}

        connection = get_rabbitmq_connection(RABBITMQ_HOST)
        channel = connection.channel()
        channel.queue_declare(queue='response_queue')
        channel.basic_publish(exchange='', routing_key='response_queue', body=json.dumps(formatted_data))
        logger.info("Data sent to Response Service: %s", formatted_data)
        connection.close()
    except Exception as e:
        logger.error(f"Error processing data: {e}")

def main():
    connection = get_rabbitmq_connection(RABBITMQ_HOST)
    channel = connection.channel()
    channel.queue_declare(queue='formatting_queue')
    channel.basic_consume(queue='formatting_queue', on_message_callback=callback, auto_ack=True)
    logger.info("Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
