import logging
import json
import os

logging.basicConfig(level=logging.INFO)

# Clase para manejar la lectura y escritura de respuestas en un archivo JSON
class ResponseHandler:
    def __init__(self, filename="data/responses/responses.json"):
        self.filename = filename

    def save_response(self, response_data):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r") as f:
                    responses = json.load(f)
            else:
                responses = []
            responses.append(response_data)
            with open(self.filename, "w") as f:
                json.dump(responses, f, indent=4)
        except Exception as e:
            logging.warning(f"No se pudo guardar la respuesta en JSON: {e}")