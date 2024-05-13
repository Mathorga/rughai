import os.path
import pyglet
import pyglet.gl as gl

import engine.controllers as controllers
from engine.benchmark import Benchmark
from engine.dungen.dungen import random_walk
from engine.upscaler import TrueUpscaler, Upscaler
from engine.settings import GLOBALS, SETTINGS, Keys, load_settings

import constants.scenes as scenes
from inventory.inventory_node import InventoryNode

from scenes.rughai.r_0_0 import R_0_0
from scenes.rughai.r_0_1 import R_0_1
from scenes.rughai.r_0_2 import R_0_2
from scenes.rughai.r_0_3 import R_0_3
from scenes.rughai.r_0_4 import R_0_4
from scenes.rughai.r_0_5 import R_0_5
from scenes.rughai.r_0_6 import R_0_6
from scenes.rughai.r_0_7 import R_0_7
from scenes.rughai.r_0_8 import R_0_8

FRAGMENT_SOURCE = """
    #version 150 core
    in vec4 vertex_colors;
    in vec3 texture_coords;
    out vec4 final_color;

    uniform sampler2D sprite_texture;
    uniform float dt;

    void main() {
        final_color = texture(sprite_texture, texture_coords.xy) * vertex_colors;

        // Dips to red on long rendered frames.
        //final_color.gb *= (1.0 - (dt - 0.01) * 100.0);

        // Rotate colors.
        //final_color.rgb = final_color.gbr;

        // Black/white.
        //float brightness = (final_color.r + final_color.g + final_color.b) / 3.0;
        //final_color = vec4(brightness, brightness, brightness, final_color.a);

        // Shows current xy coords on top of real colors.
        //final_color.rg *= texture_coords.xy;

        // Negative colors.
        //final_color.rgb = 1.0 - final_color.rgb;

        if (final_color.a < 0.01) {
            discard;
        }
    }
"""
vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
frag_shader = pyglet.graphics.shader.Shader(FRAGMENT_SOURCE, "fragment")
upscaler_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

class Rughai:
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
        self.window = self.__create_window()
        self.fps_display = pyglet.window.FPSDisplay(
            window = self.window,
            color = (0x00, 0x00, 0x00, 0xFF),
            samples = 16
        )

        # Controllers.
        controllers.create_controllers(window = self.window)

        # On retina Macs everything is rendered 2x-zoomed for some reason. compensate for this using a platform scaling.
        platform_scaling: float = 0.5 if "macOS" in GLOBALS[Keys.PLATFORM] else 1.0

        # Compute pixel scaling (minimum unit is <1 / scaling>)
        # Using a scaling of 1 means that movements are pixel-perfect (aka nothing moves by sub-pixel values).
        # Using a scaling of 5 means that the minimum unit is 1/5 of a pixel.
        GLOBALS[Keys.SCALING] = 1 if SETTINGS[Keys.PIXEL_PERFECT] else int(min(
            self.window.width // SETTINGS[Keys.VIEW_WIDTH],
            self.window.height // SETTINGS[Keys.VIEW_HEIGHT]
        ) * platform_scaling)

        self._upscaler = TrueUpscaler(
            window = self.window,
            render_width = int((SETTINGS[Keys.VIEW_WIDTH] * GLOBALS[Keys.SCALING]) / platform_scaling),
            render_height = int((SETTINGS[Keys.VIEW_HEIGHT] * GLOBALS[Keys.SCALING]) / platform_scaling),
            program = upscaler_program
        )

        # Create benchmarks.
        self._update_bench = Benchmark(
            window = self.window,
            text = "UT: ",
            y = 80
        )
        self._render_bench = Benchmark(
            window = self.window,
            text = "RT: ",
            y = 50
        )

        # Create a scene.
        self.__active_scene = R_0_0(
            window = self.window,
            view_width = SETTINGS[Keys.VIEW_WIDTH],
            view_height = SETTINGS[Keys.VIEW_HEIGHT],
            on_ended = self.__on_scene_end
        )

    def __create_window(self) -> pyglet.window.Window:
        window = pyglet.window.Window(
            width = SETTINGS[Keys.WINDOW_WIDTH] if not SETTINGS[Keys.FULLSCREEN] else None,
            height = SETTINGS[Keys.WINDOW_HEIGHT] if not SETTINGS[Keys.FULLSCREEN] else None,
            caption = SETTINGS[Keys.TITLE],
            fullscreen = SETTINGS[Keys.FULLSCREEN],
            vsync = True,
            resizable = True
        )

        # Set the clear color (used when the window is cleared).
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)

        window.push_handlers(self)
        if not SETTINGS[Keys.DEBUG]:
            window.set_mouse_visible(False)

        return window

    def __on_scene_end(self, bundle: dict):
        print("scene_ended", bundle)
        if bundle["next_scene"]:
            # First delete the current scene then clear controllers.
            self.__active_scene.delete()
            controllers.COLLISION_CONTROLLER.clear()
            controllers.INTERACTION_CONTROLLER.clear()

            if bundle["next_scene"] == scenes.R_0_0:
                self.__active_scene = R_0_0(
                    window = self.window,
                    view_width = SETTINGS[Keys.VIEW_WIDTH],
                    view_height = SETTINGS[Keys.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_1:
                self.__active_scene = R_0_1(
                    window = self.window,
                    view_width = SETTINGS[Keys.VIEW_WIDTH],
                    view_height = SETTINGS[Keys.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_2:
                self.__active_scene = R_0_2(
                    window = self.window,
                    view_width = SETTINGS[Keys.VIEW_WIDTH],
                    view_height = SETTINGS[Keys.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_3:
                self.__active_scene = R_0_3(
                    window = self.window,
                    view_width = SETTINGS[Keys.VIEW_WIDTH],
                    view_height = SETTINGS[Keys.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_4:
                self.__active_scene = R_0_4(
                    window = self.window,
                    view_width = SETTINGS[Keys.VIEW_WIDTH],
                    view_height = SETTINGS[Keys.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_5:
                self.__active_scene = R_0_5(
                    window = self.window,
                    view_width = SETTINGS[Keys.VIEW_WIDTH],
                    view_height = SETTINGS[Keys.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_6:
                self.__active_scene = R_0_6(
                    window = self.window,
                    view_width = SETTINGS[Keys.VIEW_WIDTH],
                    view_height = SETTINGS[Keys.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_7:
                self.__active_scene = R_0_7(
                    window = self.window,
                    view_width = SETTINGS[Keys.VIEW_WIDTH],
                    view_height = SETTINGS[Keys.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )
            elif bundle["next_scene"] == scenes.R_0_8:
                self.__active_scene = R_0_8(
                    window = self.window,
                    view_width = SETTINGS[Keys.VIEW_WIDTH],
                    view_height = SETTINGS[Keys.VIEW_HEIGHT],
                    bundle = bundle,
                    on_ended = self.__on_scene_end
                )

    def on_draw(self) -> None:
        """
        Draws everything to the screen.
        """

        # Update window matrix.
        self.window.projection = pyglet.math.Mat4.orthogonal_projection(
            left = 0,
            right = self.window.width,
            bottom = 0,
            top = self.window.height,
            # For some reason near and far planes are inverted in sign, so that -500 means 500 and 1024 means -1024.
            z_near = -3000,
            z_far = 3000
        )

        # Benchmark measures render time.
        with self._render_bench:
            self.window.clear()

            # Upscaler handles maintaining the wanted output resolution.
            with self._upscaler:
                self.__active_scene.draw()

                if SETTINGS[Keys.DEBUG]:
                    self._render_bench.draw()
                    self._update_bench.draw()

                if SETTINGS[Keys.DEBUG]:
                    self.fps_display.draw()

    def update(self, dt: float) -> None:
        # upscaler_program["dt"] = dt
        # Benchmark measures update time.
        with self._update_bench:
            # InputController makes sure every input is handled correctly.
            with controllers.INPUT_CONTROLLER:
                self.__active_scene.update(dt)

            # Compute collisions through collision manager.
            controllers.COLLISION_CONTROLLER.update(dt)

    def run(self) -> None:
        pyglet.clock.schedule_interval(self.update, 1.0 / SETTINGS[Keys.TARGET_FPS])
        # pyglet.clock.schedule(self.update)
        pyglet.app.run()

# map_res = random_walk(
#     map_width = 30,
#     map_height = 30,
#     lifespan = 120,
#     max_reach = 8
# )

# map_res_trans: list[list[str]] = []
# for line in map_res:
#     map_res_trans.append(list(map(lambda x: "@" if x == 0 else ".", line)))

# print(map_res_trans)

app = Rughai()
app.run()