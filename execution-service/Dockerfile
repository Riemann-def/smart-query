# Usar una imagen base oficial de Python
FROM python:3.8-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requerimientos y el código de la aplicación al contenedor
COPY requirements.txt .

# Instalar las dependencias
RUN apt-get update && \
    apt-get install -y libpq-dev && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación al contenedor
COPY . .


# Comando para correr la aplicación
CMD ["python", "execution_service.py"]
