from typing import Dict, List
import pyglet.math as pm

from engine.utils import CollisionSweep
from engine.collision.collision_node import CollisionType, CollisionNode

class CollisionController:
    # TODO Swept collisions.
    def __init__(self) -> None:
        self.__colliders: Dict[CollisionType, List[CollisionNode]] = {}

    def add_collider(
        self,
        collider: CollisionNode
    ) -> None:
        if collider.type in self.__colliders:
            self.__colliders[collider.type].append(collider)
        else:
            self.__colliders[collider.type] = [collider]

    def __check_collisions(self) -> None:
        # Only check collision from dynamic to static, since dynamic/dynamic collisions are not needed for now.
        if CollisionType.DYNAMIC in self.__colliders and CollisionType.STATIC in self.__colliders:
            for collider in self.__colliders[CollisionType.DYNAMIC]:
                # TODO Add a broad phase to enhance performance.

                # Save the resulting collisions for the current collider.
                collisions: List[CollisionSweep] = []
                for other in self.__colliders[CollisionType.STATIC]:
                    if collider != other:
                        # Compute collision between colliders.
                        collision_sweep = collider.collide(other)

                        # Only save collision if it actually happened.
                        if collision_sweep.hit is not None and collision_sweep.time < 1.0:
                            collisions.append(collision_sweep)

                # Handling collider movement here allows us to check for all collisions before actually moving.
                # This also allows to perform multiple collision steps if necessary.
                if len(collisions) > 0:
                    # Move to the collision point.
                    collider.set_position((collider.get_position()[0] + collider.velocity_x * collisions[0].time, collider.get_position()[1] + collider.velocity_y * collisions[0].time))

                    # Compute sliding reaction.
                    x_result = (collider.velocity_x * abs(collisions[0].hit.normal.y)) * (1.0 - collisions[0].hit.time)
                    y_result = (collider.velocity_y * abs(collisions[0].hit.normal.x)) * (1.0 - collisions[0].hit.time)
                    collider.set_velocity((x_result, y_result))

                collider.set_position((collider.get_position()[0] + collider.velocity_x, collider.get_position()[1] + collider.velocity_y))
                collider.set_velocity((0.0, 0.0))

    def update(self, _dt) -> None:
        self.__check_collisions()

    def clear(self) -> None:
        self.__colliders.clear()

    def remove_collider(self, collider: CollisionNode):
        """
        Removes the given collider from the list, effectively preventing it from triggering collisions.
        """
        self.__colliders[collider.type].remove(collider)
