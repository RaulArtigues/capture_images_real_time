from src.modules.image_quality.image_processor import ImageProcessor
from src.modules.image_quality.piqa import SimplePIQA
from src.utils import properties
from pyiqa import create_metric
import numpy as np
import logging
import torch
import cv2

logging.basicConfig(level=logging.INFO)

class QualityEvaluator:
    def __init__(self, method):
        """
        Clase para evaluar la calidad de la imagen usando PIQA, NIQE o BRISQUE.
        :param method: 'PIQA', 'NIQE'.
        """
        self.method = method
        if self.method == "PIQA":
            self.evaluator = SimplePIQA()
        elif self.method == "NIQE":
            self.model = create_metric('niqe')
        elif self.method == "brisque":
            self.model = create_metric('brisque')
        else:
            raise ValueError("Método inválido. Use 'PIQA', 'NIQE'.")

    def evaluate_image_quality(self, image_base64):
        """
        Evalúa la calidad de la imagen utilizando métricas básicas (nitidez, exposición, resolución)
        y métodos avanzados como NIQE o PIQA.
        """
        def evaluate_niqe(image):
            """Evalúa la calidad usando NIQE."""
            try:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype('float32') / 255.0
                image_tensor = torch.from_numpy(image_rgb).permute(2, 0, 1).unsqueeze(0)
                with torch.no_grad():
                    score = self.model(image_tensor).item()
                quality = "HIGH" if score <= properties.score_high_niqe else "MEDIUM" if score <= properties.score_medium_niqe else "BAD"
                logging.info(f"Puntuación NIQE: {score}, Calidad: {quality}")
                return {"niqe_score": round(score, 4), "niqe_quality": quality}
            except Exception as e:
                logging.error(f"Error al calcular el puntaje NIQE: {e}")
                return {"niqe_error": "NIQE calculation failed"}

        def evaluate_piqa(image):
            """Evalúa la calidad usando PIQA."""
            try:
                score = self.evaluator.compute(image)
                quality = "HIGH" if score <= properties.score_high_piqa else "MEDIUM" if score <= properties.score_medium_piqa else "BAD"
                logging.info(f"Puntuación PIQA: {score}, Calidad: {quality}")
                return {"piqa_score": round(score, 4), "piqa_quality": quality}
            except Exception as e:
                logging.error(f"Error al calcular el puntaje PIQA: {e}")
                return {"piqa_error": "PIQA calculation failed"}

        # Decodificar la imagen de Base64
        image_processor = ImageProcessor()
        image = image_processor.read_image_from_base64(image_base64)

        if image is None:
            logging.error("No se pudo decodificar la imagen.")
            return {"error": "Invalid image decoding"}

        # Consolidar resultados
        results = {}
        if self.method == "NIQE":
            results.update(evaluate_niqe(image))
        elif self.method == "PIQA":
            results.update(evaluate_piqa(image))
        else:
            logging.warning("Método de evaluación avanzado no definido.")
            results.update({"error": "No advanced method selected"})

        return results