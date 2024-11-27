from flask import request
import logging

def client_info():
    data = request.json

    user_agent = data.get("userAgent", "N/A")
    platform = data.get("platform", "N/A")
    screen_width = data.get("screenWidth", "N/A")
    screen_height = data.get("screenHeight", "N/A")
    pixel_ratio = data.get("pixelRatio", "N/A")
    color_depth = data.get("colorDepth", "N/A")
    touch_points = data.get("touchPoints", "N/A")
    cpu_cores = data.get("cpuCores", "N/A")
    
    info = {
        "user_agent": user_agent,
        "platform": platform,
        "screen_width": screen_width,
        "screen_height": screen_height,
        "pixel_ratio": pixel_ratio,
        "color_depth": color_depth,
        "touch_points": touch_points,
        "cpu_cores": cpu_cores,
    }
    return info