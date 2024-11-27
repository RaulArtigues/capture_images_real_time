from src.image_quality.utils.properties import SharpnessProperties
from typing import Optional, Dict, Any
import numpy as np
import logging
import time
import cv2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class SharpnessAnalyzer:
    """
    Clase para analizar la nitidez de imágenes.
    """
    def __init__(self, default_threshold: Optional[float] = None):
        """
        Inicializa el analizador con un umbral de nitidez predeterminado.

        :param default_threshold: Umbral de nitidez predeterminado.
        """
        self.default_threshold = default_threshold or SharpnessProperties.default_threshold_sharpness

    def detect_sharpness(self, image: Any, threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Analiza la nitidez de la imagen y determina si es válida.

        :param image: Imagen en formato OpenCV (numpy array).
        :param threshold: Umbral opcional para considerar una imagen como nítida.
        :return: Diccionario con el valor de nitidez, si la nitidez es correcta,
                 y si el proceso fue exitoso (is_valid).
        """
        start_time = time.time()
        if image is None or not isinstance(image, (np.ndarray,)):
            logging.error("La imagen proporcionada es inválida. Se esperaba un numpy array no vacío.")
            return self.error_result_sharpness(start_time)

        threshold = threshold or self.default_threshold

        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

            is_correct_sharpness = sharpness >= threshold
            if is_correct_sharpness:
                logging.info(f"Nitidez (Varianza Laplaciano): {sharpness}. La imagen cumple con el umbral de nitidez.({threshold}).")
            else:
                logging.warning(f"Nitidez (Varianza Laplaciano): {sharpness}. La imagen no cumple con el umbral de nitidez ({threshold}).")

            end_time = time.time()
            elapsed_time_seconds = round(end_time - start_time, 4)
            elapsed_time_milliseconds = int((end_time - start_time) * 1000)
            logging.info(f"Tiempo de procesamiento en Sharpness: {elapsed_time_seconds}s ({elapsed_time_milliseconds}ms)")

            return {
                "sharpness_value": sharpness,
                "is_correct_sharpness": is_correct_sharpness,
                "is_valid": True
            }

        except Exception as e:
            logging.error(f"Error inesperado al analizar la nitidez: {e}", exc_info=True)
            return self.error_result_sharpness(start_time)
        
    @staticmethod
    def error_result_sharpness(start_time: float) -> Dict[str, Any]:
        """
        Genera un resultado de error estándar.

        :return: Diccionario con resultados indicando que el análisis falló.
        """
        end_time = time.time()
        elapsed_time_seconds = round(end_time - start_time, 4)
        elapsed_time_milliseconds = int((end_time - start_time) * 1000)
        logging.error(f"Error en el análisis de Nitidez. Tiempo transcurrido: "
                      f"{elapsed_time_seconds}s ({elapsed_time_milliseconds}ms)")
        return {
            "sharpness_value": None,
            "is_correct_sharpness": False,
            "is_valid": False
        }