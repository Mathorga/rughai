import math
import random
from typing import Callable
import pyglet
import pyglet.math as pm

import engine.controllers as controllers
from engine.animation import Animation
from engine.cursor_input_handler import CursorInputHandler
from engine.inventory_controller import SECTION_OVERFLOW_NONE, SECTION_OVERFLOW_WRAP, MenuSection
from engine.node import Node, PositionNode
from engine.settings import GLOBALS, Keys
from engine.shapes.rect_node import RectNode
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

class MenuNode(Node):
    __slots__ = (
        "__view_width",
        "__view_height",
        "__world_batch",
        "__ui_batch",
        "sections",
        "__slot_image",
        "__slots_sprites",
        "__cursor_input",
        "__cursor_section",
        "__cursor_slot_position",
        "__cursor_image",
        "__cursor_sprite"
    )

    def __init__(
        self,
        view_width: int,
        view_height: int,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__()

        self.__view_width: int = view_width
        self.__view_height: int = view_height

        ################ Batches ################
        self.__world_batch: pyglet.graphics.Batch | None = world_batch
        self.__ui_batch: pyglet.graphics.Batch | None = ui_batch

        self.sections: list[RectNode] = []

        ################ Slots ################
        # Fetch a generic slot image.
        self.__slot_image: pyglet.image.Texture = pyglet.resource.image("sprites/menus/inventory/consumable_slot.png")
        utils.set_anchor(
            resource = self.__slot_image,
            center = True
        )
        self.__slots_sprites: list[SpriteNode] = []

        ################ Cursor ################
        # Cursor movement handler.
        self.__cursor_input: CursorInputHandler = CursorInputHandler(
            kick_time = 0.5,
            step_time = 0.2,
            up_keys = [pyglet.window.key.I],
            left_keys = [pyglet.window.key.J],
            down_keys = [pyglet.window.key.K],
            right_keys = [pyglet.window.key.L],
        )

        # The section the cursor is currently located in.
        self.__cursor_section: str = list(controllers.MENU_CONTROLLER.sections)[0]

        # The position the cursor currently highlights inside its current section.
        self.__cursor_slot_position: tuple[int, int] = (0, 0)

        # Cursor sprite data.
        self.__cursor_image: Animation = Animation(source = "sprites/menus/inventory/inventory_cursor.json")
        self.__cursor_sprite: SpriteNode | None = None

    def update(self, dt: float) -> None:
        super().update(dt = dt)

        # Fetch input.
        inventory_toggled: bool = controllers.INPUT_CONTROLLER.get_inventory_toggle()

        self.__cursor_input.update(dt = dt)

        if self.__cursor_sprite is not None:
            self.__cursor_sprite.update(dt = dt)

        # Use input.
        if inventory_toggled:
            self.toggle()

        if controllers.MENU_CONTROLLER.is_open:
            # Fetch movement from input handler and update cursor.
            self.__update_cursor_position(self.__cursor_input.get_movement())

    def delete(self) -> None:
        self.clear_sprites()

    def __compute_overflow(
        self,
        movement: pm.Vec2
    ) -> None:
        # Fetch current cursor section.
        cursor_section: MenuSection = controllers.MENU_CONTROLLER.sections[self.__cursor_section]

        # Compute updated cursor position.
        updated_slot_position_x: int = self.__cursor_slot_position[0] + int(movement.x)
        updated_slot_position_y: int = self.__cursor_slot_position[1] + int(movement.y)
        
        # Right.
        if updated_slot_position_x > cursor_section.slots[0] - 1:
            right_overflow: str = cursor_section.overflow.right
            if right_overflow == SECTION_OVERFLOW_NONE:
                updated_slot_position_x = cursor_section.slots[0] - 1
            else:
                updated_slot_position_x = 0

                # Make sure to jump to the new section if provided.
                if right_overflow != SECTION_OVERFLOW_WRAP:
                    self.__cursor_section = right_overflow

                    # Make sure the other axis does not overflow.
                    cursor_section: MenuSection = controllers.MENU_CONTROLLER.sections[self.__cursor_section]
                    updated_slot_position_y = int(utils.clamp(updated_slot_position_y, 0, cursor_section.slots[1] - 1))

        # Left.
        if updated_slot_position_x < 0:
            left_overflow: str = cursor_section.overflow.left
            if left_overflow == SECTION_OVERFLOW_NONE:
                updated_slot_position_x = 0
            elif left_overflow == SECTION_OVERFLOW_WRAP:
                updated_slot_position_x = cursor_section.slots[0] - 1
            else:
                right_section: MenuSection = controllers.MENU_CONTROLLER.sections[left_overflow]
                updated_slot_position_x = right_section.slots[0] - 1

                # Make sure to jump to the new section if provided.
                if left_overflow != SECTION_OVERFLOW_WRAP:
                    self.__cursor_section = left_overflow

                    # Make sure the other axis does not overflow.
                    cursor_section: MenuSection = controllers.MENU_CONTROLLER.sections[self.__cursor_section]
                    updated_slot_position_y = int(utils.clamp(updated_slot_position_y, 0, cursor_section.slots[1] - 1))

        # Top.
        if updated_slot_position_y > cursor_section.slots[1] - 1:
            top_overflow: str = cursor_section.overflow.top
            if top_overflow == SECTION_OVERFLOW_NONE:
                updated_slot_position_y = cursor_section.slots[1] - 1
            else:
                updated_slot_position_y = 0

                # Make sure to jump to the new section if provided.
                if top_overflow != SECTION_OVERFLOW_WRAP:
                    self.__cursor_section = top_overflow

                    # Make sure the other axis does not overflow.
                    cursor_section: MenuSection = controllers.MENU_CONTROLLER.sections[self.__cursor_section]
                    updated_slot_position_x = int(utils.clamp(updated_slot_position_x, 0, cursor_section.slots[0] - 1))

        # Bottom.
        if updated_slot_position_y < 0:
            bottom_overflow: str = cursor_section.overflow.bottom
            if bottom_overflow == SECTION_OVERFLOW_NONE:
                updated_slot_position_y = 0
            elif bottom_overflow == SECTION_OVERFLOW_WRAP:
                updated_slot_position_y = cursor_section.slots[1] - 1
            else:
                right_section: MenuSection = controllers.MENU_CONTROLLER.sections[bottom_overflow]
                updated_slot_position_y = right_section.slots[1] - 1

                # Make sure to jump to the new section if provided.
                if bottom_overflow != SECTION_OVERFLOW_WRAP:
                    self.__cursor_section = bottom_overflow

                    # Make sure the other axis does not overflow.
                    cursor_section: MenuSection = controllers.MENU_CONTROLLER.sections[self.__cursor_section]
                    updated_slot_position_x = int(utils.clamp(updated_slot_position_x, 0, cursor_section.slots[0] - 1))

        # Update the current cursor slot position.
        self.__cursor_slot_position = (
            updated_slot_position_x,
            updated_slot_position_y
        )

    def __update_cursor_position(self, movement: pm.Vec2) -> None:
        # Check for overflows.
        # The overflow checks update the current section and slot coordinates of the cursor.
        self.__compute_overflow(
            movement = movement
        )

        # Fetch current cursor section.
        cursor_section: MenuSection = controllers.MENU_CONTROLLER.sections[self.__cursor_section]

        section_position: tuple[float, float] = (
            cursor_section.position[0] * self.__view_width,
            cursor_section.position[1] * self.__view_height
        )
        section_size: tuple[float, float] = (
            cursor_section.size[0] * self.__view_width,
            cursor_section.size[1] * self.__view_height
        )

        if self.__cursor_sprite is not None:
            self.__cursor_sprite.set_position(
                position = (
                    section_position[0] + (section_size[0] / (cursor_section.slots[0] + 1) * (self.__cursor_slot_position[0] + 1)),
                    section_position[1] + (section_size[1] / (cursor_section.slots[1] + 1) * (self.__cursor_slot_position[1] + 1)),
                ),
                z = 450
            )

    def create_sprites(self) -> None:
        """
        Creates all menu sprites.
        """

        for section_name in controllers.MENU_CONTROLLER.sections:
            section: MenuSection = controllers.MENU_CONTROLLER.sections[section_name]
            print(section)
            section_position: tuple[float, float] = (
                section.position[0] * self.__view_width,
                section.position[1] * self.__view_height
            )
            section_size: tuple[float, float] = (
                section.size[0] * self.__view_width,
                section.size[1] * self.__view_height
            )

            self.sections.append(RectNode(
                x = section.position[0] * self.__view_width,
                y = section.position[1] * self.__view_height,
                width = int((section.position[0] + section.size[0]) * self.__view_width),
                height = int((section.position[1] + section.size[1]) * self.__view_height),
                color = (
                    random.randint(0x00, 0xFF),
                    random.randint(0x00, 0xFF),
                    random.randint(0x00, 0xFF),
                    0x7F
                ),
                batch = self.__ui_batch
            ))

            # Create all slots' sprites.
            for i in range(section.slots[0]):
                for j in range(section.slots[1]):
                    self.__slots_sprites.append(SpriteNode(
                        resource = self.__slot_image,
                        x = section_position[0] + (section_size[0] / (section.slots[0] + 1) * (i + 1)),
                        y = section_position[1] + (section_size[1] / (section.slots[1] + 1) * (j + 1)),
                        z = 425.0,
                        batch = self.__ui_batch
                    ))

        # Fetch current cursor section.
        cursor_section: MenuSection = controllers.MENU_CONTROLLER.sections[self.__cursor_section]
        section_position: tuple[float, float] = (
            cursor_section.position[0] * self.__view_width,
            cursor_section.position[1] * self.__view_height
        )
        section_size: tuple[float, float] = (
            cursor_section.size[0] * self.__view_width,
            cursor_section.size[1] * self.__view_height
        )

        # Create cursor sprite.
        self.__cursor_sprite = SpriteNode(
            resource = self.__cursor_image.content,
            x = section_position[0] +  + (section_size[0] / (cursor_section.slots[0] + 1) * (self.__cursor_slot_position[0] + 1)),
            y = section_position[1] + (section_size[1] / (cursor_section.slots[1] + 1) * (self.__cursor_slot_position[1] + 1)),
            z = 450.0,
            batch = self.__ui_batch
        )

    def clear_sprites(self) -> None:
        """
        Deletes all temporary sprites.
        """

        # Clear slots sprites.
        for sprite in self.__slots_sprites:
            sprite.delete()
        self.__slots_sprites.clear()

        # Clear cursor.
        if self.__cursor_sprite is not None:
            self.__cursor_sprite.delete()
            self.__cursor_sprite = None

        # Clear sections sprites.
        for section in self.sections:
            section.delete()
        self.sections.clear()

    def toggle(self) -> None:
        """
        Opens or closes the menu based on its current state.
        """

        controllers.MENU_CONTROLLER.toggle()

        if controllers.MENU_CONTROLLER.is_open:
            self.create_sprites()
        else:
            self.clear_sprites()

class InventoryNode(Node):
    __slots__ = (
        "view_width",
        "view_height",
        "world_batch",
        "ui_batch",
        "consumables_area_size",
        "step",
        "ammo_sprites",
        "consumable_slot_image",
        "consumables_slots_sprites",
        "consumables_sprites",
        "quiks_slots_sprites",
        "background",
        "cursor_image",
        "cursor"
    )

    def __init__(
        self,
        view_width: int,
        view_height: int,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> None:
        self.view_width: int = view_width
        self.view_height: int = view_height

        # Batches.
        self.world_batch: pyglet.graphics.Batch | None = world_batch
        self.ui_batch: pyglet.graphics.Batch | None = ui_batch

        self.consumables_area_size: tuple[int, int] = (
            self.view_width // 2,
            self.view_height * 3 // 4
        )
        self.step: tuple[int, int] = (
            self.consumables_area_size[0] // controllers.INVENTORY_CONTROLLER.consumables_size[0],
            self.consumables_area_size[1] // controllers.INVENTORY_CONTROLLER.consumables_size[1]
        )

        self.ammo_sprites: dict[str, SpriteNode] = {}

        # Fetch consumable slot image.
        self.consumable_slot_image: pyglet.image.Texture = pyglet.resource.image("sprites/menus/inventory/consumable_slot.png")
        utils.set_anchor(
            resource = self.consumable_slot_image,
            center = True
        )

        # Consumables sprites.
        self.consumables_slots_sprites: list[SpriteNode] = []
        self.consumables_sprites: dict[str, SpriteNode] = {}

        # Inventory background.
        self.background: SpriteNode | None = None

        # Quiks access sprites.
        self.quiks_slots_sprites: list[SpriteNode] = []

        # Cursor sprite.
        self.cursor_image: Animation = Animation(source = "sprites/menus/inventory/inventory_cursor.json")
        self.cursor: SpriteNode | None = None

        # Create all quiks' slots.
        # Quiks should always be visible, so they're 
        for i in range(controllers.INVENTORY_CONTROLLER.quicks_count):
            self.quiks_slots_sprites.append(SpriteNode(
                resource = self.consumable_slot_image,
                x = (self.view_width // 2) + (i * self.step[0] + self.step[0] // 2),
                y = 10.0,
                z = 550.0,
                batch = self.ui_batch
            ))

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

        # Create all consumables' slots.
        for i in range(controllers.INVENTORY_CONTROLLER.consumables_size[0]):
            for j in range(controllers.INVENTORY_CONTROLLER.consumables_size[1]):
                self.consumables_slots_sprites.append(SpriteNode(
                    resource = self.consumable_slot_image,
                    x = i * self.step[0] + self.step[0] // 2,
                    y = self.view_height - (j * self.step[1] + self.step[1] // 2),
                    # y = self.view_height - consumables_area_size[1] // 2 - (j * step[1] + step[1] // 2),
                    z = 425.0,
                    batch = self.ui_batch
                ))

        # Create cursor.
        self.cursor = SpriteNode(
            resource = self.cursor_image.content,
            x = self.step[0] // 2,
            y = self.view_height - (self.step[1] // 2),
            # y = self.view_height - consumables_area_size[1] // 2 - (step[1] // 2),
            z = 450.0,
            batch = self.ui_batch
        )

        # Create all items' sprites.
        for consumable_position in controllers.INVENTORY_CONTROLLER.consumables_position.items():
            if consumable_position[0] is not None and not consumable_position[0] in self.consumables_sprites:
                # Compute the current 2d index.
                idx2d: tuple[int, int] = utils.idx1to2(consumable_position[1], controllers.INVENTORY_CONTROLLER.consumables_size[1])

                self.consumables_sprites[consumable_position[0]] = SpriteNode(
                    resource = Animation(source = CONSUMABLES_ANIMATION[consumable_position[0]]).content,
                    # TODO Scale and shift correctly.
                    x = idx2d[0] * self.step[0] + self.step[0] // 2,
                    # y = self.view_height - consumables_area_size[1] // 2 - (idx2d[1] * step[1] + step[1] // 2),
                    y = self.view_height - (idx2d[1] * self.step[1] + self.step[1] // 2),
                    z = 500.0,
                    batch = self.ui_batch
                )

    def clear_sprites(self) -> None:
        """
        Deletes all temporary inventory sprites.
        By tempo
        """

        # Clear background.
        if self.background is not None:
            self.background.delete()
            self.background = None

        # Clear consumables slots sprites.
        for sprite in self.consumables_slots_sprites:
            sprite.delete()
        self.consumables_slots_sprites.clear()

        # Clear cursor.
        if self.cursor is not None:
            self.cursor.delete()
            self.cursor = None

        # Clear consumables sprites.
        for sprite in self.consumables_sprites.values():
            sprite.delete()
        self.consumables_sprites.clear()

        # Clear ammo sprites.
        for sprite in self.ammo_sprites.values():
            sprite.delete()
        self.ammo_sprites.clear()

        # # Clear quiks slots sprites.
        # for sprite in self.quiks_slots_sprites:
        #     sprite.delete()
        # self.quiks_slots_sprites.clear()

    def toggle(self) -> None:
        """
        Opens or closes the inventory based on its current state.
        """

        controllers.INVENTORY_CONTROLLER.toggle()

        if controllers.INVENTORY_CONTROLLER.is_open:
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

        if self.cursor is not None:
            self.cursor.update(dt = dt)

        # Use input.
        if inventory_toggled:
            self.toggle()

    def delete(self) -> None:
        self.clear_sprites()

        # Clear quiks slots sprites.
        for sprite in self.quiks_slots_sprites:
            sprite.delete()
        self.quiks_slots_sprites.clear()