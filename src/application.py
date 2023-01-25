import pyglet
import pyglet.gl as gl
import pyglet.math as pm

import settings
from camera import Camera
from fixed_resolution import FixedResolution
from game_window import GameWindow

class Application:
    def __init__(
        self,
        view_width: int,
        view_height: int,
        window_width: int,
        window_height: int,
        title,
        fullscreen: bool = False
    ):
        # Create a new window.
        self._window = self._create_window(
            window_width if window_width is not None else view_width,
            window_height if window_height is not None else view_height,
            title,
            fullscreen
        )

        # Define a fixed resolution.
        self._fr = self._create_fr(view_width, view_height)

        # Create a camera.
        self._camera = Camera(
            window = self._window,
        )

        self._window.push_handlers(self)
        self._sprites = []

    def on_draw(self):
        with self._fr:
            with self._camera:
                for sprite in self._sprites:
                    sprite.draw()

    def _create_window(
        self,
        view_width: int,
        view_height: int,
        title,
        fullscreen: bool
    ) -> pyglet.window.Window:
        win = GameWindow(
            view_width = view_width * 3 if not fullscreen else None,
            view_height = view_height * 3 if not fullscreen else None,
            title = title,
            fullscreen = fullscreen,
            resizable = True
        )
        win.set_minimum_size(view_width, view_height)

        return win

    def _create_fr(self, width, height):
        fr = FixedResolution(
            self._window,
            width = width,
            height = height
        )
        return fr

    def update(self, dt):
        print("Giaccone")
        pass

    def run(self):
        # Scale textures using nearest neighbor filtering.
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

        pyglet.clock.schedule_interval(self.update, 1.0 / settings.TARGET_FPS)
        pyglet.app.run()