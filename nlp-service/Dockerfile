# Usar una imagen base oficial de Python
FROM python:3.8-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requerimientos y el código de la aplicación al contenedor
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    libprotobuf-dev \
    protobuf-compiler \
    git \
    && apt-get clean
# Instalar las dependencias pequeñas
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


# Comando para correr la aplicación
CMD ["python", "nlp_service.py"]
