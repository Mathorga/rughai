import os.path
import pyglet
import pyglet.gl as gl

import engine.controllers as controllers
from engine.benchmark import Benchmark
from engine.upscaler import Upscaler
from engine.settings import GLOBALS, SETTINGS, Builtins, load_settings

from scenes.rughai.r_0_0 import R_0_0
from scenes.rughai.r_0_1 import R_0_1
from scenes.rughai.r_0_2 import R_0_2
from scenes.rughai.r_0_3 import R_0_3
from scenes.rughai.r_0_4 import R_0_4
from scenes.rughai.r_0_5 import R_0_5
from scenes.rughai.r_0_6 import R_0_6

import constants.scenes as scenes

class RugHai:
    """
    Main class: this is where scene changing happens and everything is set up.
    """

    def __init__(self) -> None:
        # Set resources path.
        pyglet.resource.path = [f"{os.path.dirname(__file__)}/../assets"]
        pyglet.resource.reindex()

        # Load font files.
        pyglet.font.add_file(f"{pyglet.resource.path[0]}/fonts/I-pixel-u.ttf")
        pyglet.font.add_file(f"{pyglet.resource.path[0]}/fonts/rughai.ttf")

        # Load settings from file.
        load_settings(f"{pyglet.resource.path[0]}/settings.json")

        # Create a window.
        self._window = self.__create_window()
        self.fps_display = pyglet.window.FPSDisplay(window = self._window, color = (0, 0, 0, 255), samples = 16)

        # Controllers.
        controllers.create_controllers(window = self._window)
        # self._collision_controller = CollisionController()
        # self._input_controller = InputController(window = self._window)
        # self._dialog_controller = DialogController()

        # Compute pixel scaling (minimum unit is <1 / scaling>)
        # Using a scaling of 1 means that movements are pixel-perfect (aka nothing moves by sub-pixel values).
        # Using a scaling of 5 means that the minimum unit is 1/5 of a pixel.
        GLOBALS[Builtins.SCALING] = 1 if SETTINGS[Builtins.PIXEL_PERFECT] else min(
            self._window.width // SETTINGS[Builtins.VIEW_WIDTH],
            self._window.height // SETTINGS[Builtins.VIEW_HEIGHT]
        )


        self._upscaler = Upscaler(
            window = self._window,
            width = SETTINGS[Builtins.VIEW_WIDTH] * GLOBALS[Builtins.SCALING],
            height = SETTINGS[Builtins.VIEW_HEIGHT] * GLOBALS[Builtins.SCALING]
        )

        # Create benchmarks.
        self._update_bench = Benchmark(
            window = self._window,
            text = "UT: ",
            y = 30
        )
        self._render_bench = Benchmark(
            window = self._window,
            text = "RT: "
        )

        # Create a scene.
        self._active_scene = R_0_0(
            window = self._window,
            view_width = SETTINGS[Builtins.VIEW_WIDTH],
            view_height = SETTINGS[Builtins.VIEW_HEIGHT],
            on_ended = self.__on_scene_end
        )

    def __create_window(self) -> pyglet.window.Window:
        window = pyglet.window.Window(
            SETTINGS[Builtins.WINDOW_WIDTH] if not SETTINGS[Builtins.FULLSCREEN] else None,
            SETTINGS[Builtins.WINDOW_HEIGHT] if not SETTINGS[Builtins.FULLSCREEN] else None,
            SETTINGS[Builtins.TITLE],
            fullscreen = SETTINGS[Builtins.FULLSCREEN],
            vsync = True,
            resizable = False
        )

        window.push_handlers(self)
        if not SETTINGS[Builtins.DEBUG]:
            window.set_mouse_visible(False)

        return window

    def __on_scene_end(self, bundle: dict):
        print("scene_ended", bundle)
        if bundle["next_scene"]:
            controllers.COLLISION_CONTROLLER.clear()
            controllers.INTERACTION_CONTROLLER.clear()
            self._active_scene.delete()

            if bundle["next_scene"] == scenes.R_0_0:
                self._active_scene = R_0_0(
                    window = self._window,
                    view_width = SETTINGS[Builtins.VIEW_WIDTH],
                    view_height = SETTINGS[Builtins.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_1:
                self._active_scene = R_0_1(
                    window = self._window,
                    view_width = SETTINGS[Builtins.VIEW_WIDTH],
                    view_height = SETTINGS[Builtins.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_2:
                self._active_scene = R_0_2(
                    window = self._window,
                    view_width = SETTINGS[Builtins.VIEW_WIDTH],
                    view_height = SETTINGS[Builtins.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_3:
                self._active_scene = R_0_3(
                    window = self._window,
                    view_width = SETTINGS[Builtins.VIEW_WIDTH],
                    view_height = SETTINGS[Builtins.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_4:
                self._active_scene = R_0_4(
                    window = self._window,
                    view_width = SETTINGS[Builtins.VIEW_WIDTH],
                    view_height = SETTINGS[Builtins.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_5:
                self._active_scene = R_0_5(
                    window = self._window,
                    view_width = SETTINGS[Builtins.VIEW_WIDTH],
                    view_height = SETTINGS[Builtins.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_6:
                self._active_scene = R_0_6(
                    window = self._window,
                    view_width = SETTINGS[Builtins.VIEW_WIDTH],
                    view_height = SETTINGS[Builtins.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )

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
            z_near = -1000,
            z_far = 1000
        )

        # Scale textures using nearest neighbor filtering.
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        # Benchmark measures render time.
        with self._render_bench:
            self._window.clear()

            # Upscaler handles maintaining the wanted output resolution.
            with self._upscaler:
                self._active_scene.draw()

                if SETTINGS[Builtins.DEBUG]:
                    self._render_bench.draw()
                    self._update_bench.draw()

        if SETTINGS[Builtins.DEBUG]:
            self.fps_display.draw()

    def update(self, dt) -> None:
        # Benchmark measures update time.
        with self._update_bench:
            # InputController makes sure every input is handled correctly.
            with controllers.INPUT_CONTROLLER:
                self._active_scene.update(dt)

            # Compute collisions through collision manager.
            controllers.COLLISION_CONTROLLER.update(dt)

    def run(self) -> None:
        pyglet.clock.schedule_interval(self.update, 1.0 / SETTINGS[Builtins.TARGET_FPS])
        # pyglet.clock.schedule(self.update)
        pyglet.app.run()

app = RugHai()
app.run()