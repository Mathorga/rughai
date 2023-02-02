import os.path

import pyglet
import pyglet.gl as gl

from engine.input_controller import InputController

import settings
from rughai_hub import RugHaiHub

class RugHai:
    def __init__(self):
        # Set resources path.
        pyglet.resource.path = [f"{os.path.dirname(__file__)}/../assets"]
        pyglet.resource.reindex()

        # Create a window.
        self._win = pyglet.window.Window(
            settings.WINDOW_WIDTH if not settings.FULLSCREEN else None,
            settings.WINDOW_HEIGHT if not settings.FULLSCREEN else None,
            settings.TITLE,
            fullscreen = settings.FULLSCREEN,
            resizable = True
        )
        self._win.push_handlers(self)

        self._fps_display = pyglet.window.FPSDisplay(self._win) if settings.DEBUG else None

        if settings.PIXEL_SCALING > self._win.width / settings.VIEW_WIDTH or settings.PIXEL_SCALING > self._win.height / settings.VIEW_HEIGHT:
            settings.PIXEL_SCALING = min(self._win.width // settings.VIEW_WIDTH, self._win.height // settings.VIEW_HEIGHT)

        self._win.set_minimum_size(
            settings.VIEW_WIDTH * settings.PIXEL_SCALING,
            settings.VIEW_HEIGHT * settings.PIXEL_SCALING
        )

        # Create an input handler.
        self._input = InputController(window = self._win)

        # Create a scene.
        self._scene = RugHaiHub(
            window = self._win,
            input_controller = self._input
        )

    def on_resize(self, width, height):
        if settings.PIXEL_SCALING > width / settings.VIEW_WIDTH or settings.PIXEL_SCALING > height / settings.VIEW_HEIGHT:
            settings.PIXEL_SCALING = min(width // settings.VIEW_WIDTH, height // settings.VIEW_HEIGHT)

    def on_draw(self):
        self._win.clear()
        self._scene.draw()

        if self._fps_display != None:
            self._fps_display.draw()

    def update(self, dt):
        self._scene.update(dt)

    def run(self):
        # Enable depth testing in order to allow for depth sorting.
        # TODO Try this out! Use the z coordinate as depth!
        # gl.glEnable(gl.GL_DEPTH_TEST)

        # Scale textures using nearest neighbor filtering.
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

        pyglet.clock.schedule_interval(self.update, 1.0 / settings.TARGET_FPS)
        pyglet.app.run()

app = RugHai()
app.run()