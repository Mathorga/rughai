import pyglet

from engine.node import Node
from engine.node import PositionNode
from engine.scene_node import Bounds, SceneNode
from engine.sensor_node import SensorNode
from engine.sprite_node import SpriteNode
from engine.input_controller import InputController
from engine.tilemap_node import TilemapNode, Tileset

from player_node import PlayerNode
from duk_node import DukNode

class RugHaiHub(Node):
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        input_controller: InputController,
        scaling: int = 1
    ):
        super().__init__()

        # Define a tilemap.
        tile_size = 8
        # tilemap = TilemapNode.from_tmj_file(
        #     source = "tilemaps/rughai/main_hub.tmj",
        #     tileset = Tileset(
        #         sources = ["tilemaps/tilesets/rughai/main_tileset.png"],
        #         tile_width = tile_size,
        #         tile_height = tile_size
        #     ),
        #     scaling = scaling
        # )
        tilemaps = TilemapNode.from_tmx_file(
            source = "tilemaps/rughai/main_hub.tmx",
            scaling = scaling
        )

        # Define a background.
        bg_image = pyglet.resource.image("bg.png")
        bg_image.anchor_x = bg_image.width / 2
        bg_image.anchor_y = bg_image.height / 2
        bg = SpriteNode(
            resource = pyglet.resource.image("bg.png"),
            on_animation_end = lambda : None,
            x = (tilemaps[0].map_width * tile_size) // 2,
            y = (tilemaps[0].map_height * tile_size) // 2,
            scaling = scaling
        )

        # Player.
        cam_target = PositionNode()
        iryo = PlayerNode(
            input_controller = input_controller,
            cam_target = cam_target,
            x = 10 * tile_size,
            y = 10 * tile_size,
            scaling = scaling
        )

        # Duk.
        duk = DukNode(
            x = 10 * tile_size,
            y = 8 * tile_size,
            scaling = scaling
        )

        # Define tree prop.
        # TODO Use dedicated class.
        tree_img = pyglet.resource.image("sprites/rughai/prop/tree_l.png")
        tree_img.anchor_x = tree_img.width / 2
        tree_img.anchor_y = 3
        tree = SpriteNode(
            resource = tree_img,
            x = 5 * tile_size,
            y = 5 * tile_size,
            scaling = scaling
        )

        # Place doors.
        bottom_door = SensorNode(
            x = 25 * tile_size,
            y = 0,
            width = 50 * tile_size,
            height = 2 * tile_size,
            anchor_x = 25 * tile_size,
            anchor_y = 2 * tile_size,
            scaling = scaling,
            visible = True
        )

        # Define energy bars.
        bar_img = pyglet.resource.image("sprites/energy_bar.png")
        bar_img.anchor_x = 0
        bar_img.anchor_y = bar_img.height
        energy_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 4,
            scaling = scaling
        )
        health_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 12,
            scaling = scaling
        )

        self.__scene = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            scaling = scaling,
            cam_speed = 5.0,
            cam_bounds = Bounds(
                top = 50 * tile_size,
                bottom = 0,
                right = 50 * tile_size,
                scaling = scaling
            )
        )

        self.__scene.add_child(bg)
        # self.__scene.add_child(tilemap)
        self.__scene.add_children(tilemaps)
        self.__scene.add_child(cam_target, cam_target = True)
        self.__scene.add_child(iryo, sorted = True)
        self.__scene.add_child(duk, sorted = True)
        self.__scene.add_child(tree, sorted = True)
        self.__scene.add_child(energy_bar, ui = True)
        self.__scene.add_child(health_bar, ui = True)
        self.__scene.add_child(bottom_door)

    def draw(self) -> None:
        self.__scene.draw()

    def update(self, dt) -> None:
        self.__scene.update(dt)