from functools import reduce
import json
import os
from typing import Callable

import pyglet
import pyglet.math as pm

from engine import controllers
from engine.node import Node
from engine.scene_node import Bounds
from engine.utils.utils import idx2to1

class SectionOverflow:
    def __init__(
        self,
        top: str,
        bottom: str,
        left: str,
        right: str
    ) -> None:
        self.top: str = top
        self.bottom: str = bottom
        self.left: str = left
        self.right: str = right

    def __str__(self) -> str:
        return f"{{top: {self.top}, bottom: {self.bottom}, left: {self.left}, right: {self.right}}}"

class MenuSection:
    """
    Handles cursor movement and callbacks for a menu section.
    """

    def __init__(
        self,
        name: str,
        slots: tuple[int, int],
        bounds: Bounds,
        overflow: SectionOverflow,
        on_overflow: Callable[[str], None] | None = None
    ) -> None:
        # Section name.
        self.name: str = name

        # Section slots.
        self.slots: tuple[int, int] = slots

        # Graphic bounds in the given viewport.
        self.bounds: Bounds = bounds

        # Overflows.
        self.overflow: SectionOverflow = overflow

        # Callback for handling overflow events.
        self.on_overflow: Callable[[str], None] = on_overflow

        # Current cursor position.
        self.cursor_position: tuple[int, int] = (0, 0)

    def __str__(self) -> str:
        return f"{{name: {self.name}, slots: {self.slots}, bounds: {self.bounds} overflow: {self.overflow}}}"

class MenuController:
    """
    Holds all inventory data and provides accessors to it.
    """

    def __init__(self) -> None:
        # All menu sections by name.
        self.sections: dict[str, MenuSection] = {}

        # Currently active section
        self.current_section: str = ""

        # Cursor movement vector.
        self.cursor_movement: pm.Vec2 = pm.Vec2()

    def __str__(self) -> str:
        return f"sections: \n\t{reduce(lambda a, b: f"{a}{b}", map(lambda section: f"{section}\n\t", self.sections.values()))}"

    def load_file(self, src: str) -> None:
        abs_path: str = os.path.join(pyglet.resource.path[0], src)

        # Just return if the source file is not found.
        if not os.path.exists(abs_path):
            print(f"File does not exist: {abs_path}")
            return

        data: dict

        # Read the source file.
        with open(file = abs_path, mode = "r", encoding = "UTF8") as content:
            data = json.load(content)

        # Just return if no data is read.
        if len(data) <= 0:
            print(f"File is empty: {abs_path}")
            return

        # Just return if the "sections" entry is not found in the source file.
        if not "sections" in data:
            print(f"Error reading file: {abs_path}")
            return

        for section in data["sections"]:
            name: str = section["name"]
            size_str: str = section["slots"]
            bounds_str: str = section["bounds"]
            raw_overflows: dict[str, str] = section["overflows"]

            size: list[int] = size_str.split(",")
            bounds: list[float] = bounds_str.split(",")

            self.sections[name] = MenuSection(
                name = name,
                slots = size,
                bounds = Bounds(
                    left = bounds[0],
                    bottom = bounds[1],
                    right = bounds[2],
                    top = bounds[3]
                ),
                overflow = SectionOverflow(
                    top = raw_overflows["top"],
                    bottom = raw_overflows["bottom"],
                    left = raw_overflows["left"],
                    right = raw_overflows["right"],
                ),
                on_overflow = self.on_overflow
            )

    def on_overflow(self, new_section: str) -> None:
        """
        Handles the current section overflow.
        """

        self.current_section = new_section

    def update(self, dt: float) -> None:
        # Fetch input.
        self.cursor_movement = controllers.INPUT_CONTROLLER.get_aim_vec()

class MenuNode(Node):
    def __init__(
        self,
        view_width: int,
        view_height: int,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__()

        self.view_width: int = view_width
        self.view_height: int = view_height

        # Batches.
        self.world_batch: pyglet.graphics.Batch | None = world_batch
        self.ui_batch: pyglet.graphics.Batch | None = ui_batch

        

class InventoryController:
    """
    Holds all inventory data and provides accessors to it.
    """

    __slots__ = (
        "quicks_count",
        "quicks",
        "current_ammo",
        "ammo",
        "currencies",
        "consumables_size",
        "consumables_position",
        "consumables_count",
        "is_open"
    )

    def __init__(self) -> None:
        # Currently equipped quick-access consumables.
        self.quicks_count: int = 4
        self.quicks: list[str | None] = [None for _ in range(self.quicks_count)]

        # Currently equipped ammo.
        self.current_ammo: str | None = None
        self.ammo: dict[str, int] = {}

        self.currencies: dict[str, int] = {}

        # Amount of available comsumables slots.
        self.consumables_size: tuple[int, int] = (5, 4)

        # List of all consumables' positions.
        self.consumables_position: dict[str, int] = {}

        # Current amount for each consumable.
        self.consumables_count: dict[str, int] = {}

        # Tells whether the inventory is open or not.
        self.is_open: bool = False

    def toggle(self) -> None:
        """
        Toggles the open state of the inventory by opening it if closed and closing it if open.
        """

        self.is_open = not self.is_open

    def __str__(self) -> str:
        return f"quicks_count: {self.quicks_count}\nquicks: {self.quicks}\ncurrent_ammo: {self.current_ammo}\nammo: {self.ammo}\ncurrencies: {self.currencies}\nconsumables_size: {self.consumables_size}\nconsumables_position: {self.consumables_position}\nconsumables_count: {self.consumables_count}\n"

    def equip_consumable(self, consumable: str) -> None:
        """
        Equips [consumable] to a quick slot.
        """

        free_index: int
        try:
            # Get the index of the first empty slot in the list.
            free_index = self.quicks.index(next(filter(lambda quick: quick is None, self.quicks)))
        except ValueError:
            # Just return if no empty spot is found.
            return

        # Set the given consumable to the found empty slot.
        self.quicks[free_index] = consumable

    def load_file(self, source: str) -> None:
        """
        Reads and stores all inventory data from the file provided in [source].
        """

        abs_path: str = os.path.join(pyglet.resource.path[0], source)

        # Just return if the source file is not found.
        if not os.path.exists(abs_path):
            return

        data: dict

        # Load the json file.
        with open(file = abs_path, mode = "r", encoding = "UTF8") as source_file:
            data = json.load(source_file)

        # Just return if no data is read.
        if len(data) <= 0:
            return

        # Read consumables size.
        size_str: str = data["consumables_size"]
        cons_size: list[int] = list(map(lambda item: int(item), size_str.split(",")))
        self.consumables_size = (cons_size[0], cons_size[1])

        # Load quicks.
        self.quicks_count = data["quicks_count"]
        self.quicks = data["quicks"]

        # Load currencies.
        self.currencies.clear()
        for element in data["currencies"]:
            id: str = element["id"]
            count: int = element["count"]
            self.currencies[id] = count

        # Load ammo.
        self.ammo.clear()
        self.current_ammo = data["current_ammo"]
        for element in data["ammo"]:
            id: str = element["id"]
            count: int = element["count"]

            self.ammo[id] = count

        # Load consumables.
        self.consumables_count.clear()
        for element in data["consumables_count"]:
            id: str = element["id"]
            count: int = element["count"]

            self.consumables_count[id] = count

        # Load consumables positions.
        self.consumables_position.clear()
        for element in data["consumables_position"]:
            id: str = element["id"]
            position_str: str = element["position"]
            position: list[int] = list(map(lambda item: int(item), position_str.split(",")))
            self.consumables_position[id] = idx2to1(i = position[0], j = position[1], m = self.consumables_size[0])