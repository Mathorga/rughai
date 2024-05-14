import os
from typing import Callable
import pyglet
from pyglet.graphics import Batch

from engine.animation import Animation
from engine.node import PositionNode
from engine.sprite_node import SpriteNode

class RealWorldItemNode(PositionNode):
    __slots__ = (
        "sprite"
    )

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        sprite: SpriteNode | None = None,
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.sprite: SpriteNode | None = sprite
        if self.sprite is not None:
            self.add_component(self.sprite)

CONSUMABLES_ANIMATION: dict[str, str] = {
    # "caroot": "sprites/items/consumables/caroot.json",
    "bloobary": "sprites/items/consumables/bloobary.json"
}

CONSUMABLES_USE: dict[str, Callable] = {
    "caroot": lambda: print("you ate a caroot"),
    "bloobary": lambda: print("you ate a bloobary")
}

AMMO_ICON_ANIMATION: dict[str, Animation] = {
    # "arrow": Animation(source = "sprites/items/ammo/arrow.json"),
    # "fire_arrow": Animation(source = "sprites/items/ammo/fire_arrow.json"),
}

class InventoryNode:
    """
    Holds all inventory data and provides accessors to it.
    """

    __slots__ = (
        "quicks_count",
        "quicks",
        "current_ammo",
        "ammo",
        "currencies",
        "consumables_count",
        "consumables",
        "consumables_sprite",
        "world_batch",
        "ui_batch",
        "is_open"
    )

    def __init__(self) -> None:
        # Currently equipped quick-access consumables.
        self.quicks_count: int = 4
        self.quicks: list[str | None] = [None for _ in range(self.quicks_count)]

        # Currently equipped ammo.
        self.current_ammo: str | None = None
        self.ammo: list[str] = []

        self.currencies: dict[str, int] = {}

        # Current amount for each consumable.
        self.consumables_count: dict[str, int] = {}

        # Consumables.
        self.consumables: list[list[str]] = []
        self.consumables_sprite: dict[str, SpriteNode] = {}

        # Batches.
        self.world_batch: pyglet.graphics.Batch | None = None
        self.ui_batch: pyglet.graphics.Batch | None = None

        # Tells whether the inventory menu is open or closed.
        self.is_open: bool = False

    def set_batches(
        self,
        world_batch: pyglet.graphics.Batch | None,
        ui_batch: pyglet.graphics.Batch | None
    ) -> None:
        self.world_batch = world_batch
        self.ui_batch = ui_batch

        if world_batch is None or ui_batch is None:
            return

        # Create sprites.
        

    def toggle(self) -> None:
        """
        Opens or closes the inventory based on its current state.
        """
        # TODO

    def use_consumable(self, position: tuple[int, int]) -> None:
        CONSUMABLES_USE[self.consumables[position[0]][position[1]]]()

    def load_file(self, source: str) -> None:
        """
        Reads and stores all inventory data from the file provided in [source].
        """

        abs_path: str = os.path.join(pyglet.resource.path[0], source)

        # Just return if the source file is not found.
        if not os.path.exists(abs_path):
            return

        # TODO Open file and read data from it.
        pass