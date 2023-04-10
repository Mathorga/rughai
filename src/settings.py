import os

# Working directory.
WORKING_DIR = os.path.dirname(os.path.realpath(__file__)) + "/.."

DEBUG = True

# Display settings.
TITLE = "RUG-HAI"
FONT_NAME = "I pixel u"
# VIEW_WIDTH = 300
# VIEW_HEIGHT = 200
# GBA resolution:
VIEW_WIDTH = 240
VIEW_HEIGHT = 160
PIXEL_PERFECT = False
# WINDOW_WIDTH = 600
# WINDOW_HEIGHT = 400
# GBA resolution x3:
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 480
FULLSCREEN = True

# Keep target fps high, as low values could cause unwanted lags.
TARGET_FPS = 480

BACKGROUND_COLOR = "#222222"
CAM_SPEED = 5.0