from engine.node import PositionNode

class ItemNode:
    def __init__(self) -> None:
        self.rwo: PositionNode | None = None

class InventoryNode:
    """

    """

    def __init__(self) -> None:
        self.quicks_count: int = 4
        self.quicks: list[ItemNode] = [None for _ in range(self.quicks_count)]

        self.currencies: dict[str, int] = {}

        self.consumables: list[ItemNode] = []
        self.ammo: list[ItemNode] = []