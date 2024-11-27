class ImageDimensionProperties:
    """
    Propiedades relacionadas con las dimensiones y el procesamiento de bloques de imágenes.
    """

    """
    Tupla que representa el ancho y alto objetivo para imágenes en modo horizontal.
    """
    target_horizontal = (1920, 1080)

    """
    Tupla que representa el ancho y alto objetivo para imágenes en modo vertical.
    """
    target_vertical = (1080, 1920)

class SharpnessProperties:
    """
    Propiedades relacionadas con el análisis de la nitidez de las imágenes.
    """

    """
    Valor mínimo para considerar una imagen como suficientemente nítida.
    """
    default_threshold_sharpness = 150.0

class ExposureProperties:
    """
    Propiedades relacionadas con los umbrales de exposición (sobreexposición y subexposición).
    """

    """
    Valor máximo de intensidad para considerar un píxel como sobreexpuesto.
    """
    overexposed_threshold = 245
    
    """
    Valor mínimo de intensidad para considerar un píxel como subexpuesto.
    """
    underexposed_threshold = 10

    """
    Proporción máxima permitida de píxeles sobreexpuestos o subexpuestos antes de considerar la imagen inválida.
    """
    tolerance = 0.3

    default_thresholds_exposure = {
        "overexposed_threshold": overexposed_threshold,
        "underexposed_threshold": underexposed_threshold,
        "tolerance": tolerance
    }

class SpecularReflectionsProperties:
    """
    Parámetros utilizados para la detección de reflejos especulares en imágenes.
    """

    """
    Nivel de intensidad mínimo para detectar posibles reflejos especulares.
    """
    intensity_threshold = 240

    """
    Nivel de saturación mínimo para considerar un área como especular.
    """
    saturation_threshold = 50
    
    """
    Tamaño mínimo en píxeles de una región para que sea considerada como un reflejo especular.
    """
    min_region_size = 200
    
    """
    Sensibilidad utilizada durante el análisis de reflejos especulares. 
    Valores más altos reducen la detección de pequeños reflejos.
    """
    sensitivity = 1.5

class ResponseHandlerPaths:
    """
    Clase que contiene las rutas a archivos JSON utilizados para gestionar respuestas relacionadas con imágenes.
    """
    responses_hander_images_real_time = "data/responses/responses_images_real_time.json"
    responses_hander_images_gallery = "data/responses/responses_images_gallery.json"