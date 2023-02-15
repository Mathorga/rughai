import pyglet

from engine.node import Node
from engine.scene_node import SceneNode
from engine.sprite_node import SpriteNode
from engine.input_controller import InputController
from engine.tilemap_node import TilemapNode, Tileset

from player_node import PlayerNode

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

        self.__scene = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            scaling = scaling,
            cam_speed = 5.0
        )

        # Define a tilemap.
        tile_size = 8
        tilemap = TilemapNode.from_tmj_file(
            source = "tilemaps/rughai/hub_50_50.tmj",
            tile_set = Tileset(
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
        bg = SpriteNode(
            resource = pyglet.resource.image("bg.png"),
            on_animation_end = lambda : None,
            x = (tilemap.map_width * tile_size) // 2,
            y = (tilemap.map_height * tile_size) // 2,
            scaling = scaling
        )

        iryo = PlayerNode(
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
        tree = SpriteNode(
            resource = tree_img,
            on_animation_end = lambda : None,
            x = 5 * tile_size,
            y = 5 * tile_size,
            scaling = scaling
        )

        # Define energy bar.
        bar_img = pyglet.resource.image("sprites/energy_bar.png")
        bar_img.anchor_x = 0
        bar_img.anchor_y = bar_img.height
        energy_bar = SpriteNode(
            resource = bar_img,
            on_animation_end = lambda : None,
            x = 4,
            y = view_height - 4,
            scaling = scaling
        )
        health_bar = SpriteNode(
            resource = bar_img,
            on_animation_end = lambda : None,
            x = 4,
            y = view_height - 12,
            scaling = scaling
        )

        self.__scene.add_child(bg)
        self.__scene.add_child(tilemap)
        self.__scene.add_child(iryo, cam_target = True, sorted = True)
        self.__scene.add_child(tree, sorted = True)
        self.__scene.add_child(energy_bar, ui = True)
        self.__scene.add_child(health_bar, ui = True)

    def render(self) -> None:
        self.__scene.render()

    def update(self, dt) -> None:
        self.__scene.update(dt)