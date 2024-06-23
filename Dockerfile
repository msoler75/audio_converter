# Imagen base para el contenedor
FROM tiangolo/uwsgi-nginx-flask:python3.9

# Instalar FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Copiar los archivos necesarios al contenedor
COPY app.py requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Ejecutar la aplicación Flask
CMD ["python", "app.py"]
