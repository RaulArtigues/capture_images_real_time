from typing import Any, Dict
import logging
import json
import os
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class ResponseHandler:
    """
    Clase para manejar la lectura y escritura de respuestas en un archivo JSON.
    """
    def __init__(self, filename: str):
        """
        Inicializa la clase con el archivo donde se guardarán las respuestas.

        :param filename: Ruta del archivo JSON donde se almacenarán las respuestas.
        """
        self.filename = filename
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

    @staticmethod
    def convert_to_native(results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convierte estructuras de datos numpy a tipos nativos de Python.

        :param results: Diccionario con los resultados a convertir.
        :return: Diccionario con tipos de datos nativos.
        """
        def _convert_value(value: Any) -> Any:
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

    def _initialize_responses_file(self):
        """
        Crea un archivo JSON vacío si no existe.
        """
        if not os.path.exists(self.filename):
            logging.info(f"El archivo no existe. Creando nuevo: {self.filename}")
            with open(self.filename, "w") as f:
                json.dump([], f)

    def save_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Guarda una respuesta en el archivo JSON después de convertir los datos a tipos nativos.

        :param response_data: Diccionario con los datos de la respuesta.
        :return: Diccionario con información sobre el éxito o error del proceso.
        """
        if not isinstance(response_data, dict):
            logging.error("El parámetro response_data debe ser un diccionario.")
            return {"is_valid": False}

        try:
            self._initialize_responses_file()

            with open(self.filename, "r") as f:
                responses = json.load(f)

            native_data = self.convert_to_native(response_data)
            responses.append(native_data)

            with open(self.filename, "w") as f:
                json.dump(responses, f, indent=4)

            logging.info("Respuesta guardada exitosamente.")
            return {"is_valid": True}

        except json.JSONDecodeError as jde:
            logging.error(f"Error al decodificar JSON: {jde}", exc_info=True)
            return {"is_valid": False, "error": "JSONDecodeError"}
        except OSError as ose:
            logging.error(f"Error del sistema al manejar el archivo: {ose}", exc_info=True)
            return {"is_valid": False, "error": "OSError"}
        except Exception as e:
            logging.error(f"No se pudo guardar la respuesta en JSON: {e}", exc_info=True)
            return {"is_valid": False, "error": str(e)}