import os.path

import pyglet
import pyglet.gl as gl
import pyglet.math as pm

import settings
from application import Scene
from engine.input_controller import InputController
from engine.character import Player
from engine.tile_map import TileMap, TileSet

# Set resources path.
pyglet.resource.path = [f"{os.path.dirname(__file__)}/../assets"]
pyglet.resource.reindex()

# Create a window.
win = pyglet.window.Window(
    settings.WINDOW_WIDTH if not settings.FULLSCREEN else None,
    settings.WINDOW_HEIGHT if not settings.FULLSCREEN else None,
    settings.TITLE,
    fullscreen = settings.FULLSCREEN,
    resizable = True
)
win.set_minimum_size(settings.VIEW_WIDTH, settings.VIEW_HEIGHT)
fps_display = pyglet.window.FPSDisplay(win) if settings.DEBUG else None

# Create an input handler.
input_controller = InputController(window = win)

# Create a scene.
scene = Scene(
    window = win,
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

iryo = Player(
    res_folder = "sprites/rughai/iryo/iryo_idle.gif",
    x = 0,
    y = 0,
    input_controller = input_controller
)

scene.add_object(rughai_ground_tile_map)
scene.add_object(iryo, cam_target = True)


@win.event
def on_draw():
    win.clear()
    scene.draw()

    if fps_display != None:
        fps_display.draw()

def update(dt):
    scene.update(dt)


# Enable depth testing in order to allow for depth sorting.
# TODO Try this out! Use the z coordinate as depth!
#gl.glEnable(gl.GL_DEPTH_TEST)

# Scale textures using nearest neighbor filtering.
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

pyglet.clock.schedule_interval(update, 1.0 / settings.TARGET_FPS)
pyglet.app.run()