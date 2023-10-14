# Resumen del Proyecto

El objetivo de este proyecto es desarrollar una imagen Docker que aproveche la potencia de python-ffmpeg para la conversión de audios.

La versatilidad del contenedor Docker permitirá su fácil implementación en Google Cloud Run, lo que permitirá a los usuarios enviar archivos Word mediante comandos POST a través de la API. A cambio, recibirán el audio convertido en formato .mp3

# Parámetros en url

Parámetros del método <b>POST</b>: <b>file</b> que será el archivo que se quiere convertir.

Se admite varios parámetros en la url para la configuración de salida deseada:
**frecuencia**: Especifica la frecuencia de muestreo del audio. Los valores admitidos son (en khz): 8, 11, 22 y 44. Si no se proporciona este parámetro, se utilizará el valor predeterminado de 22khz.

**canales**: Especifica el número de canales de audio. Los valores admitidos son: 1 para mono o 2 para estéreo. Si no se proporciona este parámetro, se utilizará el valor predeterminado de 1 (mono).

**kbps**: Especifica la tasa de bits de audio en kilobits por segundo. Este parámetro controla la calidad de la compresión del audio. Si no se proporciona este parámetro, se utilizará el valor predeterminado de 16 kbps.

Ejemplo:

http://www.miservicio.com:8080/?frecuencia=22&canales=2&kbps=128k


# Pasos a seguir para generar el contenedor Docker

Para lograr esto, necesitas crear un Dockerfile que contenga los componentes necesarios para realizar la conversión. Luego, puedes implementar este Dockerfile en Google Cloud Run. A continuación, te guiaré a través de los pasos para crear el Dockerfile y construir la imagen Docker:

## Paso 1: Construir la imagen Docker 

Los archivos "Dockerfile", “app.py” y “requirements.txt” han de estar en la misma carpeta, en la que ejecutaremos el siguiente comando para construir la imagen Docker:

> docker build -t audio_converter .

Esto construirá la imagen con el nombre "audio_converter".

## Paso 2: Ejecutar la imagen localmente (opcional)

Antes de implementar la imagen en Google Cloud Run, puedes probarla localmente para asegurarte de que funciona correctamente. Para hacerlo, ejecuta:

> docker run -it -p 5000:5000 audio_converter

Esto arrancará el servidor API REST en el puerto 5000.

Ahora puedes probar la API REST usando Postman o una herramienta similar.

## Paso 3: (opcional) Instalar la consola de Google Cloud

Instala, si acaso no lo tienes todavía, la consola de Google Cloud. Sigue los pasos indicados en:

<https://cloud.google.com/sdk/docs/install?hl=es-419>

## Paso 4: Preparar el proyecto y las APIS en Google cloud

Primero debes crear un proyecto en Google Cloud. Una vez lo hayas creado debes habilitar la API de Google Cloud Run, y de Artifacts.

Habilita la API de artifacts desde [Google Cloud Console](https://console.cloud.google.com/flows/enableapi?apiid=artifactregistry.googleapis.com&hl=es-419) o con el siguiente comando gcloud:

> gcloud services enable artifactregistry.googleapis.com

## Paso 5: Creamos un repositorio para las imágenes Docker

Crearemos un repositorio en artifacts en una de las regiones:

> gcloud artifacts repositories create REPO_NAME --repository-format=docker --location=REGION

Por ejemplo:

> gcloud artifacts repositories create services --repository-format=docker --location=us-west1

En este caso hemos creado un repositorio llamado ‘services’ en la región us-west1.

## Paso 6: Subir la imagen de Docker a Artifact Registry

Etiquetar la imagen con la dirección del repositorio de Artifact Registry: La dirección del repositorio de Artifact Registry se encuentra en el formato: REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME. Asegúrate de tener el SDK de Google Cloud instalado y haber iniciado sesión con tu cuenta de GCP.

> docker tag audio_converter REGION-docker.pkg.dev/TU_PROYECTO_ID/REPO_NAME/nombre-de-la-app

Reemplaza REGION con la región donde esté ubicado tu repositorio de Artifact Registry, TU_PROYECTO_ID con el ID de tu proyecto de GCP, REPO_NAME con el nombre del repositorio de Artifact Registry donde deseas almacenar la imagen y nombre-de-la-app por el nombre que deseas para tu imagen en Artifact Registry.

Por ejemplo:

> docker tag audio_converter us-west1-docker.pkg.dev/TU_PROYECTO_ID/services/audio_converter

## Paso 7: Iniciar sesión en Artifact Registry

Antes de subir la imagen, debes iniciar sesión con la herramienta de línea de comandos de Docker para que pueda autenticarse en Artifact Registry.

> gcloud auth configure-docker REGION-docker.pkg.dev

Reemplaza REGION con la región correspondiente donde está ubicado tu repositorio de Artifact Registry.

## Paso 8: Subir la imagen al repositorio

Subir la imagen a Artifact Registry: Utiliza el comando docker push para enviar la imagen etiquetada a Artifact Registry.

> docker push REGION-docker.pkg.dev/TU_PROYECTO_ID/REPO_NAME/nombre-de-la-app

Reemplaza nuevamente REGION, TU_PROYECTO_ID, REPO_NAME y nombre-de-la-app por los valores correspondientes.

Por ejemplo:

> docker push us-west1-docker.pkg.dev/TU_PROYECTO_ID/services/audio_converter

## Paso 9: Desplegar la imagen de en Google Cloud Run

Para desplegar la imagen del Docker en Google Cloud Run usa el comando:

> gcloud run deploy --image=REGION-docker.pkg.dev/TU_PROYECTO_ID/REPO_NAME/nombre-de-la-app --platform=managed --allow-unauthenticated

Ejemplo:

> gcloud run deploy --image=us-west1-docker.pkg.dev/TU_PROYECTO_ID/services/audio_converter --platform=managed --allow-unauthenticated

Esto va a darnos una salida de este estilo:

> Deploying container to Cloud Run service [wordtomd] in project [tseyor2023] region [us-west1]
>
> OK Deploying... Done.
>
> OK Creating Revision...
>
> OK Routing traffic...
>
> OK Setting IAM Policy...
>
> Done.
>
> Service [audioconvert] revision [audioconvert-00001-loz] has been deployed and is serving 100 percent of traffic.
>
> Service URL: https://audioconvert-zpzbiu7ooq-uw.a.run.app

Ahora podemos acceder al servicio según la URL indicada finalmente.

Una vez que el servicio esté desplegado, podrás llamarlo desde tu aplicación enviando un comando POST con el archivo de audio en el campo ‘file’ y recibirás el archivo convertido resultante en formato mp3 en la respuesta.
