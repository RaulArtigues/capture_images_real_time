FROM python:3.10-slim

# Actualizar e instalar las herramientas necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    llvm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear y activar un entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar wheel antes de las dependencias
RUN pip install --upgrade pip wheel

# Copiar los archivos del proyecto
WORKDIR /app
COPY . .

# Instalar las dependencias del proyecto
RUN pip install -r requirements.txt

# Exponer el puerto de la aplicación
EXPOSE 5001

# Comando para iniciar la aplicación
CMD ["python", "app.py"]