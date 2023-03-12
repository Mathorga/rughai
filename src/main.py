import os.path
import pyglet
import pyglet.gl as gl
from engine.collision_manager import CollisionManager

from engine.input_controller import InputController
from engine.benchmark import Benchmark
from fixed_resolution import Upscaler

import settings
from rughai_hub import RugHaiHub

class RugHai:
    def __init__(self) -> None:
        # Set resources path.
        pyglet.resource.path = [f"{os.path.dirname(__file__)}/../assets"]
        pyglet.resource.reindex()

        # Create a window.
        self._window = self.__create_window()

        # Create a collision manager.
        self._collision_manager = CollisionManager()

        # Compute pixel scaling (minimum unit is <1 / scaling>)
        # Using a scaling of 1 means that movements are pixel-perfect (aka nothing moves by sub-pixel values).
        # Using a scaling of 5 means that the minimum unit is 1/5 of a pixel.
        self._scaling = 1 if settings.PIXEL_PERFECT else min(
            self._window.width // settings.VIEW_WIDTH,
            self._window.height // settings.VIEW_HEIGHT
        )

        self._upscaler = Upscaler(
            window = self._window,
            width = settings.VIEW_WIDTH * self._scaling,
            height = settings.VIEW_HEIGHT * self._scaling
        )

        # Create benchmarks.
        self._update_bench = Benchmark(
            window = self._window,
            text = "UT: "
        )
        self._render_bench = Benchmark(
            window = self._window,
            text = "RT: ",
            y = self._window.height - 30
        )

        # Create an input handler.
        self._input = InputController(window = self._window)

        # Create a scene.
        self._scene = RugHaiHub(
            window = self._window,
            collision_manager = self._collision_manager,
            view_width = settings.VIEW_WIDTH,
            view_height = settings.VIEW_HEIGHT,
            input_controller = self._input,
            scaling = self._scaling,
            on_bottom_door_entered = lambda : print("bottom_door_entered")
        )

    def __create_window(self) -> pyglet.window.Window:
        window = pyglet.window.Window(
            settings.WINDOW_WIDTH if not settings.FULLSCREEN else None,
            settings.WINDOW_HEIGHT if not settings.FULLSCREEN else None,
            settings.TITLE,
            fullscreen = settings.FULLSCREEN,
            vsync = True,
            resizable = False
        )

        window.push_handlers(self)
        if not settings.DEBUG:
            window.set_mouse_visible(False)

        return window

    def on_draw(self) -> None:
        # Benchmark measures render time.
        with self._render_bench:
            self._window.clear()

            # Upscaler handles maintaining the wanted output resolution.
            with self._upscaler:
                self._scene.draw()

            if settings.DEBUG:
                self._update_bench.draw()
                self._render_bench.draw()

    def update(self, dt) -> None:
        # Compute collisions through collision manager.
        self._collision_manager.update(dt)

        # Benchmark measures update time.
        with self._update_bench:
            # InputController makes sure every input is handled correctly.
            with self._input:
                self._scene.update(dt)

    def run(self) -> None:
        # Enable depth testing in order to allow for depth sorting.
        # TODO Try this out! Use the z coordinate as depth!
        # gl.glDepthFunc(gl.GL_LESS)
        # gl.glEnable(gl.GL_DEPTH_TEST)

        # Scale textures using nearest neighbor filtering.
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        pyglet.clock.schedule_interval(self.update, 1.0 / settings.TARGET_FPS)
        pyglet.app.run()

app = RugHai()
app.run()