import os
import json
import pika
import time
import logging
from pymongo import MongoClient
from common.utils import get_rabbitmq_connection

# Configurar el registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
MONGO_URI = os.getenv("MONGO_URI")

# Conexión a MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['credentials_db']
collection = db['credentials']

# Credenciales de la base de datos local
LOCAL_DB_CREDENTIALS = {
    "db_type": "postgresql",
    "db_host": os.getenv("DB_HOST"),
    "db_user": os.getenv("DB_USER"),
    "db_password": os.getenv("DB_PASSWORD"),
    "db_name": os.getenv("DB_NAME")
}

def store_credentials(credentials):
    collection.update_one({}, {"$set": credentials}, upsert=True)
    logger.info("Credenciales almacenadas en MongoDB")
    request_metadata_update()

def request_metadata_update():
    credentials = collection.find_one({}, {'_id': False})
    if credentials:
        connection = get_rabbitmq_connection(RABBITMQ_HOST)
        channel = connection.channel()
        channel.queue_declare(queue='metadata_update_queue')
        channel.basic_publish(exchange='', routing_key='metadata_update_queue', body=json.dumps(credentials))
        logger.info("Solicitud de actualización de metadatos enviada")
        connection.close()

def initialize_credentials():
    if collection.count_documents({}) == 0:
        logger.info("La colección de credenciales está vacía. Almacenando credenciales locales...")
        store_credentials(LOCAL_DB_CREDENTIALS)

def callback(ch, method, properties, body):
    credentials = json.loads(body)
    store_credentials(credentials)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    time.sleep(10)
    initialize_credentials()

    connection = get_rabbitmq_connection(RABBITMQ_HOST)
    channel = connection.channel()
    channel.queue_declare(queue='credentials_queue')
    channel.basic_consume(queue='credentials_queue', on_message_callback=callback, auto_ack=False)
    logger.info("Esperando mensajes en la cola 'credentials_queue'...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
