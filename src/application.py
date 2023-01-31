import pyglet
import pyglet.gl as gl
import pyglet.math as pm
from engine.playable import Playable

import settings
from engine.input_controller import InputController
from engine.scene import Scene
from engine.tile_map import TileMap, TileSet

class Application:
    def __init__(
        self,
        debug: bool = False
    ):
        pyglet.resource.path = ["../assets"]
        pyglet.resource.reindex()

        # Create a new window.
        self._window = pyglet.window.Window(
            settings.WINDOW_WIDTH if not settings.FULLSCREEN else None,
            settings.WINDOW_HEIGHT if not settings.FULLSCREEN else None,
            settings.TITLE,
            fullscreen = settings.FULLSCREEN,
            resizable = True
        )
        self._window.set_minimum_size(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self._window.push_handlers(self)
        self.__fps_display = pyglet.window.FPSDisplay(self._window) if debug else None

        # Create a new input controller.
        self._input = InputController(
            window = self._window
        )

        # Create the starting scene.
        self._scene = Scene(
            window = self._window,
            view_width = settings.VIEW_WIDTH,
            view_height = settings.VIEW_HEIGHT
        )
        # Add a tilemap to the app.
        rughai_ground_tile_map = TileMap.from_tmj_file(
            source = "tilemaps/rughai/hub.tmj",
            order = 1,
            tile_set = TileSet(
                source = "tilemaps/tilesets/rughai/ground.png",
                tile_width = 8,
                tile_height = 8
            ),
        )

        iryo = Playable(
            res_folder = "sprites/rughai/iryo/iryo_idle.gif",
            x = 0,
            y = 0,
            input_controller = self._input
        )

        self._scene.add_object(rughai_ground_tile_map)
        self._scene.add_object(iryo, cam_target = True)

    def on_draw(self):
        self._window.clear()
        self._scene.draw()

        if self.__fps_display != None:
            self.__fps_display.draw()

    def update(self, dt):
        self._scene.update(dt)

    def run(self):
        # Enable depth testing in order to allow for depth sorting.
        # TODO Try this out! Use the z coordinate as depth!
        #gl.glEnable(gl.GL_DEPTH_TEST)

        # Scale textures using nearest neighbor filtering.
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

        pyglet.clock.schedule_interval(self.update, 1.0 / settings.TARGET_FPS)
        pyglet.app.run()
        