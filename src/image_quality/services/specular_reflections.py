from src.image_quality.utils.properties import SpecularReflectionsProperties
from typing import Dict, Any
import numpy as np
import logging
import time
import cv2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class SpecularReflections:
    """
    Clase para detectar reflejos especulares en imágenes.
    """
    def __init__(self):
        """
        Inicializa los parámetros predeterminados para la detección de reflejos especulares.
        """
        self.intensity_threshold = SpecularReflectionsProperties.intensity_threshold
        self.saturation_threshold = SpecularReflectionsProperties.saturation_threshold
        self.min_region_size = SpecularReflectionsProperties.min_region_size
        self.sensitivity = SpecularReflectionsProperties.sensitivity

    def detect_specular_reflections(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Detecta reflejos especulares en una imagen y calcula un puntaje para determinar su validez.

        :param image: Imagen en formato OpenCV (numpy array).
        :return: Diccionario con el puntaje de reflejo especular y si es válido.
        """
        start_time = time.time()
        if image is None or not isinstance(image, np.ndarray):
            logging.error("La imagen proporcionada no es válida. Se esperaba un numpy array no vacío.")
            return self.error_result_specular_reflections(start_time)

        try:
            image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            canal_h, canal_s, canal_v = cv2.split(image_hsv)

            _, mask_intensity = cv2.threshold(canal_v, self.intensity_threshold, 255, cv2.THRESH_BINARY)
            _, mask_saturation = cv2.threshold(canal_s, self.saturation_threshold, 255, cv2.THRESH_BINARY_INV)

            mask_specular = cv2.bitwise_and(mask_intensity, mask_saturation)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask_refined = cv2.morphologyEx(mask_specular, cv2.MORPH_CLOSE, kernel)

            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_refined, connectivity=8)
            mask_final = np.zeros_like(mask_refined)
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area >= self.min_region_size:
                    mask_final[labels == i] = 255

            total_pixels = canal_v.size
            specular_pixels = np.count_nonzero(mask_final)
            specular_score = (specular_pixels / total_pixels) * 100

            is_correct_specular_reflections = specular_score < float(self.sensitivity)
            
            logging.info(f"Reflexión Especular: {specular_score:.2f}%. La imagen "
             f"{'cumple' if is_correct_specular_reflections else 'no cumple'} "
             f"con el umbral Especular ({float(self.sensitivity)}).")

            end_time = time.time()
            elapsed_time_seconds = round(end_time - start_time, 4)
            elapsed_time_milliseconds = int((end_time - start_time) * 1000)
            logging.info(f"Tiempo de procesamiento en Specular Reflection: {elapsed_time_seconds}s ({elapsed_time_milliseconds}ms)")

            return {
                "specular_score": specular_score,
                "is_correct_specular_reflections": is_correct_specular_reflections,
                "is_valid": True
            }

        except cv2.error as e:
            logging.error(f"Error de OpenCV durante el análisis: {e}", exc_info=True)
            return self.error_result_specular_reflections(start_time)
        except Exception as e:
            logging.error(f"Error inesperado al analizar los reflejos especulares: {e}", exc_info=True)
            return self.error_result_specular_reflections(start_time)

    @staticmethod
    def error_result_specular_reflections(start_time: float) -> Dict[str, Any]:
        """
        Genera un resultado de error estándar.

        :return: Diccionario con resultados indicando que el análisis falló.
        """
        end_time = time.time()
        elapsed_time_seconds = round(end_time - start_time, 4)
        elapsed_time_milliseconds = int((end_time - start_time) * 1000)
        logging.error(f"Error en el análisis de Reflexión Especular. Tiempo transcurrido: "
                      f"{elapsed_time_seconds}s ({elapsed_time_milliseconds}ms)")
        return {
            "specular_score": None,
            "is_correct_specular_reflections": False,
            "is_valid": False
        }