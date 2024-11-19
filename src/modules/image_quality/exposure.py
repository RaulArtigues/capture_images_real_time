from src.utils import properties
import numpy as np
import logging
import cv2

logging.basicConfig(level=logging.INFO)

class ExposureAnalyzer:
    @staticmethod
    def analyze(image, thresholds=None):
        """
        Analiza la exposición de una imagen para determinar el porcentaje de píxeles
        sobreexpuestos y subexpuestos, y valida si la exposición es aceptable.

        :param image: Imagen en formato BGR.
        :param thresholds: Diccionario con umbrales de exposición opcionales.
        :return: Diccionario con los resultados de la exposición.
        """
        if image is None:
            logging.error("La imagen proporcionada es inválida (None).")
            return None

        try:
            # Cargar umbrales
            thresholds = thresholds or properties.default_thresholds_exposure
            overexposed_threshold = thresholds["overexposed_threshold"]
            underexposed_threshold = thresholds["underexposed_threshold"]
            tolerance = thresholds["tolerance"]

            # Convertir la imagen a escala de grises si no lo está
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Calcular porcentaje de píxeles sobreexpuestos y subexpuestos
            total_pixels = gray.size
            overexposed_count = np.sum(gray >= overexposed_threshold)
            underexposed_count = np.sum(gray <= underexposed_threshold)

            overexposed_percentage = round((overexposed_count / total_pixels) * 100, 2)
            underexposed_percentage = round((underexposed_count / total_pixels) * 100, 2)

            # Determinar validez de sobreexposición y subexposición por separado
            is_overexposed_valid = overexposed_percentage < (tolerance * 100)
            is_underexposed_valid = underexposed_percentage < (tolerance * 100)

            # Exposición general válida solo si ambas métricas son válidas
            is_valid = is_overexposed_valid and is_underexposed_valid

            # Resultados
            results = {
                "overexposed_percentage": overexposed_percentage,
                "underexposed_percentage": underexposed_percentage,
                "is_overexposed_valid": is_overexposed_valid,
                "is_underexposed_valid": is_underexposed_valid,
                "is_valid": is_valid
            }

            # Logging
            logging.info(
                f"Exposición analizada: Sobreexpuesto={overexposed_percentage}%, "
                f"Subexpuesto={underexposed_percentage}%, "
                f"Válido (general)={is_valid}, "
                f"Válido (sobreexpuesto)={is_overexposed_valid}, "
                f"Válido (subexpuesto)={is_underexposed_valid}"
            )

            return results

        except Exception as e:
            logging.error(f"Error al analizar la exposición: {e}")
            return None