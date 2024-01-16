from enum import Enum
import json
import platform


class Keys(str, Enum):
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
    SOUND = "sound"
    MUSIC = "music"
    SFX = "sfx"

    # Globals.
    PLATFORM = "platform"
    SCALING = "scaling"
    FLOAT_ROUNDING = "float_rounding"

SETTINGS = {
    # Debug.
    Keys.DEBUG: True,
    Keys.SHOW_COLLISIONS: True,
    Keys.SHOW_TILES_GRID: True,
    Keys.FREE_CAM_BOUNDS: False,

    # Text settings.
    Keys.TITLE: "",
    Keys.FONT_NAME:  "",

    # Display settings.
    # GBA resolution:
    Keys.VIEW_WIDTH: 240,
    Keys.VIEW_HEIGHT: 160,
    # GBA resolution x3:
    Keys.WINDOW_WIDTH: 720,
    Keys.WINDOW_HEIGHT: 480,

    # Defines whether rendering and movement is per pixel or sub-pixel (unused for now).
    Keys.PIXEL_PERFECT: False,
    Keys.FULLSCREEN: True,

    # Keep target fps high, as low values could cause unwanted lags.
    Keys.TARGET_FPS: 480,

    Keys.CAMERA_SPEED: 5.0,
    Keys.LAYERS_Z_SPACING: 32.0,
    Keys.TILEMAP_BUFFER: 2,

    # Sounds settings.
    Keys.SOUND: True,
    Keys.MUSIC: True,
    Keys.SFX: True
}

GLOBALS = {
    Keys.PLATFORM: "",
    Keys.SCALING: 1,
    Keys.FLOAT_ROUNDING: 5
}

def load_settings(source: str):
    data: dict

    # Load JSON file.
    with open(file = source, mode = "r", encoding = "UTF-8") as content:
        data = json.load(content)

    for entry in data.items():
        SETTINGS.update({entry})

    # Save platform for later use.
    GLOBALS[Keys.PLATFORM] = platform.platform()