# Usar una imagen base de Python
FROM python:3.9-slim

# Configurar el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos requeridos
COPY . /app

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de Flask
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]
