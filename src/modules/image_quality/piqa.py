from src.utils import properties
import numpy as np
import logging
import cv2

logging.basicConfig(level=logging.INFO)

class SimplePIQA:
    def __init__(self):
        """
        Implementación simplificada de PIQA.
        :param block_size: Tamaño de los bloques para calcular la variación.
        """
        self.block_size = properties.block_size

    def compute(self, image):
        """
        Calcula un puntaje PIQA simplificado basado en la variación en bloques.
        :param image: Imagen de entrada (en escala de grises).
        :return: Puntaje PIQA simplificado.
        """
        # Convertir a escala de grises si es necesario
        if len(image.shape) == 3:
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            image_gray = image

        # Dimensiones de la imagen
        height, width = image_gray.shape

        # Dividir la imagen en bloques
        score = 0
        num_blocks = 0
        for y in range(0, height, self.block_size):
            for x in range(0, width, self.block_size):
                block = image_gray[y:y+self.block_size, x:x+self.block_size]
                if block.size == 0:
                    continue
                # Calcular la variación del bloque
                block_std = np.std(block)
                score += block_std
                num_blocks += 1

        # Promediar el puntaje
        score = score / num_blocks if num_blocks > 0 else 0
        return score