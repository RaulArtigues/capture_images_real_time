from src.image_quality.managers.analyze_image_real_time import AnalyzeImageRealTime
from src.image_quality.managers.analyze_image_gallery import AnalyzeImageGallery
from flask import Flask, render_template
import os

app = Flask(__name__, static_folder="src/static", template_folder="src/templates")
app.config['MAX_CONTENT_LENGTH'] = 20000 * 1024 * 1024
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze_image_real_time", methods=["POST"])
def analyze_image_real_time():
    """
    Endpoint para analizar la imagen enviada al servidor.
    Llama a la clase AnalyzeImageRealTime para procesar la imagen.
    """
    return AnalyzeImageRealTime.analyze_image_real_time()

@app.route("/analyze_image_gallery", methods=["POST"])
def analyze_image_gallery():
    """
    Endpoint para analizar la imagen enviada al servidor.
    Llama a la clase AnalyzeImageRealTime para procesar la imagen.
    """
    return AnalyzeImageGallery.analyze_image_gallery()

from flask import Flask, request, jsonify
from PIL import Image
from PIL.ExifTags import TAGS
import base64
import io

def extract_exif_data(image):
    """
    Extrae los metadatos EXIF de una imagen y los devuelve como un diccionario.
    """
    exif_data = image._getexif()
    if not exif_data:
        return {}

    metadata = {}
    for tag, value in exif_data.items():
        decoded_tag = TAGS.get(tag, tag)
        metadata[decoded_tag] = value

    return metadata

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Endpoint para procesar imágenes redimensionadas y en Base64.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No se encontró el archivo de imagen"}), 400

    # Leer la imagen redimensionada
    file = request.files['image']
    try:
        resized_image = Image.open(file)
        resized_metadata = extract_exif_data(resized_image)

        # Leer la imagen en Base64 (opcional)
        base64_data = request.form.get('image_base64', None)
        if base64_data:
            decoded_image = Image.open(io.BytesIO(base64.b64decode(base64_data)))
            base64_metadata = extract_exif_data(decoded_image)
        else:
            base64_metadata = {}

        return jsonify({
            "resized_metadata": resized_metadata,
            "base64_metadata": base64_metadata,
            "message": "Imágenes procesadas exitosamente."
        })
    except Exception as e:
        return jsonify({"error": f"Error al procesar la imagen: {str(e)}"}), 500
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)