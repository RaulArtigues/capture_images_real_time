from src.utils import properties
from datetime import datetime
import numpy as np
import logging
import base64
import uuid
import cv2
import os

logging.basicConfig(level=logging.INFO)

class ImageProcessor:
    def __init__(self, save_dir="data/images"):
        self.target_horizontal = properties.target_horizontal
        self.target_vertical = properties.target_vertical
        self.save_dir = save_dir

    @staticmethod
    def convert_to_native(results):
        def _convert_value(value):
            if isinstance(value, np.generic):
                return value.item()
            elif isinstance(value, dict):
                return {k: _convert_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_convert_value(v) for v in value]
            elif value is None:
                return None
            elif isinstance(value, bool):
                return bool(value)
            return value
        return {k: _convert_value(v) for k, v in results.items()}

    def read_image_from_base64(self, image_base64):
        try:
            image_data = base64.b64decode(image_base64)
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            logging.error(f"Error al decodificar la imagen: {e}")
            return None

    def resize_and_save_image(self, image_base64, return_decoded=False):
        image = self.read_image_from_base64(image_base64)
        if image is None:
            return None, None, None if return_decoded else None, None

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

        if return_decoded:
            return resized_image_base64, image_path, resized_image, image_id, (original_width, original_height), (new_width, new_height)
        
        return resized_image_base64, image_path, image_id, (original_width, original_height), (new_width, new_height)