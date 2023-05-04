from enum import Enum
import json


class Builtins(str, Enum):
    DEBUG = "debug"
    TITLE = "title"
    FONT_NAME = "font_name"
    VIEW_WIDTH = "view_width"
    VIEW_HEIGHT = "view_height"
    WINDOW_WIDTH = "window_width"
    WINDOW_HEIGHT = "window_height"
    PIXEL_PERFECT = "pixel_perfect"
    FULLSCREEN = "fullscreen"
    TARGET_FPS = "target_fps"
    BACKGROUND_COLOR = "background_color"
    CAMERA_SPEED = "camera_speed"

settings = {
    "debug": True,

    # Text settings.
    "title": "",
    "font_name":  "",

    # Display settings.
    # GBA resolution:
    "view_width": 240,
    "view_height": 160,
    # GBA resolution x3:
    "window_width": 720,
    "window_height": 480,
    "pixel_perfect": False,
    "fullscreen": True,

    # Keep target fps high, as low values could cause unwanted lags.
    "target_fps": 480,

    "background_color": "#222222",
    "camera_speed": 5.0
}

def load_settings(source: str):
    # Load settings from json file.
    global settings

    data: dict

    # Load JSON file.
    with open(source) as content:
        data = json.load(content)

    for entry in data.items():
        settings.update({entry})