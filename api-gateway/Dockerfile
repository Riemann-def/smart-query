# Usar una imagen base oficial de Python
FROM python:3.8-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requerimientos
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación y el módulo de utilidad al contenedor
COPY . .

# Exponer el puerto en el que correrá la aplicación
EXPOSE 8000

# Comando para correr la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
