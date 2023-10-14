import ffmpeg
from flask import Flask, request, send_file
import os
from urllib.parse import urlparse, parse_qs
import tempfile

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def process_file():

    if request.method == 'GET':
        host = request.host
        return f"""<h1>API de conversión de archivos de audio</h1>
<p>Parámetros del método <b>POST</b>: <b>file</b> que será el archivo que se quiere convertir.</p>
<p>Se admite varios parámetros en la url para la configuración de salida deseada:</p>
<ul>
<li><b>frecuencia</b>: Especifica la frecuencia de muestreo del audio. Los valores admitidos son (en khz): 8, 11, 22 y 44, o se puede poner el valor real: 22050. Si no se proporciona este parámetro, se utilizará el valor predeterminado de 22khz.</li>
<li><b>canales</b>: Especifica el número de canales de audio. Los valores admitidos son: 1 para mono o 2 para estéreo. Si no se proporciona este parámetro, se utilizará el valor predeterminado de 1 (mono).</li>
<li><b>kbps</b>: Especifica la tasa de bits de audio en kilobits por segundo. Este parámetro controla la calidad de la compresión del audio. Si no se proporciona este parámetro, se utilizará el valor predeterminado de 24 kbps.</li>
</ul>
<p>Ejemplo:</p>
<p>{host}/?frecuencia=22&canales=2&kbps=128k</p>
"""

    elif request.method == 'POST':
          
        if 'file' not in request.files:
            return "No se proporcionó un archivo en la solicitud.", 400

        try:
            # Obtener la URL completa de la solicitud
            url = request.url

            # Analizar la URL y extraer los parámetros
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)

            # Obtener los valores de los parámetros
            frecuencia = params.get('frecuencia', ['22050'])[0]
            if frecuencia == '8':
                frecuencia = '8000'  
            elif frecuencia == '11':
                frecuencia = '11025' 
            elif frecuencia == '22':
                frecuencia = '22050'  
            elif frecuencia == '44':
                frecuencia = '44100'  
            canales = params.get('canales', ['1'])[0]
            kbps = params.get('kbps', ['24k'])[0]

            temp_dir = tempfile.gettempdir()
            
            # Guardar el archivo de audio en el disco
            file = request.files['file']
            filename = file.filename  # Obtener el nombre original del archivo
            input_file_path =  os.path.join(temp_dir, filename.replace(" ", "_"))
            file.save(input_file_path)

            # Definir el nombre y ruta de destino para el archivo convertido
            output_file_path = os.path.join(temp_dir, f'converted_{os.path.splitext(filename)[0].replace(" ", "_")}.mp3')

            print (input_file_path)
            print (output_file_path)
            
            if not os.path.exists(input_file_path):
                return "El archivo no se pudo copiar.", 400

            # Utilizar ffmpeg para realizar la conversión
            ffmpeg.input(input_file_path).output(output_file_path,
                                        format='mp3',
                                        audio_bitrate=kbps,
                                        ac=int(canales),
                                        ar=frecuencia,
                                        sample_fmt='s16',
                                        dither_method='triangular_hp').overwrite_output().run()
            
            
            if not os.path.exists(output_file_path):
                return "El archivo no se pudo generar.", 400

            # Eliminar el archivo original después de la conversión
            os.remove(input_file_path)

            # Devolver el archivo convertido como respuesta para descarga
            return send_file(output_file_path, as_attachment=True)

        except Exception as e:
            return f"Ocurrió un error durante el procesamiento del archivo: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)