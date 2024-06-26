# SmartQuery

SmartQuery es una aplicación avanzada que permite generar consultas SQL a partir de lenguaje natural utilizando varios microservicios desplegados con Docker y Docker Compose.

## Descripción

Este proyecto demuestra la capacidad de convertir consultas en lenguaje natural a SQL utilizando una serie de microservicios que se comunican entre sí mediante RabbitMQ. La arquitectura incluye servicios para procesamiento de lenguaje natural, validación, ejecución de consultas, y formateo de resultados, todo respaldado por una base de datos PostgreSQL.

## Arquitectura del Proyecto

- **API Gateway**: Recibe las solicitudes POST desde el frontend y distribuye las consultas a los microservicios correspondientes. Además, espera respuestas del servicio de formateo para enviarlas de vuelta al frontend.
- **NLP Service**: Procesa el lenguaje natural y genera consultas SQL.
- **Validation Service**: Valida las consultas SQL generadas.
- **Execution Service**: Ejecuta las consultas SQL en la base de datos PostgreSQL.
- **Formatting Service**: Formatea los resultados de las consultas para su presentación.
- **Frontend**: Interfaz de usuario desarrollada en React para interactuar con el sistema.
- **Database (PostgreSQL)**: Almacena los datos.
- **RabbitMQ**: Sistema de mensajería para la comunicación entre microservicios.

## Despliegue

### Prerrequisitos

- Docker
- Docker Compose

### Instalación

1. Clona el repositorio:

    ```bash
    git clone https://github.com/riemann-def/SmartQuery.git
    cd SmartQuery
    ```

2. Crea un archivo `.env` en el directorio `nlp-service` con tu clave de API de OpenAI:

    ```env
    OPENAI_API_KEY=tu-clave-api
    ```

3. Construye y levanta los contenedores:

    ```bash
    docker-compose up --build
    ```

### Uso

1. Accede al frontend en tu navegador web:

    ```
    http://localhost:8005
    ```

2. Ingresa tu consulta en lenguaje natural y presiona "Search".

3. Los resultados de la consulta SQL se mostrarán en la interfaz.

## Estructura del Proyecto

- `api-gateway`: Contiene el código para el servicio de puerta de enlace de la API.
- `nlp-service`: Contiene el código para el servicio de procesamiento de lenguaje natural.
- `validation-service`: Contiene el código para el servicio de validación de consultas.
- `execution-service`: Contiene el código para el servicio de ejecución de consultas.
- `formatting-service`: Contiene el código para el servicio de formateo de resultados.
- `frontend`: Contiene el código para el servicio de frontend.
- `common`: Contiene módulos y utilidades comunes para compartir entre servicios.
- `db-init`: Contiene scripts SQL para la inicialización de la base de datos.

## Variables de Entorno

- `RABBITMQ_HOST`: Host de RabbitMQ (usualmente `rabbitmq` en el contexto de Docker Compose).
- `DB_HOST`: Host de la base de datos PostgreSQL.
- `DB_USER`: Usuario de la base de datos.
- `DB_PASSWORD`: Contraseña de la base de datos.
- `DB_NAME`: Nombre de la base de datos.
- `OPENAI_API_KEY`: Clave API para el acceso a OpenAI (en el servicio NLP).

## Esquema de la Base de Datos

El esquema de la base de datos está diseñado para gestionar una ticketera de ocio nocturno y consta de las siguientes tablas:

- **Usuarios**: Almacena información sobre los usuarios registrados, incluyendo su nombre, correo electrónico y fecha de registro.
- **Locales**: Contiene detalles sobre los locales, como su nombre, dirección, capacidad, teléfono y correo electrónico.
- **Eventos**: Registra los eventos que se llevarán a cabo en los locales, incluyendo el nombre del evento, descripción, fecha, hora y una referencia al local.
- **Entradas**: Guarda información sobre las entradas vendidas para los eventos, incluyendo el precio y la fecha de compra, y referencias a los usuarios y eventos correspondientes.
- **Artistas**: Almacena información sobre los artistas, incluyendo su nombre, género y país de origen.
- **Eventos_Artistas**: Relaciona los eventos con los artistas que participan en ellos.
- **Opiniones**: Recoge las opiniones de los usuarios sobre los eventos, incluyendo la puntuación y el comentario.
- **Categorías**: Define las categorías de eventos, como conciertos, fiestas, festivales, etc.
- **Eventos_Categorias**: Relaciona los eventos con sus categorías correspondientes.

Cada tabla está relacionada de manera que se puedan realizar consultas complejas para obtener información significativa sobre los eventos y las entradas vendidas. Esto permite generar consultas SQL específicas y detalladas a partir de lenguaje natural.


## Contribuciones

Las contribuciones son bienvenidas. Por favor sigue los siguientes pasos para contribuir:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature-nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Haz push a la rama (`git push origin feature-nueva-funcionalidad`).
5. Abre un Pull Request.

## Problemas Comunes

### Error: `Object of type Decimal is not JSON serializable`

Este error ocurre cuando se intenta serializar un objeto `Decimal` directamente. Asegúrate de convertir los objetos `Decimal` a `float` antes de la serialización.

### Error: `Object of type date is not JSON serializable`

Este error ocurre cuando se intenta serializar un objeto `date` directamente. Asegúrate de convertir los objetos `date` a `str` en formato ISO antes de la serialización.

## Contacto

Para cualquier pregunta o problema, puedes contactarme a través de [tu-email@example.com](mailto:tu-email@example.com).

---

Este proyecto utiliza [OpenAI](https://openai.com) para la generación de consultas SQL a partir de lenguaje natural.
