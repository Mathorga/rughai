import json
import pyglet

settings = {
    "DEBUG": True,

    # Text settings.
    "TITLE": "",
    "FONT_NAME":  "",

    # Display settings.
    # GBA resolution:
    "VIEW_WIDTH": 240,
    "VIEW_HEIGHT": 160,
    # GBA resolution x3:
    "WINDOW_WIDTH": 720,
    "WINDOW_HEIGHT": 480,
    "PIXEL_PERFECT": False,
    "FULLSCREEN": True,

    # Keep target fps high, as low values could cause unwanted lags.
    "TARGET_FPS": 480,

    "BACKGROUND_COLOR": "#222222",
    "CAM_SPEED": 5.0
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