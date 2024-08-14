import random
import pyglet
import pyglet.math as pm

from engine import controllers
from engine.animation import Animation
from engine.cursor_input_handler import CursorInputHandler
from engine.inventory_controller import SECTION_OVERFLOW_NONE, SECTION_OVERFLOW_WRAP, MenuSection
from engine.node import Node
from engine.shapes.rect_node import RectNode
from engine.sprite_node import SpriteNode
from engine.utils import utils
from engine.utils.types import SpriteRes


class MenuNode(Node):
    """
    Generic menu node, holds the structure of a menu from a menu definition file.
    """

    __slots__ = (
        "__x",
        "__y",
        "__width",
        "__height",
        "__world_batch",
        "__ui_batch",
        "sections",
        "__section_slot_res",
        "__slots_sprites",
        # "__slot_image",
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
        x: float,
        y: float,
        width: float,
        height: float,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__()

        self.__x: int = int(x * view_width)
        self.__y: int = int(y * view_height)
        self.__width: int = int(width * view_width)
        self.__height: int = int(height * view_height)

        ################ Batches ################
        self.__world_batch: pyglet.graphics.Batch | None = world_batch
        self.__ui_batch: pyglet.graphics.Batch | None = ui_batch

        self.sections: list[RectNode] = []

        ################ Slots ################
        # Sprite res for section slots.
        self.__section_slot_res: dict[str, SpriteRes] = {}

        # Single slot sprites.
        self.__slots_sprites: list[SpriteNode] = []

        # Fetch a generic slot image.
        # self.__slot_image: pyglet.image.Texture = pyglet.resource.image("sprites/menus/inventory/consumable_slot.png")
        # utils.set_anchor(
        #     resource = self.__slot_image,
        #     center = True
        # )

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

    def set_section_slot_res(self, section: str, sprite_res: SpriteRes) -> None:
        """
        Sets the sprite to use as base slot for the specified section.
        [section] is the name of the section to apply the sprite to.
        [sprite_res] is the sprite resource to apply to the specified section.
        """

        self.__section_slot_res[section] = sprite_res

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
            self.__x + cursor_section.position[0] * self.__width,
            self.__y + cursor_section.position[1] * self.__height
        )
        section_size: tuple[float, float] = (
            cursor_section.size[0] * self.__width,
            cursor_section.size[1] * self.__height
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
            section_position: tuple[float, float] = (
                self.__x + section.position[0] * self.__width,
                self.__y + section.position[1] * self.__height
            )
            section_size: tuple[float, float] = (
                section.size[0] * self.__width,
                section.size[1] * self.__height
            )

            self.sections.append(RectNode(
                x = section_position[0],
                y = section_position[1],
                width = section_size[0],
                height = section_size[1],
                color = (
                    random.randint(0x00, 0xFF),
                    random.randint(0x00, 0xFF),
                    random.randint(0x00, 0xFF),
                    0x7F
                ),
                batch = self.__ui_batch
            ))

            # Make sure a slot image is provided for the current section.
            if section_name not in self.__section_slot_res or self.__section_slot_res[section_name] is None:
                continue

            # Create all slots' sprites.
            for i in range(section.slots[0]):
                for j in range(section.slots[1]):
                    self.__slots_sprites.append(SpriteNode(
                        resource = self.__section_slot_res[section_name],
                        x = section_position[0] + (section_size[0] / (section.slots[0] + 1) * (i + 1)),
                        y = section_position[1] + (section_size[1] / (section.slots[1] + 1) * (j + 1)),
                        z = 425.0,
                        batch = self.__ui_batch
                    ))

        # Fetch current cursor section.
        cursor_section: MenuSection = controllers.MENU_CONTROLLER.sections[self.__cursor_section]
        section_position: tuple[float, float] = (
            self.__x + cursor_section.position[0] * self.__width,
            self.__y + cursor_section.position[1] * self.__height
        )
        section_size: tuple[float, float] = (
            cursor_section.size[0] * self.__width,
            cursor_section.size[1] * self.__height
        )

        # Create cursor sprite.
        self.__cursor_sprite = SpriteNode(
            resource = self.__cursor_image.content,
            x = section_position[0] + (section_size[0] / (cursor_section.slots[0] + 1) * (self.__cursor_slot_position[0] + 1)),
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