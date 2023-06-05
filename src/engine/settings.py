from enum import Enum
import json
import platform


class Builtins(str, Enum):
    DEBUG = "debug"
    SHOW_COLLISIONS = "show_collisions"
    SHOW_TILES_GRID = "show_tiles_grid"
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
    LAYERS_Z_SPACING = "layers_z_spacing"
    PLATFORM = "platform"

settings = {
    # Debug.
    Builtins.DEBUG: True,
    Builtins.SHOW_COLLISIONS: True,
    Builtins.SHOW_TILES_GRID: True,

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

    Builtins.CAMERA_SPEED: 5.0,
    Builtins.LAYERS_Z_SPACING: 32.0,

    Builtins.PLATFORM: ""
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

    settings[Builtins.PLATFORM] = platform.platform()