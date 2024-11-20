from src.modules.image_quality.quality_evaluator import QualityEvaluator
from src.modules.image_quality.image_processor import ImageProcessor
from src.modules.image_quality.shaperness import SharpnessAnalyzer
from src.modules.image_quality.exposure import ExposureAnalyzer
from src.modules.image_quality.response_handler import ResponseHandler
from flask import Flask, request, jsonify, render_template
import logging
import time
import os

logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder="src/static", template_folder="src/templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze_image", methods=["POST"])
def analyze_image():
    """
    Procesa la imagen enviada en formato Base64, calcula la calidad utilizando varias métricas (NIQE, PIQA, BRISQUE)
    y devuelve los resultados junto con las métricas básicas como nitidez, exposición y resolución.
    """
    start_time = time.time()
    data = request.get_json()
    image_base64 = data.get("image", "")

    if not image_base64:
        return jsonify({"error": "La imagen en Base64 está vacía"}), 400

    # Inicialización de evaluadores y procesadores
    processor = ImageProcessor()
    evaluator_niqe = QualityEvaluator("NIQE")
    evaluator_piqa = QualityEvaluator("PIQA")

    try:
        # Redimensionar y guardar la imagen
        resized_image_base64, saved_path, resized_image, image_id, original_dims, resized_dims = processor.resize_and_save_image(image_base64, return_decoded=True)
        if resized_image is None:
            raise ValueError("Error al redimensionar o guardar la imagen.")
    except Exception as e:
        logging.error(f"Error durante el procesamiento de la imagen: {e}")
        return jsonify({"error": "Error al procesar la imagen"}), 400

    try:
        # Análisis de métricas básicas
        sharpness = SharpnessAnalyzer.analyze(resized_image)
        exposure = ExposureAnalyzer.analyze(resized_image)

        # Evaluación de calidad avanzada
        niqe_results = evaluator_niqe.evaluate_image_quality(resized_image_base64)
        piqa_results = evaluator_piqa.evaluate_image_quality(resized_image_base64)

         # Medir el tiempo de procesamiento
        elapsed_time_seconds = time.time() - start_time
        elapsed_time_milliseconds = elapsed_time_seconds * 1000

        # Consolidar resultados
        results = {
            "image_id": image_id,
            "original_dimensions": {"width": original_dims[0], "height": original_dims[1]},
            "resized_dimensions": {"width": resized_dims[0], "height": resized_dims[1]},
            "sharpness": sharpness,
            "exposure": exposure,
            "niqe": niqe_results,
            "piqa": piqa_results,
            "saved_path": saved_path,
            "processing_time_seconds": round(elapsed_time_seconds, 4),
            "processing_time_milliseconds": round(elapsed_time_milliseconds, 2)
        }

        # Convertir a resultados serializables por JSON
        native_results = processor.convert_to_native(results)

        # Guardar en archivo JSON
        handler = ResponseHandler()
        handler.save_response(native_results)

        return jsonify(native_results)

    except Exception as e:
        logging.error(f"Error durante el análisis de la imagen: {e}")
        return jsonify({"error": "Error durante el análisis de la imagen"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)