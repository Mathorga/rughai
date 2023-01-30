import pyglet
import pyglet.gl as gl
import pyglet.math as pm

import settings
from camera import Camera
from fixed_resolution import FixedResolution
from game_object import GameObject
from input_controller import InputController

class Application:
    def __init__(
        self,
        view_width: int,
        view_height: int,
        window_width: int,
        window_height: int,
        title: str,
        fullscreen: bool = False,
        assets_path: str = "../assets",
        debug: bool = False
    ):
        pyglet.resource.path = [assets_path]
        pyglet.resource.reindex()

        # Create a new window.
        self._window = self._create_window(
            window_width if window_width is not None else view_width,
            window_height if window_height is not None else view_height,
            title,
            fullscreen
        )
        self.__fps_display = pyglet.window.FPSDisplay(self._window) if debug else None

        # Create a new input controller.
        self.__input_controller = InputController(
            window = self._window
        )

        # Define a fixed resolution.
        self._fr = FixedResolution(
            self._window,
            width = view_width,
            height = view_height
        )

        # Create a camera.
        self._camera = Camera(
            window = self._window,
        )

        self._window.push_handlers(self)
        self._objects = []

    def add_object(self, game_object: GameObject):
        self._objects.append(game_object)

    def on_draw(self):
        self._window.clear()
        with self._fr:
            with self._camera:
                for object in self._objects:
                    object.draw()

        if self.__fps_display != None:
            self.__fps_display.draw()

    def _create_window(
        self,
        view_width: int,
        view_height: int,
        title,
        fullscreen: bool
    ) -> pyglet.window.Window:
        win = pyglet.window.Window(
            view_width if not fullscreen else None,
            view_height if not fullscreen else None,
            title,
            fullscreen = fullscreen,
            resizable = True
        )
        win.set_minimum_size(view_width, view_height)

        return win

    def update(self, dt):
        for object in self._objects:
            object.update(dt)
        pass

    def run(self):
        # Enable depth testing in order to allow for depth sorting.
        # TODO Try this out! Use the z coordinate as depth!
        #gl.glEnable(gl.GL_DEPTH_TEST)

        # Scale textures using nearest neighbor filtering.
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

        pyglet.clock.schedule_interval(self.update, 1.0 / settings.TARGET_FPS)
        pyglet.app.run()