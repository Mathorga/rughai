import os.path
import sys
import pyglet
import pyglet.gl as gl

# setting path
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")))

import amonite.controllers as controllers
from amonite.upscaler import Upscaler
from amonite.settings import GLOBALS, SETTINGS, Keys, load_settings
from prop_placement_scene import PropPlacementScene

class RugHaiSceneEditor:
    """
    Main class: this is where scene changing happens and everything is set up.
    """

    def __init__(self) -> None:
        # Set resources path.
        pyglet.resource.path = [f"{os.path.dirname(__file__)}/../../assets"]
        pyglet.resource.reindex()

        # Load font files.
        pyglet.font.add_file(f"{pyglet.resource.path[0]}/fonts/I-pixel-u.ttf")
        pyglet.font.add_file(f"{pyglet.resource.path[0]}/fonts/rughai.ttf")

        # Load settings from file.
        load_settings(f"{pyglet.resource.path[0]}/settings.json")

        # Create a window.
        self._window = self.__create_window()

        # Controllers.
        controllers.create_controllers(window = self._window)

        # Compute pixel scaling (minimum unit is <1 / scaling>)
        # Using a scaling of 1 means that movements are pixel-perfect (aka nothing moves by sub-pixel values).
        # Using a scaling of 5 means that the minimum unit is 1/5 of a pixel.
        GLOBALS[Keys.SCALING] = 1 if SETTINGS[Keys.PIXEL_PERFECT] else min(
            self._window.width // SETTINGS[Keys.VIEW_WIDTH],
            self._window.height // SETTINGS[Keys.VIEW_HEIGHT]
        )

        self._upscaler = Upscaler(
            window = self._window,
            width = SETTINGS[Keys.VIEW_WIDTH] * GLOBALS[Keys.SCALING],
            height = SETTINGS[Keys.VIEW_HEIGHT] * GLOBALS[Keys.SCALING]
        )

        # Create a scene.
        self.__scene = PropPlacementScene(
            window = self._window,
            view_width = SETTINGS[Keys.VIEW_WIDTH],
            view_height = SETTINGS[Keys.VIEW_HEIGHT]
        )

    def __create_window(self) -> pyglet.window.BaseWindow:
        window = pyglet.window.Window(
            SETTINGS[Keys.WINDOW_WIDTH] if not SETTINGS[Keys.FULLSCREEN] else None,
            SETTINGS[Keys.WINDOW_HEIGHT] if not SETTINGS[Keys.FULLSCREEN] else None,
            SETTINGS[Keys.TITLE],
            fullscreen = SETTINGS[Keys.FULLSCREEN],
            vsync = True,
            resizable = False
        )

        window.push_handlers(self)
        if not SETTINGS[Keys.DEBUG]:
            window.set_mouse_visible(False)

        return window

    def on_draw(self) -> None:
        """
        Draws everything to the screen.
        """

        # Update window matrix.
        self._window.projection = pyglet.math.Mat4.orthogonal_projection(
            left = 0,
            right = self._window.width,
            bottom = 0,
            top = self._window.height,
            # For some reason near and far planes are inverted in sign, so that -500 means 500 and 1024 means -1024.
            z_near = -3000,
            z_far = 3000
        )

        # Scale textures using nearest neighbor filtering.
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        # Benchmark measures render time.
        self._window.clear()

        # Upscaler handles maintaining the wanted output resolution.
        with self._upscaler:
            self.__scene.draw()

    def update(self, dt) -> None:
        # InputController makes sure every input is handled correctly.
        with controllers.INPUT_CONTROLLER:
            self.__scene.update(dt)

        # Compute collisions through collision manager.
        controllers.COLLISION_CONTROLLER.update(dt)

    def run(self) -> None:
        pyglet.clock.schedule_interval(self.update, 1.0 / SETTINGS[Keys.TARGET_FPS])
        # pyglet.clock.schedule(self.update)
        pyglet.app.run()

app = RugHaiSceneEditor()
app.run()