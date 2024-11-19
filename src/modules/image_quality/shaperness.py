from src.utils import properties
import logging
import cv2

logging.basicConfig(level=logging.INFO)

class SharpnessAnalyzer:
    @staticmethod
    def analyze(image, threshold=None):
        """
        Analiza la nitidez de la imagen y determina si es válida.

        :param image: Imagen en formato OpenCV (numpy array).
        :param threshold: Umbral para determinar si la nitidez es válida. Si no se proporciona, se usa el valor por defecto.
        :return: Un diccionario con el valor de nitidez y si es válido o no.
        """
        if threshold is None:
            threshold = properties.default_sharpness_threshold

        try:
            # Convertir la imagen a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Calcular la nitidez utilizando la varianza del Laplaciano
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            logging.info(f"Nitidez (varianza Laplaciano): {sharpness}")

            # Determinar si la imagen cumple con el umbral de nitidez
            is_valid = sharpness >= threshold
            return {
                "sharpness_value": sharpness,
                "is_valid": is_valid
            }
        except Exception as e:
            logging.error(f"Error al analizar la nitidez: {e}")
            return {
                "sharpness_value": None,
                "is_valid": False
            }