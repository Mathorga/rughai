import pyglet
from engine.node import PositionNode

class ItemNode:
    __slots__ = (
        "rwo",
        "world_batch",
        "ui_batch"
    )

    def __init__(
        self,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> None:
        self.rwo: PositionNode | None = None
        self.world_batch: pyglet.graphics.Batch | None = world_batch
        self.ui_batch: pyglet.graphics.Batch | None = ui_batch

class TomatoNode(ItemNode):
    def __init__(self) -> None:
        super().__init__()

class CatrootNode(ItemNode):
    def __init__(self) -> None:
        super().__init__()

ITEM_MAPPING: dict[str, type] = {
    "tomato": TomatoNode,
    "catroot": CatrootNode
}

class InventoryNode:
    """
        Holds all inventory data and provides accessors to it.
    """

    __slots__ = (
        "quicks_count",
        "quicks",
        "current_ammo"
        "ammo",
        "currencies",
        "consumables"
    )

    def __init__(self) -> None:
        self.quicks_count: int = 4
        self.quicks: list[ItemNode | None] = [None for _ in range(self.quicks_count)]

        self.current_ammo: str | None = None
        self.ammo: list[ItemNode] = []

        self.currencies: dict[str, int] = {}

        self.consumables: list[ItemNode] = []

    def load_file(self, file_path: str) -> None:
        # TODO Open file and read data from it.
        pass