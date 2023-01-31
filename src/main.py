import os.path

import pyglet
import pyglet.gl as gl
import pyglet.math as pm

from engine.input_controller import InputController

import settings
from rughai_hub import RugHaiHub

# Set resources path.
pyglet.resource.path = [f"{os.path.dirname(__file__)}/../assets"]
pyglet.resource.reindex()

# Create a window.
win = pyglet.window.Window(
    settings.WINDOW_WIDTH if not settings.FULLSCREEN else None,
    settings.WINDOW_HEIGHT if not settings.FULLSCREEN else None,
    settings.TITLE,
    fullscreen = settings.FULLSCREEN,
    resizable = True
)
win.set_minimum_size(settings.VIEW_WIDTH, settings.VIEW_HEIGHT)
fps_display = pyglet.window.FPSDisplay(win) if settings.DEBUG else None

# Create an input handler.
input_controller = InputController(window = win)

# Create a scene.
scene = RugHaiHub(
    window = win,
    input_controller = input_controller
)

@win.event
def on_draw():
    win.clear()
    scene.draw()

    if fps_display != None:
        fps_display.draw()

def update(dt):
    scene.update(dt)


# Enable depth testing in order to allow for depth sorting.
# TODO Try this out! Use the z coordinate as depth!
gl.glEnable(gl.GL_DEPTH_TEST)

# Scale textures using nearest neighbor filtering.
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

pyglet.clock.schedule_interval(update, 1.0 / settings.TARGET_FPS)
pyglet.app.run()