import json
import os
from typing import Callable

import pyglet

from engine.utils.utils import idx2to1


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
        "consumables_count"
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
        self.consumables_position: dict[str, int] = {
            "bloobary": 12,
            "caroot": 13,
            "hokbary": 14
        }

        # Current amount for each consumable.
        self.consumables_count: dict[str, int] = {}

    def to_string(self) -> str:
        return f"""
            quicks_count: {self.quicks_count}
            quicks: {self.quicks}
            current_ammo: {self.current_ammo}
            ammo: {self.ammo}
            currencies: {self.currencies}
            consumables_size: {self.consumables_size}
            consumables_position: {self.consumables_position}
            consumables_count: {self.consumables_count}
        """

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

        # Read quicks count.
        self.quicks_count = data["quicks_count"]

        # Load currencies.
        self.currencies.clear()
        for element in data["currencies"]:
            id: str = element["id"]
            count: int = element["count"]

            self.currencies[id] = count

        # Load ammo.
        self.ammo.clear()
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