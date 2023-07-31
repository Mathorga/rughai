from typing import Tuple

from engine.node import PositionNode


class ShapeNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        color: Tuple[int, int, int, int] = (0x00, 0x00, 0x00, 0xFF)
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.color = color

    def set_color(self, color: Tuple[int, int, int]):
        self.color = color