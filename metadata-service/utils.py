import psycopg2
import mysql.connector
import logging

logger = logging.getLogger(__name__)

def execute_schema_queries(conn, queries):
    try:
        cur = conn.cursor()

        results = {}
        for query_name, query in queries.items():
            cur.execute(query)
            results[query_name] = cur.fetchall()

        cur.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error ejecutando consultas de esquema: {e}")
        return None

def format_schema(columns, primary_keys, foreign_keys):
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
        if table_name in schema and column_name not in schema[table_name]["primary_keys"]:
            schema[table_name]["primary_keys"].append(column_name)

    for table_name, column_name, foreign_table_name, foreign_column_name in foreign_keys:
        if table_name in schema:
            schema[table_name]["foreign_keys"].append({
                "column_name": column_name,
                "foreign_table_name": foreign_table_name,
                "foreign_column_name": foreign_column_name
            })

    return schema


# Queries específicas para PostgreSQL
def get_postgresql_queries():
    return {
        "columns": f"""
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public'
        """,
        "primary_keys": f"""
        SELECT
            tc.table_name, 
            kcu.column_name
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public'
        """,
        "foreign_keys": f"""
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
        """
    }

# Queries específicas para MySQL
def get_mysql_queries():
    return {
        "columns": f"""
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = DATABASE();
        """,
        "primary_keys": f"""
        SELECT
            kcu.table_name,
            kcu.column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE
            tc.constraint_type = 'PRIMARY KEY'
            AND kcu.table_schema = DATABASE();
        """,
        "foreign_keys": f"""
        SELECT
            kcu.TABLE_NAME,
            kcu.COLUMN_NAME,
            kcu.REFERENCED_TABLE_NAME AS foreign_table_name,
            kcu.REFERENCED_COLUMN_NAME AS foreign_column_name
        FROM
            information_schema.KEY_COLUMN_USAGE AS kcu
        WHERE
            kcu.TABLE_SCHEMA = DATABASE()
            AND kcu.REFERENCED_TABLE_NAME IS NOT NULL;
        """
    }

def get_postgresql_schema(credentials):
    try:
        conn = psycopg2.connect(
            host=credentials['db_host'],
            user=credentials['db_user'],
            password=credentials['db_password'],
            dbname=credentials['db_name']
        )
        queries = get_postgresql_queries()
        results = execute_schema_queries(conn, queries)
        if results:
            return format_schema(results['columns'], results['primary_keys'], results['foreign_keys'])
        else:
            return None
    except Exception as e:
        logger.error(f"Error al obtener el esquema de PostgreSQL: {e}")
        return None

def get_mysql_schema(credentials):
    try:
        conn = mysql.connector.connect(
            host=credentials['db_host'],
            user=credentials['db_user'],
            password=credentials['db_password'],
            database=credentials['db_name']
        )
        queries = get_mysql_queries()
        results = execute_schema_queries(conn, queries)
        if results:
            return format_schema(results['columns'], results['primary_keys'], results['foreign_keys'])
        else:
            return None
    except Exception as e:
        logger.error(f"Error al obtener el esquema de MySQL: {e}")
        return None

def get_db_schema(credentials):
    db_type = credentials.get("db_type", "postgresql")
    if db_type == "postgresql":
        return get_postgresql_schema(credentials)
    elif db_type == "mysql":
        return get_mysql_schema(credentials)
    # Agrega más condiciones según el tipo de base de datos
    else:
        logger.error(f"Tipo de base de datos no soportado: {db_type}")
        return None
