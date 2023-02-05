from collections import deque
import os.path
from statistics import mean

import pyglet
import pyglet.gl as gl

from engine.input_controller import InputController

import settings
from rughai_hub import RugHaiHub

class FPSIndicator:
    def __init__(
        self,
        window: pyglet.window.Window,
        samples: int = 240,
        update_period: float = 0.25
    ):
        self._window = window

        self._fps_label = pyglet.text.Label(
            text = "",
            anchor_x = "left",
            anchor_y = "top",
            x = 10,
            y = window.height - 10,
            bold = True
        )

        self._update_period = update_period
        self._elapsed = 0.0
        self._delta_times = deque(maxlen=samples)

        pyglet.clock.schedule(self.update_fps)

    def update_fps(self, dt):
        self._elapsed += dt
        self._delta_times.append(dt)

        if self._elapsed >= self._update_period:
            self._elapsed = 0.0
            self._fps_label.text = f"TPS: {1 / mean(self._delta_times):.0f}"

    def draw(self):
        self._fps_label.draw()

class RugHai:
    def __init__(self):
        # Set resources path.
        pyglet.resource.path = [f"{os.path.dirname(__file__)}/../assets"]
        pyglet.resource.reindex()

        # Create a window.
        self._window = pyglet.window.Window(
            settings.WINDOW_WIDTH if not settings.FULLSCREEN else None,
            settings.WINDOW_HEIGHT if not settings.FULLSCREEN else None,
            settings.TITLE,
            fullscreen = settings.FULLSCREEN,
            resizable = False
        )
        self._window.push_handlers(self)
        self._window.set_mouse_visible(False)

        # Compute pixel scaling (minimum unit is <1 / scaling>)
        # Using a scaling of 1 means that movements are pixel-perfect (aka nothing moves by sub-pixel values).
        # Using a scaling of 5 means that the minimum unit is 1/5 of a pixel.
        self._scaling = 1 if settings.PIXEL_PERFECT else min(self._window.width // settings.VIEW_WIDTH, self._window.height // settings.VIEW_HEIGHT)

        self._fps_display = pyglet.window.FPSDisplay(
            window = self._window,
            samples = settings.TARGET_FPS
        ) if settings.DEBUG else None

        self._fps_label = FPSIndicator(
            window = self._window,
            samples = settings.TARGET_FPS
        ) if settings.DEBUG else None

        # Create an input handler.
        self._input = InputController(window = self._window)

        # Create a scene.
        self._scene = RugHaiHub(
            window = self._window,
            input_controller = self._input,
            scaling = self._scaling
        )

    def on_draw(self):
        self._window.clear()
        self._scene.draw()

        if self._fps_display != None:
            self._fps_display.draw()

        if self._fps_label != None:
            self._fps_label.draw()

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