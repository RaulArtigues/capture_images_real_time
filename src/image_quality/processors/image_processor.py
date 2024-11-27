from src.image_quality.utils.properties import ImageDimensionProperties
from typing import Optional, Tuple, Dict, Any
import numpy as np
import logging
import base64
import uuid
import time
import cv2
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class ImageProcessor:
    """
    Clase para procesar imágenes, incluyendo redimensionamiento y decodificación desde Base64.
    """
    def __init__(self, save_dir: str = "data/images"):
        """
        Inicializa la clase con las configuraciones predeterminadas.

        :param save_dir: Directorio donde se guardarán las imágenes procesadas.
        """
        self.target_horizontal = ImageDimensionProperties.target_horizontal
        self.target_vertical = ImageDimensionProperties.target_vertical
        self.save_dir = save_dir

    def read_image_from_base64(self, image_base64: str) -> Optional[np.ndarray]:
        """
        Decodifica una imagen en Base64 y la convierte a formato OpenCV.

        :param image_base64: Imagen codificada en Base64.
        :return: Imagen en formato OpenCV o None si falla.
        """
        if not image_base64:
            logging.error("El string de la imagen en Base64 está vacío.")
            return None

        try:
            image_data = base64.b64decode(image_base64)
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Error al decodificar la imagen.")
            return image
        except Exception as e:
            logging.error(f"Error al decodificar la imagen: {e}", exc_info=True)
            return None

    def resize_and_save_image(self, image_base64: str, return_decoded: bool = False) -> Optional[Dict[str, Any]]:
        """
        Redimensiona y guarda una imagen. Puede devolver la imagen redimensionada en Base64.

        :param image_base64: Imagen codificada en Base64.
        :param return_decoded: Si True, devuelve la imagen decodificada en OpenCV.
        :return: Diccionario con los resultados del procesamiento o None en caso de error.
        """
        start_time = time.time()

        image = self.read_image_from_base64(image_base64)
        if image is None:
            return self.error_result_image_processor(start_time)

        original_height, original_width = image.shape[:2]
        logging.info(f"Dimensiones originales de la imagen: {original_width}x{original_height}")

        target_resolution = self.target_horizontal if original_width > original_height else self.target_vertical
        target_width, target_height = target_resolution

        aspect_ratio = original_width / original_height
        if aspect_ratio > target_width / target_height:
            new_width = target_width
            new_height = int(target_width / aspect_ratio)
        else:
            new_height = target_height
            new_width = int(target_height * aspect_ratio)

        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        logging.info(f"Dimensiones de la imagen redimensionada: {new_width}x{new_height}")

        os.makedirs(self.save_dir, exist_ok=True)
        image_id = str(uuid.uuid4())
        image_path = os.path.join(self.save_dir, f"image_{image_id}.jpg")
        cv2.imwrite(image_path, resized_image)
        logging.info(f"Imagen guardada en: {image_path}")

        _, buffer = cv2.imencode('.jpg', resized_image)
        resized_image_base64 = base64.b64encode(buffer).decode('utf-8')

        end_time = time.time()
        elapsed_time_seconds = round(end_time - start_time, 4)
        elapsed_time_milliseconds = int((end_time - start_time) * 1000)

        logging.info(f"Tiempo de procesamiento en Image Processor: {elapsed_time_seconds}s ({elapsed_time_milliseconds}ms)")

        return {
            "resized_image_base64": resized_image_base64,
            "image_path": image_path,
            "resized_image": resized_image,
            "image_id": image_id,
            "original_dimensions": (original_width, original_height),
            "resized_dimensions": (new_width, new_height),
            "is_valid": True
        }

    @staticmethod
    def error_result_image_processor(start_time: float) -> Dict[str, Any]:
        """
        Genera un resultado de error estándar.

        :param start_time: Tiempo inicial del proceso.
        :return: Diccionario de error.
        """
        end_time = time.time()
        elapsed_time_seconds = round(end_time - start_time, 4)
        elapsed_time_milliseconds = int((end_time - start_time) * 1000)

        logging.error(f"Error en el procesamiento. Tiempo transcurrido en Image Processor: {elapsed_time_seconds}s ({elapsed_time_milliseconds}ms)")

        return {
            "resized_image_base64": None,
            "image_path": None,
            "resized_image": None,
            "image_id": None,
            "original_dimensions": None,
            "resized_dimensions": None,
            "is_valid": False
        }