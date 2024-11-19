# Usa una imagen base de Python ligera
FROM python:3.10-slim

# Establecer directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    llvm \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt al contenedor
COPY requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación al contenedor
COPY . /app/

# Exponer el puerto en el que Flask servirá la aplicación
EXPOSE 5001

# Establecer el comando para ejecutar la aplicación
CMD ["python", "app.py"]