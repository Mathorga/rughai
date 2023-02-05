import pyglet

from engine.scene import Scene
from engine.background import Background
from engine.tile_map import TileMap, TileSet
from engine.input_controller import InputController
from engine.prop import Prop

import settings
from iryo import Iryo

class RugHaiHub(Scene):
    def __init__(
        self,
        window: pyglet.window.Window,
        input_controller: InputController,
        scaling: int = 1
    ):
        super().__init__(
            window = window,
            view_width = settings.VIEW_WIDTH,
            view_height = settings.VIEW_HEIGHT,
            scaling = scaling,
            cam_speed = 5.0
        )

        # Define a tilemap.
        tile_size = 8
        tile_map = TileMap.from_tmj_file(
            source = "tilemaps/rughai/hub.tmj",
            tile_set = TileSet(
                source = "tilemaps/tilesets/rughai/ground.png",
                tile_width = tile_size,
                tile_height = tile_size
            ),
            scaling = scaling
        )

        # Define a background.
        bg_image = pyglet.resource.image("bg.png")
        bg_image.anchor_x = bg_image.width / 2
        bg_image.anchor_y = bg_image.height / 2
        bg = Background(
            x = (tile_map.map_width * tile_size) / 2,
            y = (tile_map.map_height * tile_size) / 2,
            image = pyglet.resource.image("bg.png"),
            scaling = scaling
        )

        iryo = Iryo(
            input_controller = input_controller,
            x = 10 * tile_size,
            y = 10 * tile_size,
            scaling = scaling
        )

        # Define tree.
        # TODO Use dedicated class.
        tree_img = pyglet.resource.image("sprites/rughai/prop/tree_l.png")
        tree_img.anchor_x = tree_img.width / 2
        tree_img.anchor_y = 3
        tree = Prop(
            image = tree_img,
            x = 5 * tile_size,
            y = 5 * tile_size,
            scaling = scaling
        )

        self.add_object(bg, sorted = False)
        self.add_object(tile_map, sorted = False)
        self.add_object(iryo, cam_target = True, sorted = True)
        self.add_object(tree, sorted = True)