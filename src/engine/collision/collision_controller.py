from typing import Dict, List

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

                collider_position = collider.get_position()
                if len(collisions) > 0:
                    collider.set_position((collider_position[0] + collider.velocity_x * collisions[0].time, collider_position[1] + collider.velocity_y * collisions[0].time))
                else:
                    # Just set the position without taking collisions into consideration.
                    collider.set_position((collider_position[0] + collider.velocity_x, collider_position[1] + collider.velocity_y))

    def update(self, dt) -> None:
        self.__check_collisions()

    def clear(self) -> None:
        self.__colliders.clear()

    def remove_collider(self, collider: CollisionNode):
        """
        Removes the given collider from the list, effectively preventing it from triggering collisions.
        """
        self.__colliders[collider.type].remove(collider)
