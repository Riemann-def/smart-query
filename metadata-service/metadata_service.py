import os
import json
import logging
import time
import pika
from pymongo import MongoClient
import psycopg2
import mysql.connector
# Importa más conectores según sea necesario

from common.utils import get_rabbitmq_connection
from utils import get_db_schema

# Configurar el registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
MONGO_URI = os.getenv("MONGO_URI")

# Conexión a MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['metadata_db']
metadata_collection = db['metadata']
credentials_collection = db['credentials']

# Credenciales de la base de datos local
LOCAL_DB_CREDENTIALS = {
    "db_type": "postgresql",
    "db_host": os.getenv("DB_HOST"),
    "db_user": os.getenv("DB_USER"),
    "db_password": os.getenv("DB_PASSWORD"),
    "db_name": os.getenv("DB_NAME")
}


def store_schema(schema):
    metadata_collection.update_one({}, {"$set": {"schema": schema}}, upsert=True)
    logger.info("Metadatos almacenados en MongoDB")

def handle_metadata_request(ch, method, properties, body):
    # Recuperar el esquema almacenado en MongoDB
    metadata = metadata_collection.find_one({}, {'_id': False, 'schema': True})
    if metadata and 'schema' in metadata:
        schema = metadata['schema']
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=json.dumps(schema)
        )
        logger.info("Metadatos enviados al servicio de NLP: %s", schema)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        logger.error("No se encontraron metadatos en MongoDB")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def handle_metadata_update(ch, method, properties, body):
    credentials = json.loads(body)
    try:
        schema = get_db_schema(credentials)
        if schema:
            store_schema(schema)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            raise ValueError("Error al actualizar los metadatos")
    except Exception as e:
        logger.error(f"Error al actualizar los metadatos: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def initialize_metadata():
    if metadata_collection.count_documents({}) == 0:
        logger.info("La colección de metadatos está vacía. Obteniendo metadatos iniciales...")
        schema = get_db_schema(LOCAL_DB_CREDENTIALS)
        if schema:
            store_schema(schema)
        else:
            logger.error("Error al obtener el esquema de la base de datos local")

def main():
    time.sleep(25)
    initialize_metadata()
    
    connection = get_rabbitmq_connection(RABBITMQ_HOST)
    channel = connection.channel()
    channel.queue_declare(queue='metadata_request_queue')
    channel.queue_declare(queue='metadata_update_queue')

    channel.basic_consume(queue='metadata_request_queue', on_message_callback=handle_metadata_request, auto_ack=False)
    channel.basic_consume(queue='metadata_update_queue', on_message_callback=handle_metadata_update, auto_ack=False)

    logger.info("Esperando mensajes en las colas 'metadata_request_queue' y 'metadata_update_queue'...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
