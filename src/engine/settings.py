from enum import Enum
import json
import platform


class Builtins(str, Enum):
    # Settings.
    DEBUG = "debug"
    SHOW_COLLISIONS = "show_collisions"
    SHOW_TILES_GRID = "show_tiles_grid"
    FREE_CAM_BOUNDS = "free_cam_bounds"
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
    TILEMAP_BUFFER = "tilemap_buffer"

    # Globals.
    PLATFORM = "platform"
    SCALING = "scaling"

SETTINGS = {
    # Debug.
    Builtins.DEBUG: True,
    Builtins.SHOW_COLLISIONS: True,
    Builtins.SHOW_TILES_GRID: True,
    Builtins.FREE_CAM_BOUNDS: False,

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

    # Defines whether rendering and movement is per pixel or sub-pixel (unused for now).
    Builtins.PIXEL_PERFECT: False,
    Builtins.FULLSCREEN: True,

    # Keep target fps high, as low values could cause unwanted lags.
    Builtins.TARGET_FPS: 480,

    Builtins.CAMERA_SPEED: 5.0,
    Builtins.LAYERS_Z_SPACING: 32.0,
    Builtins.TILEMAP_BUFFER: 2
}

GLOBALS = {
    Builtins.PLATFORM: "",
    Builtins.SCALING: 1
}

def load_settings(source: str):
    data: dict

    # Load JSON file.
    with open(file = source, mode = "r", encoding = "UTF-8") as content:
        data = json.load(content)

    for entry in data.items():
        SETTINGS.update({entry})

    # Save platform for later use.
    GLOBALS[Builtins.PLATFORM] = platform.platform()