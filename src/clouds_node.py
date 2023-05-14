import random
from typing import Optional
import pyglet

from engine.node import Node
from engine.scene_node import Bounds

from cloud_node import CloudNode
from engine.utils import rect_rect_check

class CloudsNode(Node):
    def __init__(
        self,
        bounds: Bounds,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__()

        self.clouds_num = 25

        self.bounds = bounds

        self.clouds = [
            CloudNode(
                x = bounds.left + random.random() * (bounds.right - bounds.left),
                y = bounds.bottom + random.random() * (bounds.top - bounds.bottom),
                scaling = scaling,
                batch = batch
            ) for _ in range(self.clouds_num)
        ]

    def update(self, dt: int) -> None:
        # Update all clouds.
        for cloud in self.clouds:
            cloud.update(dt)

        # TODO If any cloud is out of bounds, then delete it and create a new one.
        for cloud in self.clouds:
            cloud_bb = cloud.get_bounding_box()
            if not rect_rect_check(*cloud_bb, *self.bounds.get_bounding_box()):
                cloud.set_position(
                    (
                        self.bounds.left - (cloud_bb[2] / 2),
                        self.bounds.bottom + random.random() * (self.bounds.top - self.bounds.bottom),
                    )
                )

    def delete(self) -> None:
        for cloud in self.clouds:
            cloud.delete()

        self.clouds = None