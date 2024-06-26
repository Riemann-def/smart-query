import json
import os
import psycopg2
import pika
import logging
from openai import OpenAI
from common.utils import get_rabbitmq_connection

# Configurar el registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Configurar la clave de API de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def get_db_schema():
    conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
    cur = conn.cursor()

    # Obtener nombres de tablas y columnas
    cur.execute("""
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'public'
    """)
    columns = cur.fetchall()

    # Obtener claves primarias
    cur.execute("""
    SELECT
        tc.table_name, 
        kcu.column_name
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
    WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public'
    """)
    primary_keys = cur.fetchall()

    # Obtener claves foráneas
    cur.execute("""
    SELECT
        tc.table_name, 
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name 
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
    """)
    foreign_keys = cur.fetchall()

    schema = {}
    for table_name, column_name, data_type in columns:
        if table_name not in schema:
            schema[table_name] = {
                "columns": [],
                "primary_keys": [],
                "foreign_keys": []
            }
        schema[table_name]["columns"].append({"column_name": column_name, "data_type": data_type})

    for table_name, column_name in primary_keys:
        if table_name in schema:
            schema[table_name]["primary_keys"].append(column_name)

    for table_name, column_name, foreign_table_name, foreign_column_name in foreign_keys:
        if table_name in schema:
            schema[table_name]["foreign_keys"].append({
                "column_name": column_name,
                "foreign_table_name": foreign_table_name,
                "foreign_column_name": foreign_column_name
            })

    cur.close()
    conn.close()
    return schema

def generate_sql(query, schema):
    schema_str = "Schema:\n"
    for table, details in schema.items():
        schema_str += f"Table {table}: "
        schema_str += ", ".join([f"{col['column_name']} ({col['data_type']})" for col in details['columns']])
        schema_str += "\n"
        schema_str += f"Primary Keys: {', '.join(details['primary_keys'])}\n"
        if details['foreign_keys']:
            schema_str += "Foreign Keys:\n"
            for fk in details['foreign_keys']:
                schema_str += f" - {fk['column_name']} references {fk['foreign_table_name']}({fk['foreign_column_name']})\n"

    prompt = f"""
    You are an SQL expert. Based on the given database schema, generate an SQL query for the following natural language request.

    Database Schema:
    {schema_str}

    Natural Language Query:
    {query}

    Please make sure the SQL query accurately reflects the provided schema.
    """

    try:
        logger.info("Prompt para GPT-3: %s", prompt)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Utiliza el motor adecuado (GPT-3.5, GPT-4, etc.)
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=150
        )
        sql_query = completion.choices[0].message.content
        logger.info(f"Consulta SQL generada correctamente: {sql_query}")
        return {"sql_query": sql_query}
    except Exception as e:
        logger.error(f"Error generando consulta SQL: {e}")
        raise e

def callback(ch, method, properties, body):
    data = json.loads(body)
    query = data.get("query")

    schema = get_db_schema()
    sql_query = generate_sql(query, schema)

    connection = get_rabbitmq_connection(RABBITMQ_HOST)
    channel = connection.channel()
    channel.queue_declare(queue='validation_queue')
    channel.basic_publish(exchange='', routing_key='validation_queue', body=json.dumps({"sql_query": sql_query}))
    logger.info(f"Query sent to Validation Service: {sql_query}")
    connection.close()

def main():
    connection = get_rabbitmq_connection(RABBITMQ_HOST)
    channel = connection.channel()
    channel.queue_declare(queue='nlp_queue')
    channel.basic_consume(queue='nlp_queue', on_message_callback=callback, auto_ack=True)
    logger.info("Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
