import json
import os
import logging
import pika
import uuid
from openai import OpenAI
from common.utils import get_rabbitmq_connection

# Configurar el registro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configurar la clave de API de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def request_metadata():
    connection = get_rabbitmq_connection(RABBITMQ_HOST)
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    corr_id = str(uuid.uuid4())
    channel.basic_publish(
        exchange='',
        routing_key='metadata_request_queue',
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id,
        ),
        body=json.dumps({})
    )

    logger.info("Solicitud de metadatos enviada, esperando respuesta...")

    for method_frame, properties, body in channel.consume(callback_queue, inactivity_timeout=10):
        if properties.correlation_id == corr_id:
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            channel.queue_delete(callback_queue)
            connection.close()
            logger.info("Metadatos recibidos correctamente")
            return json.loads(body)
    else:
        logger.error("No se recibió respuesta en el tiempo esperado")
        channel.queue_delete(callback_queue)
        connection.close()
        return None

def generate_sql(query, schema):
    schema_str = "Schema:\n"
    for table, details in schema.items():
        if "columns" not in details:
            logger.error(f"Missing 'columns' in table {table}")
            continue
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

    Please provide only the SQL query, without any additional text or headings. Ensure the SQL query accurately reflects the provided schema and is syntactically correct.
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

    schema = request_metadata()
    if schema is None:
        logger.error("No se pudo obtener el esquema de la base de datos")
        return

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
