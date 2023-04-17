import os.path
import pyglet
import pyglet.gl as gl

from engine.collision_manager import CollisionManager
from engine.input_controller import InputController
from engine.benchmark import Benchmark
from engine.upscaler import Upscaler
from scenes.rughai.r_0_0 import R_0_0
from scenes.rughai.r_0_1 import R_0_1
from scenes.rughai.r_0_2 import R_0_2
from scenes.rughai.r_0_3 import R_0_3
from scenes.rughai.r_0_4 import R_0_4
from scenes.rughai.r_0_5 import R_0_5
from scenes.rughai.r_0_6 import R_0_6

import settings
import constants.scenes as scenes

class RugHai:
    def __init__(self) -> None:
        # Set resources path.
        pyglet.resource.path = [f"{os.path.dirname(__file__)}/../assets"]
        pyglet.resource.reindex()
        pyglet.font.add_file(f"{os.path.dirname(__file__)}/../assets/fonts/I-pixel-u.ttf")

        # Create a window.
        self._window = self.__create_window()

        # Handlers.
        # Create a collision manager.
        self._collision_manager = CollisionManager()

        # Create an input handler.
        self._input = InputController(window = self._window)

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
            text = "UT: ",
            y = 30,
            visible = settings.DEBUG
        )
        self._render_bench = Benchmark(
            window = self._window,
            text = "RT: ",
            visible = settings.DEBUG
        )

        # Create a scene.
        self._active_scene = R_0_0(
            window = self._window,
            collision_manager = self._collision_manager,
            input_controller = self._input,
            view_width = settings.VIEW_WIDTH,
            view_height = settings.VIEW_HEIGHT,
            scaling = self._scaling,
            on_ended = self.__on_scene_end
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

    def __on_scene_end(self, bundle: dict):
        print("scene_ended", bundle)
        if bundle["next_scene"]:
            self._collision_manager.clear()
            self._active_scene.delete()

            if bundle["next_scene"] == scenes.R_0_0:
                self._active_scene = R_0_0(
                    window = self._window,
                    collision_manager = self._collision_manager,
                    input_controller = self._input,
                    view_width = settings.VIEW_WIDTH,
                    view_height = settings.VIEW_HEIGHT,
                    bundle = bundle,
                    scaling = self._scaling,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_1:
                self._active_scene = R_0_1(
                    window = self._window,
                    collision_manager = self._collision_manager,
                    input_controller = self._input,
                    view_width = settings.VIEW_WIDTH,
                    view_height = settings.VIEW_HEIGHT,
                    bundle = bundle,
                    scaling = self._scaling,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_2:
                self._active_scene = R_0_2(
                    window = self._window,
                    collision_manager = self._collision_manager,
                    input_controller = self._input,
                    view_width = settings.VIEW_WIDTH,
                    view_height = settings.VIEW_HEIGHT,
                    bundle = bundle,
                    scaling = self._scaling,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_3:
                self._active_scene = R_0_3(
                    window = self._window,
                    collision_manager = self._collision_manager,
                    input_controller = self._input,
                    view_width = settings.VIEW_WIDTH,
                    view_height = settings.VIEW_HEIGHT,
                    bundle = bundle,
                    scaling = self._scaling,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_4:
                self._active_scene = R_0_4(
                    window = self._window,
                    collision_manager = self._collision_manager,
                    input_controller = self._input,
                    view_width = settings.VIEW_WIDTH,
                    view_height = settings.VIEW_HEIGHT,
                    bundle = bundle,
                    scaling = self._scaling,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_5:
                self._active_scene = R_0_5(
                    window = self._window,
                    collision_manager = self._collision_manager,
                    input_controller = self._input,
                    view_width = settings.VIEW_WIDTH,
                    view_height = settings.VIEW_HEIGHT,
                    bundle = bundle,
                    scaling = self._scaling,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_6:
                self._active_scene = R_0_6(
                    window = self._window,
                    collision_manager = self._collision_manager,
                    input_controller = self._input,
                    view_width = settings.VIEW_WIDTH,
                    view_height = settings.VIEW_HEIGHT,
                    bundle = bundle,
                    scaling = self._scaling,
                    on_ended = self.__on_scene_end
                )

    def on_draw(self) -> None:
        # Update window matrix.
        self._window.projection = pyglet.math.Mat4.orthogonal_projection(
            left = 0,
            right = self._window.width,
            bottom = 0,
            top = self._window.height,
            z_near = -1000,
            z_far = 1000
        )

        # Benchmark measures render time.
        with self._render_bench:
            self._window.clear()

            # Upscaler handles maintaining the wanted output resolution.
            with self._upscaler:
                self._active_scene.draw()

    def update(self, dt) -> None:
        # Compute collisions through collision manager.
        self._collision_manager.update(dt)

        # Benchmark measures update time.
        with self._update_bench:
            # InputController makes sure every input is handled correctly.
            with self._input:
                self._active_scene.update(dt)

    def run(self) -> None:
        # Scale textures using nearest neighbor filtering.
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        pyglet.clock.schedule_interval(self.update, 1.0 / settings.TARGET_FPS)
        # pyglet.clock.schedule(self.update)
        pyglet.app.run()

app = RugHai()
app.run()