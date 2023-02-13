import pyglet
from energy_bar import EnergyBar

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
        view_width: int,
        view_height: int,
        input_controller: InputController,
        scaling: int = 1
    ):
        super().__init__(
            window = window,
            view_width = view_width,
            view_height = view_height,
            scaling = scaling,
            cam_speed = 5.0
        )

        # Define a tilemap.
        tile_size = 8
        tile_map:TileMap = TileMap.from_tmj_file(
            source = "tilemaps/rughai/hub_50_50.tmj",
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
            x = (tile_map.map_width * tile_size) // 2,
            y = (tile_map.map_height * tile_size) // 2,
            image = pyglet.resource.image("bg.png"),
            scaling = scaling
        )

        iryo = Iryo(
            input_controller = input_controller,
            x = 10 * tile_size,
            y = 10 * tile_size,
            scaling = scaling
        )

        # Define tree prop.
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

        # Define energy bar.
        bar_img = pyglet.resource.image("sprites/energy_bar.png")
        bar_img.anchor_x = 0
        bar_img.anchor_y = bar_img.height
        energy_bar = EnergyBar(
            image = bar_img,
            x = 4,
            y = view_height - 4,
            scaling = scaling
        )
        health_bar = EnergyBar(
            image = bar_img,
            x = 4,
            y = view_height - 12,
            scaling = scaling
        )

        self.add_object(bg)
        self.add_object(tile_map)
        self.add_object(iryo, cam_target = True, sorted = True)
        self.add_object(tree, sorted = True)
        self.add_object(energy_bar, ui = True)
        self.add_object(health_bar, ui = True)