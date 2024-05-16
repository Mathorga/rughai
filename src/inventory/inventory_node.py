import os
from typing import Callable
import pyglet

import engine.controllers as controllers
from engine.animation import Animation
from engine.node import PositionNode
from engine.settings import GLOBALS, SETTINGS, Keys
from engine.sprite_node import SpriteNode
from engine.utils.utils import idx1to2, idx2to1

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
    "caroot": "sprites/items/consumables/caroot.json",
    "bloobary": "sprites/items/consumables/bloobary.json",
    "hokbary": "sprites/items/consumables/hokbary.json",
    "energy_drink": "sprites/items/consumables/energy_drink.json"
}

CONSUMABLES_USE: dict[str, Callable] = {
    "caroot": lambda: print("you ate a caroot"),
    "bloobary": lambda: print("you ate a bloobary"),
    "hokbary": lambda: print("you ate a hokbary"),
    "energy_drink": lambda: print("you got a drink")
}

AMMO_ICON_ANIMATION: dict[str, Animation] = {
    # "arrow": Animation(source = "sprites/items/ammo/arrow.json"),
    # "fire_arrow": Animation(source = "sprites/items/ammo/fire_arrow.json"),
}

class InventoryNode:
    __slots__ = (
        "ammo_sprites",
        "consumables_sprites",
        "world_batch",
        "ui_batch",
        "is_open"
    )

    def __init__(self) -> None:
        self.ammo_sprites: dict[str, SpriteNode] = {}

        # Consumables sprites.
        self.consumables_sprites: dict[str, SpriteNode] = {}

        # Batches.
        self.world_batch: pyglet.graphics.Batch | None = None
        self.ui_batch: pyglet.graphics.Batch | None = None

        # Tells whether the inventory menu is open or closed.
        self.is_open: bool = True

    def set_batches(
        self,
        world_batch: pyglet.graphics.Batch | None,
        ui_batch: pyglet.graphics.Batch | None
    ) -> None:
        """
        Saves the provided batches for sprites creation.
        """

        self.world_batch = world_batch
        self.ui_batch = ui_batch

        if world_batch is None or ui_batch is None:
            return

        # Create sprites.
        # for quick in controllers.INVENTORY_CONTROLLER.quicks:
        #     if quick is not None:
        #         self.consumables_sprites[quick]

        if self.is_open:
            for consumable_position in controllers.INVENTORY_CONTROLLER.consumables_position.items():
                if consumable_position[0] is not None and not consumable_position[0] in self.consumables_sprites:
                    position: tuple[int, int] = idx1to2(consumable_position[1], controllers.INVENTORY_CONTROLLER.consumables_size[1])
                    self.consumables_sprites[consumable_position[0]] = SpriteNode(
                        # TODO Scale and shift correctly.
                        x = position[1] * GLOBALS[Keys.SCALING] + 20,
                        y = position[0] * GLOBALS[Keys.SCALING] + 20,
                        resource = Animation(source = CONSUMABLES_ANIMATION[consumable_position[0]]).content,
                        batch = ui_batch
                    )

    def clear_batches(self) -> None:
        """
        Unsets all batches and deletes any existing sprite using them.
        """

        self.world_batch = None
        self.ui_batch = None

        # Clear consumables sprites.
        for sprite in self.consumables_sprites.values():
            sprite.delete()
        self.consumables_sprites.clear()

        # Clear ammo sprites.
        for sprite in self.ammo_sprites.values():
            sprite.delete()
        self.ammo_sprites.clear()

    def toggle(self) -> None:
        """
        Opens or closes the inventory based on its current state.
        """

        self.is_open = not self.is_open
        # TODO

    def use_consumable(self, consumable: str) -> None:
        """
        Uses (consumes) the item with id [consumable].
        """

        count: int | None = controllers.INVENTORY_CONTROLLER.consumables_count[consumable]

        if count is None or count <= 0:
            return

        # Actually use the consumable.
        CONSUMABLES_USE[consumable]()

        # The consumable was consumed, so decrease its count by 1.
        controllers.INVENTORY_CONTROLLER.consumables_count[consumable] -= 1

        # Remove the consumable from the inventory if it was the last one of its kind.
        if controllers.INVENTORY_CONTROLLER.consumables_count[consumable] <= 0:
            controllers.INVENTORY_CONTROLLER.consumables_position.pop(consumable)
            self.consumables_sprites.pop(consumable)

    def equip_consumable(self, consumable: str) -> None:
        """
        Equips [consumable] to a quick slot.
        """
        # TODO

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