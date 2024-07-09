import json
import os

import pyglet

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

    def to_string(self) -> str:
        return f"top: {self.top}, bottom: {self.bottom}, left: {self.left}, right: {self.right}"

class GenInventoryController:
    """
    Holds all inventory data and provides accessors to it.
    """

    def __init__(self) -> None:
        # Sizes by section name.
        self.sizes: dict[str, tuple[int, int]] = {}

        # Overflows by section name.
        self.overflows: dict[str, SectionOverflow] = {}

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

        if not "sections" in data:
            print(f"Error reading file: {abs_path}")
            return

        for section in data["sections"]:
            name: str = section["name"]
            size_str: str = section["size"]
            raw_overflows: dict[str, str] = section["overflows"]

            size: list[int] = size_str.split(",")

            self.sizes[name] = (size[0], size[1])
            self.overflows[name] = SectionOverflow(
                top = raw_overflows["top"],
                bottom = raw_overflows["bottom"],
                left = raw_overflows["left"],
                right = raw_overflows["right"],
            )

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

    def to_string(self) -> str:
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