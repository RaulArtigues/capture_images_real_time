from src.image_quality.services.specular_reflections import SpecularReflections
from src.image_quality.processors.response_handler import ResponseHandler
from src.image_quality.processors.image_processor import ImageProcessor
from src.image_quality.processors.client_metadata import client_metadata
from src.image_quality.utils.properties import ResponseHandlerPaths
from src.image_quality.services.sharpness import SharpnessAnalyzer
from src.image_quality.services.exposure import ExposureAnalyzer
from src.image_quality.processors.client_info import client_info
from flask import request, jsonify
from typing import Dict, Any
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class AnalyzeImageGallery:
    """
    Clase para analizar imágenes desde Galería.
    """
    @staticmethod
    def analyze_image_gallery() -> Any:
        """
        Procesa la imagen adjuntada en formato Base64, realiza análisis de métricas
        y devuelve los resultados.

        :return: Respuesta JSON con los resultados o un diccionario de error.
        """
        client_data = client_info()
        start_time = time.time()
        data = request.get_json()
        image_base64 = data.get("image", "")
        metadata = client_metadata()

        if not image_base64:
            elapsed_time_seconds = time.time() - start_time
            elapsed_time_milliseconds = elapsed_time_seconds * 1000
            empty_results = AnalyzeImageGallery.error_analyze_image_gallery(client_data, elapsed_time_seconds, elapsed_time_milliseconds)
            return jsonify(empty_results), 400

        processor = ImageProcessor()
        try:
            processor_result = processor.resize_and_save_image(image_base64, return_decoded=True)

            if not processor_result or not processor_result.get("is_valid", False):
                logging.error("El resultado del procesador indica un error.")
                elapsed_time_seconds = time.time() - start_time
                elapsed_time_milliseconds = elapsed_time_seconds * 1000
                empty_results = AnalyzeImageGallery.error_analyze_image_gallery(client_data, elapsed_time_seconds, elapsed_time_milliseconds)
                return jsonify(empty_results), 400

            resized_image = processor_result.get("resized_image")
            image_id = processor_result.get("image_id")
            original_dims = processor_result.get("original_dimensions")
            resized_dims = processor_result.get("resized_dimensions")
            saved_path = processor_result.get("image_path")

        except Exception as e:
            logging.error(f"Error durante el procesamiento de la imagen: {e}")
            elapsed_time_seconds = time.time() - start_time
            elapsed_time_milliseconds = elapsed_time_seconds * 1000
            empty_results = AnalyzeImageGallery.error_analyze_image_gallery(client_data, elapsed_time_seconds, elapsed_time_milliseconds)
            return jsonify(empty_results), 400

        try:
            sharpness = SharpnessAnalyzer().detect_sharpness(resized_image)
            exposure = ExposureAnalyzer().detect_exposure(resized_image)
            specular_reflections = SpecularReflections().detect_specular_reflections(resized_image)

        except Exception as e:
            logging.error(f"Error durante el análisis en una de las métricas: {e}")
            elapsed_time_seconds = time.time() - start_time
            elapsed_time_milliseconds = elapsed_time_seconds * 1000
            empty_results = AnalyzeImageGallery.error_analyze_image_gallery(client_data, elapsed_time_seconds, elapsed_time_milliseconds)
            return jsonify(empty_results), 400

        elapsed_time_seconds = time.time() - start_time
        elapsed_time_milliseconds = elapsed_time_seconds * 1000
        logging.info(f"Tiempo de procesamiento en Analyze Image Gallery: {elapsed_time_seconds}s ({elapsed_time_milliseconds}ms)")

        results_analyze_image_gallery = {
            "client_info": client_data,
            "metadata": metadata,
            "image_id": image_id,
            "original_dimensions": {"width": original_dims[0], "height": original_dims[1]},
            "resized_dimensions": {"width": resized_dims[0], "height": resized_dims[1]},
            "sharpness": sharpness,
            "exposure": exposure,
            "specular_reflections": specular_reflections,
            "saved_path": saved_path,
            "processing_time_seconds": round(elapsed_time_seconds, 4),
            "processing_time_milliseconds": round(elapsed_time_milliseconds, 2),
            "is_valid": True
        }

        try:
            response_handler = ResponseHandler(ResponseHandlerPaths.responses_hander_images_gallery)
            results_analyze_image_gallery = response_handler.convert_to_native(results_analyze_image_gallery)
            response_handler.save_response(results_analyze_image_gallery)

        except Exception:
            elapsed_time_seconds = time.time() - start_time
            elapsed_time_milliseconds = elapsed_time_seconds * 1000
            empty_results = AnalyzeImageGallery.error_analyze_image_gallery(client_data, elapsed_time_seconds, elapsed_time_milliseconds)
            return jsonify(empty_results), 500

        return jsonify(results_analyze_image_gallery)
    

    @staticmethod
    def error_analyze_image_gallery(client_data: Dict[str, Any], elapsed_time_seconds: float, elapsed_time_milliseconds: float) -> Dict[str, Any]:
        """
        Genera un diccionario estándar con todos los campos en None para los errores.

        :param client_data: Información del cliente.
        :param elapsed_time_seconds: Tiempo total de procesamiento en segundos.
        :param elapsed_time_milliseconds: Tiempo total de procesamiento en milisegundos.
        :return: Diccionario de resultados con valores None indicando un error.
        """
        return {
            "client_info": client_data,
            "metadata": None,
            "image_id": None,
            "original_dimensions": {"width": None, "height": None},
            "resized_dimensions": {"width": None, "height": None},
            "sharpness": None,
            "exposure": None,
            "specular_reflections": None,
            "saved_path": None,
            "processing_time_seconds": round(elapsed_time_seconds, 4),
            "processing_time_milliseconds": round(elapsed_time_milliseconds, 2),
            "is_valid": False
        }