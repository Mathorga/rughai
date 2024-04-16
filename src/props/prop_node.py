import pyglet

from engine.node import PositionNode


class PropNode(PositionNode):
    __slots__ = (
        "id",
        "world_batch",
        "ui_batch"
    )

    def __init__(
        self,
        id: str,
        x: float = 0.0,
        y: float = 0.0,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(x, y)

        self.id = id
        self.world_batch = world_batch
        self.ui_batch = ui_batch