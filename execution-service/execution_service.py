import json
import os
import psycopg2
import mysql.connector
from pymongo import MongoClient
from common.utils import get_rabbitmq_connection
import pika
import logging
from decimal import Decimal
from datetime import date, datetime

# Configurar el registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
MONGO_URI = os.getenv("MONGO_URI")

# Conexión a MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['credentials_db']
credentials_collection = db['credentials']

def get_credentials():
    credentials = credentials_collection.find_one({}, {'_id': False})
    if credentials:
        return credentials
    else:
        raise Exception("No se encontraron credenciales en MongoDB")

def execute_postgresql_query(sql_query, credentials):
    conn = psycopg2.connect(
        host=credentials['db_host'],
        user=credentials['db_user'],
        password=credentials['db_password'],
        dbname=credentials['db_name']
    )
    cur = conn.cursor()
    cur.execute(sql_query)
    results = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    
    return results, colnames

def execute_mysql_query(sql_query, credentials):
    conn = mysql.connector.connect(
        host=credentials['db_host'],
        user=credentials['db_user'],
        password=credentials['db_password'],
        database=credentials['db_name']
    )
    cur = conn.cursor()
    cur.execute(sql_query)
    results = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    return results, colnames

def execute_query(sql_query):
    credentials = get_credentials()
    db_type = credentials.get("db_type", "postgresql")
    if db_type == "postgresql":
        return execute_postgresql_query(sql_query, credentials)
    elif db_type == "mysql":
        return execute_mysql_query(sql_query, credentials)
    else:
        logger.error(f"Tipo de base de datos no soportado: {db_type}")
        return None, None

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def callback(ch, method, properties, body):
    data = json.loads(body)
    sql_query = data.get("sql_query")
    logger.info(f"Executing SQL Query: {sql_query}")

    try:
        results, colnames = execute_query(sql_query)
        if results is None or colnames is None:
            raise Exception("Error al ejecutar la consulta")

        logger.info(f"Query executed successfully: {results} -- {colnames}")

        connection = get_rabbitmq_connection(RABBITMQ_HOST)
        channel = connection.channel()
        channel.queue_declare(queue='formatting_queue')
        channel.basic_publish(
            exchange='', 
            routing_key='formatting_queue', 
            body=json.dumps({"results": results, "columns": colnames}, default=json_serial)
        )
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
