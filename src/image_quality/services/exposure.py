from src.image_quality.utils.properties import ExposureProperties
from typing import Optional, Dict, Any
import numpy as np
import logging
import time
import cv2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class ExposureAnalyzer:
    """
    Clase para analizar la exposición de imágenes y determinar si cumple los umbrales aceptables.
    """
    @staticmethod
    def detect_exposure(image: np.ndarray, thresholds: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Analiza la exposición de una imagen para determinar el porcentaje de píxeles
        sobreexpuestos y subexpuestos, y valida si la exposición es aceptable.

        :param image: Imagen en formato BGR como numpy array.
        :param thresholds: Diccionario opcional con los umbrales de exposición:
                           - "overexposed_threshold": Límite superior para sobreexposición.
                           - "underexposed_threshold": Límite inferior para subexposición.
                           - "tolerance": Porcentaje máximo permitido para considerar la imagen válida.
        :return: Diccionario con los resultados del análisis y la validez del proceso (is_valid).
        """
        start_time = time.time()
        if image is None or not isinstance(image, np.ndarray):
            logging.error("La imagen proporcionada es inválida. Se esperaba un numpy array no vacío.")
            return ExposureAnalyzer.error_result_exposure(start_time)

        try:
            thresholds = thresholds or ExposureProperties.default_thresholds_exposure
            overexposed_threshold = thresholds.get("overexposed_threshold", 245)
            underexposed_threshold = thresholds.get("underexposed_threshold", 10)
            tolerance = thresholds.get("tolerance", 0.3)

            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            total_pixels = gray.size
            overexposed_count = np.sum(gray >= overexposed_threshold)
            underexposed_count = np.sum(gray <= underexposed_threshold)

            overexposed_percentage = round((overexposed_count / total_pixels) * 100, 2)
            underexposed_percentage = round((underexposed_count / total_pixels) * 100, 2)

            is_overexposed_correct = overexposed_percentage < (tolerance * 100)
            is_underexposed_correct = underexposed_percentage < (tolerance * 100)
            is_correct_exposure = is_overexposed_correct and is_underexposed_correct

            logging.info(f"SobreExposición: {overexposed_percentage}. "
             f"La imagen {'cumple' if is_overexposed_correct else 'no cumple'} "
             f"con el umbral de SobreExposición ({tolerance * 100}%).")

            logging.info(f"SubExposición: {underexposed_percentage}. "
                        f"La imagen {'cumple' if is_underexposed_correct else 'no cumple'} "
                        f"con el umbral de SubExposición ({tolerance * 100}%).")

            logging.info(f"Exposición General: {'Correcta' if is_correct_exposure else 'Incorrecta'}.")
            
            end_time = time.time()
            elapsed_time_seconds = round(end_time - start_time, 4)
            elapsed_time_milliseconds = int((end_time - start_time) * 1000)
            logging.info(f"Tiempo de procesamiento en Exposure: {elapsed_time_seconds}s ({elapsed_time_milliseconds}ms)")

            return {
                "overexposed_percentage": overexposed_percentage,
                "underexposed_percentage": underexposed_percentage,
                "is_overexposed_correct": is_overexposed_correct,
                "is_underexposed_correct": is_underexposed_correct,
                "is_correct_exposure": is_correct_exposure,
                "is_valid": True
            }

        except Exception as e:
            logging.error(f"Error al analizar la exposición: {e}", exc_info=True)
            return ExposureAnalyzer.error_result_exposure(start_time)

    @staticmethod
    def error_result_exposure(start_time: float) -> Dict[str, Any]:
        """
        Genera un resultado de error estándar e incluye el tiempo transcurrido.

        :param start_time: Tiempo inicial del proceso.
        :return: Diccionario con resultados indicando que el análisis falló.
        """
        end_time = time.time()
        elapsed_time_seconds = round(end_time - start_time, 4)
        elapsed_time_milliseconds = int((end_time - start_time) * 1000)

        logging.error(f"Error en el análisis de exposición. Tiempo transcurrido: "
                      f"{elapsed_time_seconds}s ({elapsed_time_milliseconds}ms)")

        return {
            "overexposed_percentage": None,
            "underexposed_percentage": None,
            "is_overexposed_correct": False,
            "is_underexposed_correct": False,
            "is_correct_exposure": False,
            "is_valid": False
        }