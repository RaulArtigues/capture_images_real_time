from flask import request

def client_metadata():
    data = request.json
    metadata_raw = data.get('metadata', "")
    return {
        # Fotografía General
        "Make": metadata_raw.get("Make"),
        "Model": metadata_raw.get("Model"),
        "Software": metadata_raw.get("Software"),
        "DateTimeOriginal": metadata_raw.get("DateTimeOriginal"),
        "FNumber": metadata_raw.get("FNumber"),
        "FocalLength": metadata_raw.get("FocalLength"),
        "ExposureTime": metadata_raw.get("ExposureTime"),
        "ISOSpeedRatings": metadata_raw.get("ISOSpeedRatings"),
        "Flash": metadata_raw.get("Flash"),
        "PixelXDimension": metadata_raw.get("PixelXDimension"),
        "PixelYDimension": metadata_raw.get("PixelYDimension"),
        # Ubicación (Mapeo y Navegación)
        "GPSLatitude": metadata_raw.get("GPSLatitude"),
        "GPSLongitude": metadata_raw.get("GPSLongitude"),
        "GPSAltitude": metadata_raw.get("GPSAltitude"),
        "GPSTimeStamp": metadata_raw.get("GPSTimeStamp"),
        "GPSDateStamp": metadata_raw.get("GPSDateStamp"),
        # Análisis de Calidad
        "BrightnessValue": metadata_raw.get("BrightnessValue"),
        "ColorSpace": metadata_raw.get("ColorSpace"),
        "MeteringMode": metadata_raw.get("MeteringMode"),
        # Organización y Clasificación
        "Orientation": metadata_raw.get("Orientation"),
    }