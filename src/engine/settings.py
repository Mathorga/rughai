from enum import Enum
import json


class Builtins(str, Enum):
    DEBUG = "debug"
    SHOW_COLLISIONS = "show_collisions"
    TITLE = "title"
    FONT_NAME = "font_name"
    VIEW_WIDTH = "view_width"
    VIEW_HEIGHT = "view_height"
    WINDOW_WIDTH = "window_width"
    WINDOW_HEIGHT = "window_height"
    PIXEL_PERFECT = "pixel_perfect"
    FULLSCREEN = "fullscreen"
    TARGET_FPS = "target_fps"
    CAMERA_SPEED = "camera_speed"

settings = {
    # Debug.
    Builtins.DEBUG: True,
    Builtins.SHOW_COLLISIONS: True,

    # Text settings.
    Builtins.TITLE: "",
    Builtins.FONT_NAME:  "",

    # Display settings.
    # GBA resolution:
    Builtins.VIEW_WIDTH: 240,
    Builtins.VIEW_HEIGHT: 160,
    # GBA resolution x3:
    Builtins.WINDOW_WIDTH: 720,
    Builtins.WINDOW_HEIGHT: 480,
    Builtins.PIXEL_PERFECT: False,
    Builtins.FULLSCREEN: True,

    # Keep target fps high, as low values could cause unwanted lags.
    Builtins.TARGET_FPS: 480,

    Builtins.CAMERA_SPEED: 5.0
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