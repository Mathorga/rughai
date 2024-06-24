from typing import Callable
import pyglet

import engine.controllers as controllers
from engine.animation import Animation
from engine.node import Node, PositionNode
from engine.sprite_node import SpriteNode
from engine.utils import utils

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

class InventoryNode(Node):
    __slots__ = (
        "ammo_sprites",
        "consumable_slot_image",
        "consumables_slots_sprites",
        "consumables_sprites",
        "world_batch",
        "ui_batch",
        "view_width",
        "view_height",
        "background",
        "view_width",
        "view_height",
        "is_open"
    )

    def __init__(
        self,
        view_width: int,
        view_height: int,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> None:
        self.ammo_sprites: dict[str, SpriteNode] = {}

        # Fetch consumable slot image.
        self.consumable_slot_image: pyglet.image.TextureRegion = pyglet.resource.image("sprites/shadow.png")
        utils.set_anchor(
            resource = self.consumable_slot_image,
            center = True
        )

        # Consumables sprites.
        self.consumables_slots_sprites: list[SpriteNode] = []
        self.consumables_sprites: dict[str, SpriteNode] = {}

        # Batches.
        self.world_batch: pyglet.graphics.Batch | None = world_batch
        self.ui_batch: pyglet.graphics.Batch | None = ui_batch

        self.view_width: int = view_width
        self.view_height: int = view_height

        # Inventory background.
        self.background: SpriteNode | None = None

        # Tells whether the inventory menu is open or closed.
        self.is_open: bool = False

    def create_sprites(self) -> None:
        """
        Creates all inventory sprites.
        """

        # Create background.
        self.background = SpriteNode(
            x = 0.0,
            y = 0.0,
            z = 400.0,
            resource = pyglet.resource.image("sprites/menus/inventory/background.png"),
            batch = self.ui_batch
        )

        consumables_area_size: tuple[int, int] = (
            self.view_width // 2,
            self.view_height // 2
        )
        step: tuple[int, int] = (
            consumables_area_size[0] // controllers.INVENTORY_CONTROLLER.consumables_size[0],
            consumables_area_size[1] // controllers.INVENTORY_CONTROLLER.consumables_size[1]
        )

        # Create all items' slots.
        for i in range(controllers.INVENTORY_CONTROLLER.consumables_size[0]):
            for j in range(controllers.INVENTORY_CONTROLLER.consumables_size[1]):
                position: int = utils.idx2to1(i, j, controllers.INVENTORY_CONTROLLER.consumables_size[1])
                self.consumables_slots_sprites.append(SpriteNode(
                    x = i * step[0] + step[1],
                    y = self.view_height - (j * step[1] + step[1]),
                    z = 500.0,
                    resource = self.consumable_slot_image,
                    batch = self.ui_batch
                ))

        # Create all items' sprites.
        for consumable_position in controllers.INVENTORY_CONTROLLER.consumables_position.items():
            if consumable_position[0] is not None and not consumable_position[0] in self.consumables_sprites:
                # Compute the current position.
                position: tuple[int, int] = utils.idx1to2(consumable_position[1], controllers.INVENTORY_CONTROLLER.consumables_size[1])

                self.consumables_sprites[consumable_position[0]] = SpriteNode(
                    # TODO Scale and shift correctly.
                    x = position[1] * step[0] + step[0],
                    y = self.view_height - (position[0] * step[1] + step[1]),
                    z = 500.0,
                    resource = Animation(source = CONSUMABLES_ANIMATION[consumable_position[0]]).content,
                    batch = self.ui_batch
                )

    def clear_sprites(self) -> None:
        """
        Deletes all inventory sprites.
        """

        # Clear background.
        if self.background is not None:
            self.background.delete()
            self.background = None

        # Clear consumables slots sprites.
        for sprite in self.consumables_slots_sprites:
            sprite.delete()
        self.consumables_slots_sprites.clear()

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

        if self.is_open:
            self.create_sprites()
        else:
            self.clear_sprites()

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

    def update(self, dt: float) -> None:
        # Fetch input.
        inventory_toggled: bool = controllers.INPUT_CONTROLLER.get_inventory_toggle()

        # Use input.
        if inventory_toggled:
            self.toggle()

    def delete(self) -> None:
        self.clear_sprites()