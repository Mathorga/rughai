import random
from typing import Optional
import pyglet

from amonite.node import Node
from amonite.scene_node import Bounds
from amonite.utils.utils import rect_rect_check

from cloud_node import CloudNode

class CloudsNode(Node):
    def __init__(
        self,
        bounds: Bounds,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__()

        self.clouds_num = 25

        self.bounds = bounds

        # Create clouds.
        self.clouds: list[CloudNode] = [
            CloudNode(
                x = bounds.left + random.random() * (bounds.right - bounds.left),
                y = bounds.bottom + random.random() * (bounds.top - bounds.bottom),
                batch = batch
            ) for _ in range(self.clouds_num)
        ]

    def update(self, dt: int) -> None:
        for cloud in self.clouds:
            # Update the cloud.
            cloud.update(dt)

            # If a cloud is out of bounds, then move it to the other side of the scene.
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

        self.clouds.clear()